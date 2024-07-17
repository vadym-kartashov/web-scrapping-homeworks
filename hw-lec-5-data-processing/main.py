import json
import re
from pathlib import Path
from typing import Callable

from sqlalchemy import Column, String, Integer, Text, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

JOB_RECORD_REGEX = re.compile(r'<article id="post-(\d+)".*?<a\s+href="([^"]+)"[^>]*class="jobCard_link".*?<h3\s+class="jobCard_title">([^<]+)</h3>', re.DOTALL)


class JobRecord:

    def __init__(self, job_id: str, job_title: str, href: str):
        self.job_id: str = job_id
        self.job_title: str = job_title
        self.href = href

    def __repr__(self):
        return f"JobRecord(job_id={self.job_id}, job_title={self.job_title}, hrefs={self.href})"


class JobRecordEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, JobRecord):
            return obj.__dict__
        return json.JSONEncoder.default(self, obj)


def extract_job_records(response: str) -> list[JobRecord]:
    response_body = json.loads(response)
    text = response_body['template']
    matches = JOB_RECORD_REGEX.findall(text)
    job_records: list[JobRecord] = []
    for match in matches:
        job_records.append(JobRecord(
            match[0],
            match[2],
            match[1]
        ))
    return job_records


JobRecordsConsumer = Callable[[list[JobRecord]], None]


def generate_database_for_jobs_cache(consumer: JobRecordsConsumer) -> None:
    folder_path = Path('../hw-lec-4-http-requests/cache')
    files: list[Path] = [f for f in folder_path.iterdir() if f.is_file()]

    job_records = []
    for response_file in files:
        content = response_file.read_text('utf-8')
        try:
            job_records += extract_job_records(content)
        except KeyError as e:
            print('Failed to process ' + response_file.as_posix())

    consumer(job_records)


def generate_json_database_for_jobs_cache() -> None:
    def records_to_json_file_consumer(job_records: list[JobRecord]):
        json_db_file_path = Path('job_records.json')
        json_db_file_path.write_text(json.dumps(job_records, cls=JobRecordEncoder, indent=False), encoding='utf-8')

    generate_database_for_jobs_cache(records_to_json_file_consumer)


def generate_sqllite_database_for_jobs_cache() -> None:
    Base = declarative_base()

    class JobRecordEntity(Base):
        __tablename__ = 'job_records'

        id = Column(Integer, primary_key=True, autoincrement=True)
        job_id = Column(String, nullable=True)
        job_title = Column(String, nullable=True)
        href = Column(Text, nullable=True)

        def __init__(self, job_id=None, job_title=None, href=None):
            self.job_id = job_id
            self.job_title = job_title
            self.href = href

        def to_dict(self):
            return {
                'job_id': self.job_id,
                'job_title': self.job_title,
                'href': self.href
            }

        def __repr__(self):
            return f"<JobRecord(job_id={self.job_id}, job_title={self.job_title}, hrefs={self.href})>"

    def sqllite_persisting_record_consumer(job_records: list[JobRecord]):
        def map_record_to_entity(record: JobRecord) -> JobRecordEntity:
            return JobRecordEntity(
                job_id=record.job_id,
                job_title=record.job_title,
                href=record.href
            )

        job_record_entities: list[JobRecordEntity] = [map_record_to_entity(record) for record in job_records]

        db_file_path = 'job_records.db'
        db_path = Path(db_file_path)
        if db_path.exists():
            db_path.unlink()
            print(f"Existing database '{db_file_path}' has been deleted.")
        engine = create_engine(f'sqlite:///{db_file_path}')
        Session = sessionmaker(bind=engine)
        Base.metadata.create_all(engine)
        session = Session()
        try:
            session.add_all(job_record_entities)
            session.commit()
            print("Job records have been saved to the database.")
        except Exception as e:
            print(f"An error occurred while saving job records to the database: {e}")
            session.rollback()
        finally:
            session.close()

    generate_database_for_jobs_cache(sqllite_persisting_record_consumer)


if __name__ == '__main__':
    generate_json_database_for_jobs_cache()
