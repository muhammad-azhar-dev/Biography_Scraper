from _Proxies import ProxiesCrawler
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import requests
import random
import json
import time

main_url = "https://www.thefamouspeople.com"

def get_categories(url, Proxies):
    cat_names = []
    cat_urls = []
    try:
        ua = UserAgent()
        headers = {
            'User-Agent': ua.random
        }
        RandomProxy = random.choice(Proxies)
        response = requests.get(url, proxies={RandomProxy[1]:RandomProxy[0]}, headers=headers, timeout=60)
        print('status:', response.status_code)

        soup = BeautifulSoup(response.text, 'html.parser')

        cat_div = soup.find_all('div', attrs={'class':'catitems'})
        if cat_div:
            main_div = cat_div[-1]
            for div in main_div.find_all('div', attrs={'class':'col-md-6'}):
                # get url
                url_data = div.find('a', recursive=False).get('href')
                cat_url = f"https:{url_data}"
                # recursive False will only in children not in nested children
                # get name
                cat_name = div.find('p', attrs={'class':'profile-block'}).get_text().strip()

                # append data in their list
                cat_names.append(cat_name)
                cat_urls.append(cat_url)

        return cat_names, cat_urls
                
        
    except Exception as error:
        print("Error: in get_categories", error)
        return cat_names, cat_urls
    

def get_persons(url, Proxies):
    person_urls = []
    person_names = []
    try:
        ua = UserAgent()
        headers = {
            'User-Agent': ua.random
        }
        RandomProxy = random.choice(Proxies)
        response = requests.get(url, proxies={RandomProxy[1]:RandomProxy[0]}, headers=headers, timeout=60)
        time.sleep(2)
        print('status:', response.status_code)

        soup = BeautifulSoup(response.text, 'html.parser')

        main_div = soup.find('div', attrs={'id':'main-mp-content'})
        if main_div:
            all_titles = main_div.find_all('div', attrs={'class':'ptitle-internal'})
            if all_titles:
                for div in all_titles:
                    a_tag = div.find('a')
                    if a_tag:
                        # get name
                        person_name = a_tag.get_text().strip()
                        # get url
                        url_data = a_tag.get('href')
                        person_url = f"https:{url_data}"

                        # add data in their list
                        person_names.append(person_name)
                        person_urls.append(person_url)

        return person_names, person_urls

    except Exception as error:
        print("Error: in get_persons()", error)
        return person_names, person_urls
    

def save_details(url, cat_name, person_name, Proxies):
    try:
        ua = UserAgent()
        headers = {
            'User-Agent': ua.random
        }
        RandomProxy = random.choice(Proxies)
        response = requests.get(url, proxies={RandomProxy[1]:RandomProxy[0]}, headers=headers, timeout=60)
        print('status:', response.status_code)
        
        soup = BeautifulSoup(response.text, 'html.parser')

        # find description
        description = ""
        desc_data = soup.find('div', attrs={'class':'main_introduction_right'})
        if desc_data:
            description = desc_data.get_text().strip()

        # find image
        image = ""
        img = soup.find('a', attrs={'class':'fancybox-effects-a'})
        if img:
            img_data = img.get('href')
            image = f"https:{img_data}"
        
        # find born date, died date
        born_date = ""
        died_date = ""
        title_spans = soup.find_all('span', attrs={'class':'quickfactstitle'})
        if title_spans:
            # find born date
            for span in title_spans:
                data = span.get_text().strip()
                # get born date
                if data.startswith("Birthday:"):
                    born_data = span.find_next_siblings('a')
                    if born_data:
                        links = born_data[:-1] # remove last <a>
                        born_date = " ".join([link.get_text().strip() for link in links])
                        break

            for span in title_spans:
                data = span.get_text().strip()
                # get died date
                if data.startswith("Died on:"):
                    died_data = span.find_next_siblings('a')
                    if died_data:
                        died_date = " ".join([link.get_text().strip() for link in died_data])

        obj = {
                "category": f"{cat_name}",
                "name": f"{person_name}",
                "image": f"{image}",
                "nationality": "",
                "religion": "",
                "description": f"{description}",
                "generalInformation": [
                { "name": "Born", "value": f"{born_date}" },
                { "name": "Died", "value": f"{died_date}" },
                { "name": "Occupation", "value": f"{cat_name}" },
                { "name": "Famous For", "value": "" }
                ]
        }
        # add data in jsonl file
        with open("json_data/data.jsonl", "a", encoding="utf-8") as file:
            json.dump(obj, file, ensure_ascii=False)
            file.write("\n")
        print("Successfully Added data in jsonl file")



    except Exception as error:
        print("Error: in save_details()", error)



if __name__ == "__main__":
    ALL_PROXIES = ProxiesCrawler().get_proxies(0,10)
    cat_names, cat_urls = get_categories(main_url, ALL_PROXIES)
    if cat_names and cat_urls:
        for cat_name, cat_url in zip(cat_names, cat_urls):
            print("-"*30, f"{cat_name}", "-"*30)

            time.sleep(2)
            person_names, person_urls = get_persons(cat_url, ALL_PROXIES)
            if person_names and person_urls:
                print(f"Total {cat_name} are: {len(person_urls)}")
                for person_name, person_url in zip(person_names, person_urls):
                    print("-"*20, f"{person_name}", "-"*20)
                    time.sleep(2)
                    save_details(person_url, cat_name, person_name, ALL_PROXIES)

            