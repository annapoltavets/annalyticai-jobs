from datetime import datetime

import pandas as pd
from rapidapi_client import RapidApiClient
from similarity import SimilarityService
from utils import load_data, generate_hash, load_dir
from job_parser import JobParser

import os

RAPID_DIR = '../output/1_rapid'
NORM_DIR = '../output/2_normalized'
PARSED_DIR = '../output/3_job_parsed'
FACT_DIR = '../output/4_fact/jobs_fact'

FACT_COLUMNS = ['job_description_id', 'job_title', 'experience_level',
                'required_technical_skills', 'required_languages',
                'required_frameworks', 'required_datastores', 'required_tools',
                'required_cloud', 'job_summary', 'job_id', 'job_title_original',
                'employer_name', 'employer_logo', 'employer_website', 'job_publisher',
                'job_employment_type', 'job_employment_types', 'job_apply_link',
                'job_apply_is_direct', 'apply_options', 'job_is_remote',
                'job_posted_at', 'job_posted_at_timestamp',
                'job_posted_at_datetime_utc', 'job_location', 'job_city', 'job_state',
                'job_country', 'job_latitude', 'job_longitude', 'job_benefits',
                'job_google_link', 'job_salary', 'job_min_salary', 'job_max_salary',
                'job_salary_period', 'job_onet_soc', 'job_onet_job_zone',
                'job_description', 'qualifications', 'responsibilities', 'benefits',
                'category', 'search', 'job_posted_date', 'date_reposted_from']


class Transformer:

    def __init__(self, data_date: str = None):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(current_dir)

        if data_date == None:
            self.data_date = datetime.now().strftime("%Y-%m-%d")
        else:
            self.data_date = data_date
        self.rapid_folder = f"{RAPID_DIR}/{self.data_date}"

        self.fact_df = load_data(FACT_DIR, subset=['job_id'])
        print(f'Fact: {self.fact_df.shape}')
        self.rapid_df = pd.DataFrame()
        self.job_df = pd.DataFrame()
        self.desc_df = pd.DataFrame()

    def etl(self, rapid_extraction: bool = True, period: str = 'week', similarity_threads: int = 1000):
        if rapid_extraction:
            self.extract(period)

        print(f'Start time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')

        (self
         .load_rapid_extraction()
         .incremental_job_id_filter()
         .normalize_job_highlights_json()
         .process_desc_df()
         .process_job_df()
         .save_normalized()
         .update_reposted_date()
         .parse_desc()
         .merge_fact()
         )


        print(f'End time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')

    def extract(self, period: str = 'week'):
        os.makedirs(self.rapid_folder, exist_ok=True)
        rapid = RapidApiClient(date_posted=period, employment_types="FULLTIME,CONTRACTOR",
                               output_folder=self.rapid_folder)
        rapid.fetch_jobs_multithreads()
        return self

    def load_rapid_extraction(self):
        self.rapid_df = load_data(self.rapid_folder, subset=['job_id', 'job_title', 'job_description'])
        self.rapid_df['job_posted_date'] = pd.to_datetime(self.rapid_df['job_posted_at_datetime_utc']).dt.date
        print(f'Rapid extraction read: {self.rapid_df.shape}')
        return self

    def incremental_job_id_filter(self):
        self.rapid_df = self.rapid_df[~self.rapid_df['job_id'].isin(self.fact_df['job_id'])]
        print(f'Job id filtered: {self.rapid_df.shape}')
        return self

    def normalize_job_highlights_json(self):
        self.rapid_df = pd.json_normalize(self.rapid_df.to_dict(orient='records'))
        self.rapid_df.rename(columns={'job_highlights.Qualifications': 'qualifications',
                                      'job_highlights.Responsibilities': 'responsibilities',
                                      'job_highlights.Benefits': 'benefits'}, inplace=True)
        print(f'Json columns normalized: {self.rapid_df.shape}')
        return self

    def process_desc_df(self):
        desc_df = self.rapid_df[['job_id',
                                 'job_description',
                                 'job_title',
                                 'job_posted_date',
                                 'employer_name',
                                 'qualifications',
                                 'responsibilities',
                                 'benefits',
                                 'category',
                                 'search']].copy()

        desc_df['qual_qualifier'] = desc_df['qualifications'].apply(
            lambda x: '; '.join(x) if isinstance(x, list) else '')

        # deduplicate with job_description
        desc_df = (desc_df
                   .sort_values(by=['job_description', 'qual_qualifier'], na_position='last')
                   .drop_duplicates(subset='job_description', keep='first'))
        desc_df.drop(['qual_qualifier'], axis=1, inplace=True)

        # generate job_description_id
        desc_df['job_description_id'] = desc_df['job_description'].apply(generate_hash)
        print(f'Desc selected: {desc_df.shape}')

        self.desc_df = desc_df
        return self

    def find_similar_descriptions(self, threads=1000):
        similarity = SimilarityService(threads=threads)
        similarity.compare_jobs_by_category(self.desc_df, self.fact_df)
        similarity_results = similarity.get_results()
        print(f"Found {len(similarity_results)} similar descriptions")

        if len(similarity_results) > 0:
            sim_df = pd.DataFrame(similarity_results)
            print(f"Found {sim_df.shape[0]} similar descriptions")

            self.desc_df = self.desc_df.merge(sim_df, left_on='job_description_id', right_on='new_job_description_id',
                                              how='left', indicator=True)
            self.desc_df['job_description_id'] = self.desc_df.apply(
                lambda row: row['hist_job_description_id'] if row['_merge'] == 'both' else row['job_description_id'],
                axis=1)
            self.desc_df.drop(['new_job_description_id', 'hist_job_description_id', '_merge'], axis=1, inplace=True)

        print(f'Desc processed: {self.desc_df.shape}')
        return self

    def process_job_df(self):
        df1 = self.rapid_df[['job_id', 'job_title', 'job_posted_date', 'employer_name', 'employer_logo',
                             'employer_website', 'job_publisher', 'job_employment_type',
                             'job_employment_types', 'job_apply_link', 'job_apply_is_direct',
                             'apply_options', 'job_description', 'job_is_remote', 'job_posted_at',
                             'job_posted_at_timestamp', 'job_posted_at_datetime_utc', 'job_location',
                             'job_city', 'job_state', 'job_country', 'job_latitude', 'job_longitude',
                             'job_benefits', 'job_google_link', 'job_salary', 'job_min_salary',
                             'job_max_salary', 'job_salary_period', 'job_onet_soc',
                             'job_onet_job_zone']]
        df1 = df1.merge(self.desc_df[['job_id', 'job_description_id']], on='job_id', how='inner')
        df1.drop_duplicates(subset=['job_id', 'job_description_id'], inplace=True)
        self.job_df = df1
        print(f'Job processed: {self.job_df.shape}')
        return self

    def save_normalized(self):
        output_path = f'{NORM_DIR}/{self.data_date}'
        os.makedirs(output_path, exist_ok=True)
        print(output_path)
        self.desc_df.to_json(f'{output_path}/rapid_desc.json', orient="records", lines=True)
        self.job_df.to_json(f'{output_path}/rapid_jobs.json', orient="records", lines=True)
        return self

    def load_normalized(self):
        self.job_df = pd.read_json(f'{NORM_DIR}/{self.data_date}/rapid_jobs.json', lines=True)

        self.desc_df = pd.read_json(f'{NORM_DIR}/{self.data_date}/rapid_desc.json', lines=True)
        self.desc_df['job_posted_date'] = pd.to_datetime(self.desc_df['job_posted_date'], unit='ms').dt.date
        if 'date_reposted_from' not in self.desc_df.columns:
            self.desc_df['date_reposted_from'] = None
        print(f'Normalized loaded: {self.job_df.shape}, {self.desc_df.shape}')
        self.days = self.desc_df[self.desc_df['date_reposted_from'].isna()]['job_posted_date'].astype(str).unique().tolist()
        print(f'Days: {self.days}')
        return self

    def desc_df_by_date(self, data_date: str = None):
        output_folder = f'{PARSED_DIR}/{str(data_date)}'
        os.makedirs(output_folder, exist_ok=True)
        parsed = load_dir(PARSED_DIR, self.days, subset=['job_description_id'])['job_description_id']
        df = self.desc_df[
            (~self.desc_df['job_description_id'].isin(parsed)) &
            (self.desc_df['date_reposted_from'].isna()) &
            (self.desc_df['job_posted_date'].astype(str) == data_date) &
            (~self.desc_df['job_description_id'].isin(self.fact_df['job_description_id']))
            ].copy()
        df.drop(['job_id'], axis=1, inplace=True)
        df.drop_duplicates(subset=['job_description_id'], inplace=True)
        return output_folder, df

    def update_reposted_date(self):
        for f in self.fact_df['file_name'].unique().tolist():
            df = self.fact_df[self.fact_df['file_name'] == f].copy()
            desc_df = self.desc_df[['job_description_id', 'date_reposted_from']].drop_duplicates(subset=['job_description_id'])
            df = df.merge(desc_df, on=['job_description_id'], how='left', suffixes=('', '_y'))
            df['date_reposted_from'] = df['date_reposted_from'].fillna(df['date_reposted_from_y'])
            df = df[FACT_COLUMNS]
            df.to_json(f'{FACT_DIR}/{f}', orient="records", lines=True)
            print(f'Updated {FACT_DIR}/{f}')
        return self

    def parse_desc(self, limit: int = 2_300_000):
        self.days = self.desc_df[self.desc_df['date_reposted_from'].isna()]['job_posted_date'].astype(str).unique().tolist()
        print(f'Days to process: {self.days}')

        for day in self.days:
            output_folder, df = self.desc_df_by_date(day)
            print(f'Parse {day} with {df.shape[0]} rows')
            parser = JobParser()
            parser.run_parser(output_folder, df, max_workers=5, chunk_size=50, limit=5000)
            i, o = parser.client.get_usage_data()
            if (i + o > limit):
                print(f"Reached daily limit ({i}, {o}), stopping further processing.")
                break
        return self

    def merge_fact(self):
        parsed_df = load_dir(PARSED_DIR, self.days, subset=['job_description_id'])
        print(f'Merging parsed {parsed_df.shape}')

        ddf = self.desc_df.drop_duplicates('job_description_id')
        jdf = self.job_df.drop_duplicates('job_id')

        merged_df = parsed_df.merge(ddf, on=['job_description_id'], how='inner', suffixes=('', '_original'))
        merged_df = merged_df.merge(jdf, on=['job_id'], how='inner', suffixes=('', '_y'))
        merged_df = merged_df[FACT_COLUMNS]
        #merged_df = merged_df[~merged_df['job_id'].isin(self.fact_df['job_id'])]
        #merged_df = merged_df[~merged_df['job_description_id'].isin(self.fact_df['job_description_id'])]
        print(f'Merged fact {merged_df.shape}')

        merged_df.to_json(f'{FACT_DIR}/{self.data_date}_jobs.json', orient="records", lines=True)

        return self


if __name__ == "__main__":
    t = Transformer('2025-11-18')
    t.etl(period='3days')
