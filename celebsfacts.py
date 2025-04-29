from _Proxies import ProxiesCrawler
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import requests
import random
import json
import time
import re

main_url = "https://www.celebsfacts.com/sitemap-1.xml"


# This function will get all urls and return list of all urls of details pages using "sitemap"
def get_celibrity_urls(url, Proxies):
    celeb_urls = []
    try:
        ua = UserAgent()
        headers = {
            'User-Agent': ua.random
        }
        RandomProxy = random.choice(Proxies)
        response = requests.get(url, proxies={RandomProxy[1]:RandomProxy[0]}, headers=headers)
        # print('status code:',response.status_code)
        soup = BeautifulSoup(response.content, 'lxml-xml')
        # Find all <loc> tags (they contain URLs)
        urls = [loc.text for loc in soup.find_all('loc')][1:]
        for u in urls:
            celeb_urls.append(u)
        
        return celeb_urls

    except Exception as error:
        print("Error: in get_celibrity_urls()", error)
        return celeb_urls
    

def get_celeb_details(url, Proxies):
    try:
        ua = UserAgent()
        headers = {
            'User-Agent': ua.random
        }
        RandomProxy = random.choice(Proxies)
        response = requests.get(url, proxies={RandomProxy[1]:RandomProxy[0]}, headers=headers)

        soup = BeautifulSoup(response.text, 'html.parser')

        # find category
        cat_name = ""
        cat_div = soup.find('div', attrs={'class':'entry-categories'}).get_text().strip()
        cat_name = cat_div
        if "," in cat_div:
            cat_name = cat_div.split(',')[0].strip()
        
        # find main div
        main_div = soup.find('div', attrs={'class':'entry-content'})

        # find description
        description = ""
        all_p = main_div.find_all('p')
        if all_p:
            description = all_p[0].get_text().strip()


        # find image
        image = ""
        img_div = main_div.find('div', id=re.compile(r'^attachment_\d+$'))
        image = img_div.find('img').get('src')

        name = ""
        born_date = ""
        occupation = ""
        nationality = ""
        religion = ""

        # find paragraph data
        p_data = img_div.find_next_sibling('p')
        p_lines = p_data.decode_contents().split('<br/>')
        for p in p_lines[1:]:
            p = p.strip()

            # find date of birth
            if p.startswith("Date Of Birth:"):
                born_date = p.replace("Date Of Birth:","").strip()
            # find name
            if p.startswith("Birth Name:"):
                name = p.replace("Birth Name:","").strip()
            # find occupation
            if p.startswith("Occupation:"):
                occupation = p.replace("Occupation:","").strip()
            # find Nationality
            if p.startswith("Nationality:"):
                nationality = p.replace("Nationality:","").strip()
            # find Religion
            if p.startswith("Religion:"):
                religion = p.replace("Religion:","").strip()

        obj = {
            "category": f"{cat_name}",
            "name": f"{name}",
            "image": f"{image}",
            "nationality": f"{nationality}",
            "religion": f"{religion}",
            "description": f"{description}",
            "generalInformation": [
            { "name": "Born", "value": f"{born_date}" },
            { "name": "Died", "value": "" },
            { "name": "Occupation", "value": f"{occupation}" },
            { "name": "Famous For", "value": "" }
            ]
        }
        # add data in jsonl file
        with open("json_data/data.jsonl", "a", encoding="utf-8") as file:
            json.dump(obj, file, ensure_ascii=False)
            file.write("\n")
        print("Successfully Added data in jsonl file")


    except Exception as error:
        print("Error: in get_celeb_details()", error)


if __name__ == "__main__":
    ALL_PROXIES = ProxiesCrawler().get_proxies(0,10)
    celeb_urls = get_celibrity_urls(main_url, ALL_PROXIES)
    if celeb_urls:
        print('Total urls are:', len(celeb_urls))
        # loop over each url
        for index, url in enumerate(celeb_urls, start=1):
            print("-"*10, f"Scraping page-{index}", "-"*10)
            # Get details and save in jsonl file
            time.sleep(2)
            get_celeb_details(url, ALL_PROXIES)