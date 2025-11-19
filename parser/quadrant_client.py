import os

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client import  models

from datetime import datetime

from dotenv import load_dotenv

QUADRANT_URL="https://bd1f6903-b260-4da4-8d2f-d68b2190b903.us-east-1-1.aws.cloud.qdrant.io:6333"

class JobQdrantClient:

    def __init__(self):
        load_dotenv()

        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        self.qdrant_client = QdrantClient(
            url=QUADRANT_URL,
            api_key=os.environ["QUADRANT_API_KEY"],
        )

    def embed_text(self, text):
        embedding = self.model.encode(text)
        return embedding.tolist()


    def insert_point(self, job):
        if not job['qualifications']:
            print("Skipping job without qualifications:", job['job_id'])
            return

        combined_vector = (self.embed_text(job['job_id']) +
                           self.embed_text(job['job_title']) +
                           self.embed_text(job['employer_name']) +
                           self.embed_text("\n".join(job['qualifications']))
                           )

        if len(combined_vector) < 2000:
            combined_vector.extend([0.0] * (2000 - len(combined_vector)))

        print(len(combined_vector))
        self.qdrant_client.upsert(
            collection_name="rapid_jobs",
            points=[
                models.PointStruct(
                    id=round(datetime.now().timestamp() * 1000),
                    vector=combined_vector,
                    payload={
                        "job_id": job['job_id'],
                        "job_title": job['job_title'],
                        "employer_name": job['employer_name'],
                        "qualifications": job['qualifications']
                    },
                )
            ],
        )

    def insert_points(self, df):
        for index, row in df.iterrows():
            print(row['job_title'])
            self.insert_point(row)

