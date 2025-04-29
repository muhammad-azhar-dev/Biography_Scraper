from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from _Proxies import ProxiesCrawler
import requests
import random
import json
import time

main_url = "https://notednames.com"


# This function will get category names and their urls and return them
def get_categories(url, Proxies):
    cat_names = []
    cat_urls = []
    try:
        ua = UserAgent()
        headers = {
            'User-Agent':ua.random
        }
        RandomProxy = random.choice(Proxies)
        response = requests.get(url, proxies={RandomProxy[1]:RandomProxy[0]}, headers=headers)

        soup = BeautifulSoup(response.text, 'html.parser')

        # find main category div
        cat_div = soup.find('div', attrs={'class':'deflinks'})
        if cat_div:
            for div in cat_div.find_all('div', attrs={'class':'def2a'}):
                a_tag = div.find('li').find('a')
                cat_name = a_tag.get_text().strip()
                cat_link = a_tag.get('href')

                # append data in their list
                cat_names.append(cat_name)
                cat_urls.append(cat_link)

        return cat_names, cat_urls


    except Exception as error:
        print("Error: in get_categories()", error)
        return cat_names, cat_urls
    

def get_detail_urls(url, Proxies):
    person_urls = []
    person_names = []
    try:
        ua = UserAgent()
        headers = {
            'User-Agent':ua.random
        }
        RandomProxy = random.choice(Proxies)
        response = requests.get(url, proxies={RandomProxy[1]:RandomProxy[0]}, headers=headers)
        print('status:',response.status_code)

        soup = BeautifulSoup(response.text, 'html.parser')

        all_boxes = soup.find_all('div', attrs={'class':"def5"})
        if all_boxes:
            for box in all_boxes:
                anchor_tag = box.find('a')
                if anchor_tag:
                    person_url = anchor_tag.get('href')
                    person_urls.append(person_url)

                name_data = box.find('div', attrs={'class':'def6'})
                if name_data:
                    name = name_data.get_text().strip()
                    person_names.append(name)

        return person_names, person_urls

    except Exception as error:
        print("Error: in get_detail_urls()", error)
        return person_names, person_urls
    

def save_details(url, cat_name, person_name, Proxies):
    try:
        ua = UserAgent()
        headers = {
            'User-Agent':ua.random
        }
        RandomProxy = random.choice(Proxies)
        response = requests.get(url, proxies={RandomProxy[1]:RandomProxy[0]}, headers=headers)
        print('status:',response.status_code)

        soup = BeautifulSoup(response.text, 'html.parser')

        if person_name:
            name = person_name
        else:
            name = ""

        image = ""
        image_data = soup.find('img', attrs={'class':'def9a'})
        if image_data:
            image = image_data.get('src')
            print(image)
        
        nationality = ""
        religion = ""
        born_date = ""
        died_date = ""
        occupation = ""
        famous_for = ""

        heading_divs = soup.find_all('div', attrs={'class':'d7'})
        if heading_divs:
            for div in heading_divs:
                try:
                    data = div.get_text().strip()
                    # find DOB
                    if data.startswith("BIRTHDAY"):
                        dob_data = div.find_next('div', attrs={'class':'d8'})
                        if dob_data:
                            date_str = dob_data.get_text().strip()
                            born_date = " ".join(date_str.split())
                    # find Dath date
                    if data.startswith("DEATHDATE"):
                        dath_data = div.find_next('div', attrs={'class':'d8'})
                        if dath_data:
                            died_date = dath_data.get_text().strip()
                    # find Nationality
                    if data.startswith("NATIONALITY"):
                        nat_data = div.find_next('div', attrs={'class':'d8'})
                        if nat_data:
                            nationality = nat_data.get_text().strip()
                    # find Occupation
                    if data.startswith("PROFESSION"):
                        prof_data = div.find_next('div', attrs={'class':'d8'})
                        if prof_data:
                            occupation_data = prof_data.find_all('a')
                            if occupation_data:
                                occupation = occupation_data[0].get_text().strip()
                    # find Famous from
                    if data.startswith("FAMOUS FROM/AS"):
                        fam_data = div.find_next('div', attrs={'class':'d8'})
                        if fam_data:
                            famous_for = fam_data.get_text().strip()
                    # find Religion
                    if data.startswith("RELIGION"):
                        rel_data = div.find_next('div', attrs={'class':'d8'})
                        if rel_data:
                            religion = rel_data.get_text().strip()
                except:
                    continue

        obj = {
                "category": f"{cat_name}",
                "name": f"{name}",
                "image": f"{image}",
                "nationality": f"{nationality}",
                "religion": f"{religion}",
                "description": "",
                "generalInformation": [
                { "name": "Born", "value": f"{born_date}" },
                { "name": "Died", "value": f"{died_date}" },
                { "name": "Occupation", "value": f"{occupation}" },
                { "name": "Famous For", "value": f"{famous_for}" }
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
            person_names, person_urls = get_detail_urls(cat_url, ALL_PROXIES)
            if person_urls:
                print(f"Total Persons are: {len(person_urls)}")
                for person_name, person_link in zip(person_names, person_urls):
                    print("-"*15, f"Scraping '{person_name}'", "-"*15)
                    time.sleep(1)
                    save_details(person_link, cat_name, person_name, ALL_PROXIES)
    print("-"*20, "All data has been scraped succeessfully!", "-"*20)
