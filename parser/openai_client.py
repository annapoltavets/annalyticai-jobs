import os
from textwrap import dedent
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI
from model import ParsedJobDescription


class OpenAIClient:
    def __init__(self):
        load_dotenv()
        self.client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        self.failed = []

    def parse_job_description(
            self,
            job_description_id: str,
            system_prompt: str,
            user_prompt: str
    ) -> Optional[ParsedJobDescription]:
        try:
            resp = self.client.responses.parse(
                model='gpt-4o-mini',
                input=[
                    {"role": "system", "content": dedent(system_prompt)},
                    {"role": "user", "content": dedent(user_prompt)},
                ],
                text_format=ParsedJobDescription,
                # reasoning={"effort": "medium", "summary": "auto"},
                store=False,
            )
            parsed: ParsedJobDescription = resp.output_parsed
            return parsed
        except Exception as e:
            print(f"Validation call failed job_description_id=[{job_description_id}]:", e)
            self.failed.append(job_description_id)
            return None

    def get(
            self,
            job_description_id: str,
            system_prompt: str,
            user_prompt: str,
            model: str = "gpt-5-mini"
    ) -> Optional[dict]:
        try:
            resp = self.client.responses.create(
                model=model,
                input=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_output_tokens=2000,
                store=False,
            )
            # raw text from the model
            output_text = resp.output_text.strip()

            # try parse to JSON
            import json
            return json.loads(output_text)
        except Exception as e:
            print(f"Validation call failed job_description_id=[{job_description_id}]:", e)
            self.failed.append(job_description_id)
            return None

    def get_usage_data(self):
        import os, time, requests, datetime, zoneinfo
        tz = zoneinfo.ZoneInfo("America/New_York")
        now = datetime.datetime.now(tz)
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        start_time = int(start_of_day.timestamp())
        end_time = int(now.timestamp())

        # --- call Usage API (completions) ---
        resp = requests.get(
            "https://api.openai.com/v1/organization/usage/completions",
            headers={"Authorization": f"Bearer {os.environ['OPENAI_ADMIN_API_KEY']}"},
            params={"start_time": start_time, "end_time": end_time, "interval": "1d"},
            timeout=60,
        )
        data = resp.json().get("data", [])

        # Some orgs/projects return a single row for the day; others return multiple lines to roll up.
        in_tok = out_tok = 0
        for row in data:
            m = row['results']
            for r in m:
                in_tok += int(r.get("input_tokens", 0))
                out_tok += int(r.get("output_tokens", 0))

        print(f"Tokens spent: ({in_tok}, {out_tok}) ")
        return in_tok, out_tok



if __name__ == "__main__":
    client = OpenAIClient()
    client.get_usage_data()
