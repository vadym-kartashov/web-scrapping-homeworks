import hashlib
import json
import re
import requests

JOB_TITLE_REGEX = re.compile(r'<h3 class=\\"jobCard_title\\">(.*?)<\\/h3>')
BASE_URL = 'https://www.lejobadequat.com/emplois'


def load_json_file(file_path: str) -> dict:
    with open(file_path, 'r') as file:
        return json.load(file)


def make_request(paged_value: int, headers: dict, data_template: dict) -> str:
    data_template["data"]["load_more"] = [paged_value]
    data_template["data"]["paged"] = paged_value
    return post_content(BASE_URL, headers, data_template, paged_value)


def post_content(url: str, headers: dict, json: dict, id: int) -> str:
    cache_key = f"{url}{id}"
    filename = hashlib.md5(cache_key.encode('utf-8')).hexdigest()
    filename = f'cache/{filename}'

    try:
        with open(filename, 'r') as file:
            content = file.read()
            print('Retrieved from cache')
            return content
    except FileNotFoundError:
        response = requests.post(url, headers=headers, json=json)
        with open(filename, 'w') as file:
            file.write(response.text)
        print('Retrieved from server')
        return response.text


def extract_job_titles(response: str) -> list[str]:
    encoded_job_titles = JOB_TITLE_REGEX.findall(response)
    return [
        title.encode('utf-8').decode('unicode-escape').replace('&#8211;', '–').replace('H\/F', 'H/F')
        for title in encoded_job_titles
    ]


if __name__ == '__main__':
    headers = load_json_file('headers.json')
    data_template = load_json_file('data_template.json')

    page = 0
    job_titles = extract_job_titles(make_request(page, headers, data_template))

    while job_titles:
        print(f'### Printing page {page}')
        for job_title in job_titles:
            print(job_title)
        page += 1
        job_titles = extract_job_titles(make_request(page, headers, data_template))
