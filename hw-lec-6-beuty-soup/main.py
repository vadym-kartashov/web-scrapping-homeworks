import requests
from bs4 import BeautifulSoup
import json

url = "https://www.bbc.com/sport"

response = requests.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.content, "html.parser")

    articles = soup.find_all('div', type='article', limit=20)

    results = []

    for article in articles:
        ref_element = article.find_next('a')
        link = "https://www.bbc.com" + ref_element.get('href')

        print(f'requesting {link}')
        article_response = requests.get(link)
        article_soup = BeautifulSoup(article_response.content, "html.parser")

        topic_panel = article_soup.find('div', {'data-component': 'topic-list'})
        topic_list = topic_panel.find('ul', {'role':'list'})
        topic_elements = topic_list.find_all('li')

        topics = [topic.text for topic in topic_elements]

        results.append({
            "Link": link,
            "Topics": topics
        })

    with open('news_topics.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

