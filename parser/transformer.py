import pandas as pd
from rapidapi_client import RapidApiClient
from utils import load_data, generate_hash

import os

NORMALIZED = '../output/2_normalized'
FACT_DIR = '../output/4_fact/fact_jobs'
SRC_DIR = '../output/1_rapid'
class Transformer:

    def __init__(self, suffix: str):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(current_dir)

        self.suffix = suffix
        self.__df = pd.DataFrame()
        self.job_df = pd.DataFrame()
        self.desc_df = pd.DataFrame()

    def extract(self, period: str = 'week'):
        rapid = RapidApiClient(date_posted=period, employment_types="FULLTIME,CONTRACTOR")
        rapid.fetch_jobs_multithreads()
        self.rapid_folder = rapid.output_folder
        self.rapid_subfolder = rapid.subfolder

    def transform_load(self):
        folder_path = f'{SRC_DIR}/{self.suffix}'
        #folder_path = self.rapid_folder
        self.__df = load_data(folder_path, subset=['job_id', 'job_title', 'job_description'])
        self.incremental_load_job_id_filter()
        print(self.__df.shape)
        print(self.__df.columns)
        self.normalize_json()
        self.desc_df = self.process_job_description()
        self.job_df = self.process_job()
        self.save_desc()
        self.save_jobs()

    def load(self):
        self.job_df = pd.read_json(f'{NORMALIZED}/{self.suffix}/rapid_job_{self.suffix}.json', lines=True)
        self.desc_df = pd.read_json(f'{NORMALIZED}/{self.suffix}/rapid_desc_{self.suffix}.json', lines=True)

    def incremental_load_job_id_filter(self):
        fact = load_data(FACT_DIR, subset=['job_id'])['job_id']
        self.__df = self.__df[~self.__df['job_id'].isin(fact)]

    def normalize_json(self):
        print("Normalizing job_highlights...")
        self.__df = pd.json_normalize(self.__df.to_dict(orient='records'))
        self.__df.rename(columns={'job_highlights.Qualifications': 'qualifications', 'job_highlights.Responsibilities': 'responsibilities', 'job_highlights.Benefits': 'benefits'}, inplace=True)
        return self

    def process_job_description(self):
        desc_df = self.__df[['job_description', 
                             'job_title', 
                             'qualifications', 
                             'responsibilities', 
                             'benefits', 
                             'category', 
                             'search']].copy()
        desc_df['qq'] = desc_df['qualifications'].apply(lambda x: ', '.join(x) if isinstance(x, list) else '')
        desc_df = (desc_df.sort_values(by=['job_description', 'qq'], na_position='last')
                   .drop_duplicates(subset='job_description', keep='first'))
        desc_df.drop(['qq'], axis=1, inplace=True)
        desc_df['job_description_id'] = desc_df['job_description'].apply(generate_hash)

        print(desc_df.shape)
        return desc_df

    def process_job(self):
        df1 = self.__df[['job_id', 'job_title', 'employer_name', 'employer_logo',
                   'employer_website', 'job_publisher', 'job_employment_type',
                   'job_employment_types', 'job_apply_link', 'job_apply_is_direct',
                   'apply_options', 'job_description', 'job_is_remote', 'job_posted_at',
                   'job_posted_at_timestamp', 'job_posted_at_datetime_utc', 'job_location',
                   'job_city', 'job_state', 'job_country', 'job_latitude', 'job_longitude',
                   'job_benefits', 'job_google_link', 'job_salary', 'job_min_salary',
                   'job_max_salary', 'job_salary_period', 'job_onet_soc',
                   'job_onet_job_zone']]
        df1 = df1.merge(self.desc_df[['job_description', 'job_description_id']], on='job_description', how='left')
        df1.drop(['job_description'], axis=1, inplace=True)
        df1.drop_duplicates(subset=['job_id', 'job_description_id'], inplace=True)
        print(df1.shape)
        return df1

    def save_jobs(self):
        output_path = f'{NORMALIZED}/{self.suffix}/rapid_job_{self.suffix}.json'
        print(output_path)
        self.job_df.to_json(output_path, orient="records", lines=True)

    def save_desc(self):
        output_path = f'{NORMALIZED}/{self.suffix}/rapid_desc_{self.suffix}.json'
        print(output_path)
        self.desc_df.to_json(output_path, orient="records", lines=True)


if __name__ == "__main__":
    t = Transformer('2025-09-26')
    #t.transform_load()
    t.load()
    df = pd.read_json('/Users/apoltavets/anna-apps/annalyticai/labor-market/output/2_normalized/20250922-0058/rapid_desc_20250922-0058.json')
    desc = t.desc_df[t.desc_df['job_description'].isin(df['job_description'])]
    print(desc.shape)