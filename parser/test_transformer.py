import shutil
import unittest
from unittest.mock import patch, MagicMock
from utils import load_dir, load_data
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..parser')))
import transformer_v2 as tr

DATA_DATE = '2025-08-01'
tr.RAPID_DIR = '../output/1_rapid/test'
tr.NORM_DIR = '../output/2_normalized/test'
tr.PARSED_DIR = '../output/3_job_parsed/test'
tr.FACT_DIR = '../output/4_fact/test'


class TestTransformer(unittest.TestCase):

    def test_init_and_load_rapid_extraction(self, ):
        transformer = tr.Transformer(data_date=DATA_DATE)
        transformer.load_rapid_extraction()

        self.assertEqual(transformer.data_date, DATA_DATE)
        self.assertEqual(transformer.rapid_df.shape, (18, 35))
        self.assertEqual(transformer.fact_df.shape, (3, 48))
        self.assertTrue(transformer.job_df.empty)
        self.assertTrue(transformer.desc_df.empty)

    def test_incremental_job_id_filter(self):
        transformer = tr.Transformer(data_date=DATA_DATE)
        transformer.load_rapid_extraction().incremental_job_id_filter()
        print(transformer.rapid_df['job_id'].tolist())
        self.assertEqual(transformer.rapid_df.shape, (17, 35))
        self.assertEqual(sorted(transformer.rapid_df['job_id'].tolist())
                         , ['10', '11', '12', '13', '14', '15', '16', '17', '2', '3', '4', '5', '6', '7', '8', '9', '_1'])

    def test_normalize_job_highlights_json(self):
        transformer = tr.Transformer(data_date=DATA_DATE)
        transformer.load_rapid_extraction().incremental_job_id_filter().normalize_job_highlights_json()
        self.assertEqual(transformer.rapid_df.shape, (17, 37))

        print(transformer.rapid_df.columns)
        self.assertTrue('qualifications' in transformer.rapid_df.columns)
        self.assertTrue('responsibilities' in transformer.rapid_df.columns)
        self.assertTrue('benefits' in transformer.rapid_df.columns)

    def test_process_desc_df(self):
        transformer = tr.Transformer(data_date=DATA_DATE)
        (transformer.load_rapid_extraction().incremental_job_id_filter()
         .normalize_job_highlights_json()
         .process_desc_df())
        print(transformer.desc_df['job_id'].tolist())

        self.assertEqual(transformer.desc_df.shape, (15, 11))
        desc = transformer.desc_df.drop_duplicates('job_description')
        self.assertEqual(desc.shape, (15, 11))
        self.assertEqual(sorted(transformer.desc_df['job_id'].tolist())
                         , ['10', '11', '13', '14', '15', '16', '2', '3', '4', '5', '6', '7', '8', '9', '_1'])

    def test_find_similar_descriptions(self):
        transformer = tr.Transformer(data_date=DATA_DATE)
        (transformer.load_rapid_extraction().incremental_job_id_filter()
         .normalize_job_highlights_json()
         .process_desc_df()
         .find_similar_descriptions(1))
        print(transformer.desc_df['job_id'].tolist())
        desc_ids = transformer.desc_df['job_description_id'].tolist()
        print(desc_ids)
        print(transformer.desc_df[['job_id', 'job_description_id', 'date_reposted_from']])

        self.assertEqual(transformer.desc_df.shape, (15, 13))
        self.assertTrue("_300" in desc_ids)
        self.assertTrue('date_reposted_from' in transformer.desc_df.columns)

    def test_process_job_df(self):
        transformer = tr.Transformer(data_date=DATA_DATE)
        (transformer.load_rapid_extraction().incremental_job_id_filter()
         .normalize_job_highlights_json()
         .process_desc_df()
         .find_similar_descriptions(1)
         .process_job_df())

        ids = transformer.job_df['job_id'].tolist()
        print(ids)

        self.assertEqual(transformer.job_df.shape, (15, 32))
        self.assertEqual(sorted(transformer.desc_df['job_id'].tolist())
                         , ['10', '11', '13', '14', '15', '16', '2', '3', '4', '5', '6', '7', '8', '9', '_1'])

    def test_save_normalized(self):
        transformer = tr.Transformer(data_date=DATA_DATE)
        (transformer.load_rapid_extraction()
         .incremental_job_id_filter()
         .normalize_job_highlights_json()
         .process_desc_df()
         .find_similar_descriptions(1)
         .process_job_df()
         .save_normalized())
        self.assertTrue(os.path.exists(f'{tr.NORM_DIR}/{DATA_DATE}/rapid_desc.json'))
        self.assertTrue(os.path.exists(f'{tr.NORM_DIR}/{DATA_DATE}/rapid_jobs.json'))

    def test_desc_df_by_date(self):
        transformer = tr.Transformer(data_date=DATA_DATE)
        (transformer.load_normalized())
        df = transformer.desc_df
        print(df['job_posted_date'].astype(str).value_counts())
        print(df[['job_id', 'job_posted_date']])

        out_dir, desc_by_date_df = transformer.desc_df_by_date('2025-09-23')
        self.assertEqual(desc_by_date_df.shape[0], 6)
        out_dir, desc_by_date_df = transformer.desc_df_by_date('2025-09-24')
        self.assertEqual(desc_by_date_df.shape[0], 1)
        out_dir, desc_by_date_df = transformer.desc_df_by_date('2025-09-25')
        self.assertEqual(desc_by_date_df.shape[0], 2)
        out_dir, desc_by_date_df = transformer.desc_df_by_date('2025-09-26')
        self.assertEqual(desc_by_date_df.shape[0], 1)
        out_dir, desc_by_date_df = transformer.desc_df_by_date('2025-09-27')
        self.assertEqual(desc_by_date_df.shape[0], 2)
        out_dir, desc_by_date_df = transformer.desc_df_by_date('2025-09-28')
        self.assertEqual(desc_by_date_df.shape[0], 2)

    def test_update_reposted_date(self):
        transformer = tr.Transformer(data_date=DATA_DATE)
        transformer.load_normalized().update_reposted_date()
        fact = load_data(tr.FACT_DIR, subset=['job_description_id'])
        reposted = fact[fact['job_description_id'] == "_300"]['date_reposted_from'].tolist()[0]

        self.assertEqual(reposted, 1756425600000)

    def test_merge_fact(self):
        transformer = tr.Transformer(data_date=DATA_DATE)
        transformer.load_normalized()
        self.assertEqual(transformer.job_df.shape[0], 15)
        self.assertEqual(transformer.desc_df.shape[0], 15)

        transformer.merge_fact()

        df = load_dir(tr.PARSED_DIR, subset=['job_description_id'])
        self.assertEqual(df.shape[0], 14)

        transformer = tr.Transformer(data_date=DATA_DATE)
        self.assertEqual(transformer.fact_df.shape, (16, 48))
        os.remove(f'{tr.FACT_DIR}/{DATA_DATE}_jobs.json')


if __name__ == '__main__':
    unittest.main()
