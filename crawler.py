"""Parser job."""
import csv
import json
from urllib.parse import urljoin

from bs4 import BeautifulSoup

import click

from fake_useragent import UserAgent

import requests

BASE_URL = 'https://rabota.ua/'

UA = UserAgent().chrome
headers = {"User-Agent": UA}


def get_soup(response):
    return BeautifulSoup(response.text, 'lxml')


def get_pages_links(url):
    links = [url]
    response = requests.get(url, headers=headers, timeout=(1, 1))
    soup = get_soup(response)
    tags = soup.find('dl', class_='f-text-royal-blue fd-merchant f-pagination')
    if tags:
        details_tags = tags.find_all('a', class_='f-always-blue')
        for details_tag in details_tags:
            link = urljoin(BASE_URL, details_tag.attrs['href'])
            links.append(link)
    return links


def get_job_links_from_page(page_url):
    response = requests.get(page_url, headers=headers, timeout=(1, 1))
    soup = get_soup(response)
    tags = soup.find_all('a', class_='ga_listing')
    links = [urljoin(BASE_URL, tag.attrs['href']) for tag in tags]
    return links


def get_all_job_links(pages_list):
    links = []
    with click.progressbar(pages_list, label='Process get all job links') as bar:
        for link in bar:
            links += get_job_links_from_page(link)
    return links


def get_ld_json(url: str) -> dict:
    parser = "html.parser"
    req = requests.get(url)
    soup = BeautifulSoup(req.text, parser)
    return json.loads("".join(soup.find("script", {"type": "application/ld+json"}).contents))


def get_jobs(list_jobs_links):
    job_list = []
    with click.progressbar(list_jobs_links, label='Process get all job ') as bar:
        for link in bar:
            json_content = get_ld_json(link)
            job = {
                'link': link,
                'title': json_content[4]['title'],
                'description': json_content[4]['description'],
                'company': json_content[4]['hiringOrganization']['name'],
                # 'work_time': json_content[4]['employmentType'],
                'date_posted': json_content[4]['datePosted']
            }
            job_list.append(job)
        return job_list


@click.command()
@click.argument('vacancy', type=str)
@click.option('-city', type=str, default='киев')
def main(vacancy, city):
    query = "+".join(vacancy.split())
    url = urljoin(BASE_URL, f'/zapros/{query}/{city}')
    pages_links = get_pages_links(url)
    job_links = get_all_job_links(pages_links)
    jobs_list = get_jobs(job_links)

    with open(f'{vacancy}.csv', mode='w') as f:
        writer = csv.DictWriter(f, fieldnames=['link',
                                               'title',
                                               'description',
                                               'company',
                                               # 'work_time',
                                               'date_posted'
                                               ])
        writer.writeheader()
        writer.writerows(jobs_list)


if __name__ == '__main__':
    main()
