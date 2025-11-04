from datetime import datetime

import pandas as pd
from fuzzywuzzy import fuzz
from concurrent.futures import as_completed
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from spec import SearchCategory

CATEGORY_GROUPS = [
    [SearchCategory.MANAGEMENT.value],
    [SearchCategory.LEAD.value, SearchCategory.AI_ML.value, SearchCategory.BACKEND.value, SearchCategory.DATA.value, SearchCategory.DEVOPS.value, SearchCategory.ENGINEER.value, SearchCategory.FRONTEND.value],
    [SearchCategory.UI_UX_DESIGN.value],
    [SearchCategory.CYBERSECURITY.value],
    [SearchCategory.GAMES_DEVELOPMENT.value],
    [SearchCategory.HARDWARE.value],
    [SearchCategory.MOBILE.value],
    [SearchCategory.BUSINESS_ANALYSIS.value],
    [SearchCategory.QA.value]
]

class SimilarityService:

    def __init__(self, threads: int = 1000):
        self.threads = threads
        self.thread_safe_list = Queue()

    def compare_jobs(self, new_description_id: str, new_description: str, new_employer_name: str,
                     hist_dict_by_category: dict, start_pointer: int = 0):
        for j in range(start_pointer, len(hist_dict_by_category)):
            desc_score = fuzz.token_set_ratio(new_description, hist_dict_by_category[j]['job_description'])
            if desc_score > 96 or (desc_score > 90 and new_employer_name == hist_dict_by_category[j]['employer_name']):
                print(f"Match found: New ID {new_description_id} with Hist ID {hist_dict_by_category[j]['job_description_id']} | Score: {desc_score}")
                self.thread_safe_list.put({
                    'new_job_description_id': new_description_id,
                    'hist_job_description_id': hist_dict_by_category[j]['job_description_id'],
                    'date_reposted_from': hist_dict_by_category[j]['job_posted_date'],
                    'desc_score': desc_score,
                })

    def compare_jobs_by_category(self, new_desc_df: pd.DataFrame, fact: pd.DataFrame):
        with ThreadPoolExecutor(self.threads) as executor:
            futures = []
            for member in CATEGORY_GROUPS:
                new_dict = (new_desc_df[new_desc_df['category'].isin(member)]
                            .drop_duplicates(subset='job_description_id')
                            .sort_values(by='job_description_id')
                            [['job_description_id', 'job_description', 'employer_name', 'job_posted_date']]
                            .to_dict('records')
                            )

                hist_dict = (fact[fact['category'].isin(member)]
                             .drop_duplicates(subset='job_description_id')
                             .sort_values(by='job_description_id')
                             [['job_description_id', 'job_description', 'employer_name', 'job_posted_date']]
                             .to_dict('records')
                             )
                print(f'Compare Category: {member}, New: {len(new_dict)}, Hist: {len(hist_dict)}, Start time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
                for n in new_dict:
                    futures.append(executor.submit(self.compare_jobs, n['job_description_id'], n['job_description'], n['employer_name'], hist_dict))

            for future in as_completed(futures):  # Use concurrent.futures.as_completed
                try:
                    future.result()  # Ensure the future has completed
                except Exception as e:
                    print(f"Error in thread: {e}")

    def get_results(self):
        results = []
        while not self.thread_safe_list.empty():
            results.append(self.thread_safe_list.get())
        return results


if __name__ == "__main__":
    import pandas as pd

    # Mock data for new_desc_df
    new_desc_df = pd.DataFrame({
        'job_description_id': ['new_1', 'new_2'],
        'job_description': ['Software Engineer', 'Data Scientist role'],
        'employer_name': ['Company A', 'Company B'],
        'job_posted_date': ['2023-10-01', '2023-10-02'],
        'category': ['data', 'data']
    })

    # Mock data for fact
    fact = pd.DataFrame({
        'job_description_id': ['hist_1', 'hist_2'],
        'job_description': ['Software Engineer', 'Data Scientist position'],
        'employer_name': ['Company A', 'Company C'],
        'job_posted_date': ['2023-09-25', '2023-09-26'],
        'category': ['data', 'data']
    })

    # Convert job_posted_date to datetime
    new_desc_df['job_posted_date'] = pd.to_datetime(new_desc_df['job_posted_date'])
    fact['job_posted_date'] = pd.to_datetime(fact['job_posted_date'])

    print(new_desc_df)
    print(fact)

    service = SimilarityService()
    service.compare_jobs('1', 'Software Engineer', 'Company A', fact.to_dict('records'))
    for q in range(service.thread_safe_list.qsize()):
        print(service.thread_safe_list.get())

    service.compare_jobs_by_category(new_desc_df, fact)
    for q in range(service.thread_safe_list.qsize()):
        print(service.thread_safe_list.get())