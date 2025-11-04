import logging
import os
import time
from concurrent.futures import as_completed
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from spec import SPEC


import requests
import pandas as pd

class RapidApiClient:

    def __init__(self, search_map=None, date_posted="month", employment_types="FULLTIME", output_folder="../output/1_rapid"):
        load_dotenv()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(current_dir)
        self.logger = logging.getLogger(__name__)

        self.num = 1
        self.calls_num = 0
        self.records_count = {}
        if search_map != None:
            self.search_map = search_map
        else:
            self.search_map = {}
            for k, v in SPEC.items():
                self.search_map[k] = v['search']
        self.date_posted = date_posted
        self.employment_types = employment_types
        self.output_folder = f"{output_folder}"

        print("Search prescription: \n" + ",".join(self.search_map.keys()))


    def fetch_jobs(self, num_pages=50, page_limit=30):
        for key in self.search_map.keys():
            for search in self.search_map[key]:
                print(f"{key} - {search}")
                search_dfs = []
                for i in range(1, page_limit + 1):
                    url = "https://jsearch.p.rapidapi.com/search"
                    querystring = {"query": search.lower(), "page": str(i), "num_pages": str(num_pages), "country": "us",
                                   "date_posted":self.date_posted,"employment_types":self.employment_types}
                    headers = {
                        "x-rapidapi-key": os.environ["RAPID_API_KEY"],
                        "x-rapidapi-host": "jsearch.p.rapidapi.com"
                    }
                    self.calls_num += 1
                    try:
                        response = requests.get(url, headers=headers, params=querystring)
                        data = response.json()['data']
                        print(f"fetch {i}: {len(data)}")
                        if len(data) == 0:
                            break

                        x2 = pd.DataFrame(data)
                        x2['category'] = key
                        x2['search'] = search
                        search_dfs.append(x2)
                    except Exception as e:
                        print(f"Error fetching page {i} for {key}( {search}): {e}")
                        break

                filename = f'{key}_{search}'.lower().replace(' ', '_').replace('/', '_').replace('.', '_')
                output_path = f"{self.output_folder}/{self.num}_{filename}.json"

                x1 = pd.concat(search_dfs).drop_duplicates(subset='job_id')
                x1.to_json(output_path, orient='records', lines=True)

                self.records_count[key] = len(x1)

                print(x1.shape)
                self.num += 1

    from concurrent.futures import ThreadPoolExecutor, as_completed

    def fetch_search_by_category(self, category: str, num_pages: int = 50, page_limit: int = 30):
        for search in self.search_map[category]:
            print(f"{category} - {search}")
            search_dfs = []
            for i in range(1, page_limit + 1):
                url = "https://jsearch.p.rapidapi.com/search"
                querystring = {"query": search.lower(), "page": str(i), "num_pages": str(num_pages), "country": "us",
                               "date_posted": self.date_posted, "employment_types": self.employment_types}
                headers = {
                    "x-rapidapi-key": os.environ["RAPID_API_KEY"],
                    "x-rapidapi-host": "jsearch.p.rapidapi.com"
                }
                self.calls_num += 1
                try:
                    response = requests.get(url, headers=headers, params=querystring)
                    data = response.json()['data']
                    if len(data) == 0:
                        break

                    x2 = pd.DataFrame(data)
                    x2['category'] = category
                    x2['search'] = search
                    search_dfs.append(x2)
                except Exception as e:
                    print(f"Error fetching page {i} for {category} ({search}): {e}")
                    i -= 1

            filename = f'{category}_{search}'.lower().replace(' ', '_').replace('/', '_').replace('.', '_')
            output_path = f"{self.output_folder}/{self.num}_{filename}.json"
            print(f"Saving to {output_path}")

            x1 = pd.concat(search_dfs).drop_duplicates(subset='job_id')
            x1.to_json(output_path, orient='records', lines=True)

            self.records_count[category] = len(x1)

            print(x1.shape)
            self.num += 1

    def fetch_jobs_multithreads(self):
        with ThreadPoolExecutor() as executor:
            futures = []
            for key in self.search_map.keys():
                    futures.append(executor.submit(self.fetch_search_by_category, key))
                    time.sleep(3)

            for future in as_completed(futures):
                try:
                    future.result()  # Raise exceptions if any occurred in threads
                except Exception as e:
                    print(f"Error in thread: {e}")


def unit_test():
    test_map = {'test': ['vibe coder']}
    r = RapidApiClient(test_map)
    r.fetch_jobs(1, 1)
    print(f"Total API calls: {r.calls_num}")

if __name__ == "__main__":
    #RapidApiClient(date_posted="week", employment_types="FULLTIME,CONTRACTOR").fetch_search_by_category('qa')
    RapidApiClient(date_posted="week", employment_types="FULLTIME,CONTRACTOR").fetch_jobs_multithreads()