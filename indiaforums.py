from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from _Proxies import ProxiesCrawler
from urllib.parse import urlparse, parse_qs
import requests
import random
import json
import time

main_url = "https://www.indiaforums.com"

male_url = "https://www.indiaforums.com/person/list?cid=1&g=1"
female_url = "https://www.indiaforums.com/person/list?cid=1&g=2"

# This function will check how many pages are there
def check_howmany_pages(soup:BeautifulSoup):
    try:
        # find pagination div
        pagination_div = soup.find('div', attrs={'class':'pagination2-center'})
        last_anchor_tag = pagination_div.find_all('a')
        if last_anchor_tag:
            url = last_anchor_tag[-1].get('href')
            # parse url to find number from query
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            number = query_params.get("pn", [None])[0]
            return number

    except Exception as error:
        print("Error: in check_howmany_pages()", error)
        return 0

# This function will get detail url and call save_details() function with url for getting and saving data
def get_celeb_names_urls(url, gender, Proxies):
    try:
        ua = UserAgent()
        headers = {
            'User-Agent':ua.random
        }
        RandomProxy = random.choice(Proxies)
        response = requests.get(url, proxies={RandomProxy[1]:RandomProxy[0]}, headers=headers)
        print('status_code:',response.status_code)

        soup = BeautifulSoup(response.text, 'html.parser')

        # check how many pages
        number = check_howmany_pages(soup)
        print('-'*20, f"Total Pages of {gender} Actor are {number}", "-"*20)
        if number:
            for num in range(1, int(number)+1):
                print('-'*10, f"Scraping page-{num}", '-'*10)
                time.sleep(2)
                page_url = f"{url}&pn={num}"
                if num == 1:
                    page_url = url
                
                ua = UserAgent()
                headers = {
                    'User-Agent':ua.random
                }
                RandomProxy = random.choice(Proxies)
                response = requests.get(page_url, proxies={RandomProxy[1]:RandomProxy[0]}, headers=headers)
                print('status_code:',response.status_code)

                soup = BeautifulSoup(response.text, 'html.parser')

                # find name and page url
                main_div = soup.find('div', attrs={'class':'celeb-page__container'})
                if main_div:
                    for i in main_div.find_all('a'):
                        name =  i.find('p').get_text().strip()
                        link_data = i.get('href')
                        link = f"{main_url}{link_data}"

                        # call save function
                        time.sleep(1)
                        save_details(link, name, gender, Proxies)
        else:
            print("page number is not found! means it is only one page")
        
    except Exception as error:
        print("Error: in get_celeb_urls()", error)
    

# This function will get details and save in jsonl file
def save_details(url, name, gender, Proxies):
    try:
        ua = UserAgent()
        headers = {
            'User-Agent':ua.random
        }
        RandomProxy = random.choice(Proxies)
        page_url = f"{url}/about"
        response = requests.get(page_url, proxies={RandomProxy[1]:RandomProxy[0]}, headers=headers)
        print('status_code:',response.status_code)

        soup = BeautifulSoup(response.text, 'html.parser')
        # get category
        cat_name = ""
        if gender == "male":
            cat_name = "Actor"
        else:
            cat_name = "Actress"

        # get image
        image = ""
        image_data = soup.find('img', attrs={'class':'celeb-about__topcontent-image'})
        if image_data:
            image = image_data.get('src')

        print(name)

        # find description
        description = ""
        description_data = soup.find('p', attrs={'class':'celeb-about__topcontent-info'})
        if description_data:
            description = description_data.get_text().strip()

        occupation = ""
        born_date = ""
        nationality = ""
        religion = ""
        famous_for = ""

        detail_divs = soup.find_all('div', attrs={'class':'celeb-about__info-subitemtitle'})
        if detail_divs:
            for div in detail_divs:
                try:
                    div_data = div.get_text().strip()
                    # find occupation
                    if div_data.startswith("Profession"):
                        prof_div = div.find_next('div')
                        if prof_div:
                            occupation = prof_div.get_text().strip()
                    # find DOB
                    if div_data.startswith("Date Of Birth"):
                        dob_div = div.find_next('div').find_all('p')
                        if prof_div:
                            born_date = dob_div[0].get_text().strip()
                    # find Nationality
                    if div_data.startswith("Nationality"):
                        nat_div = div.find_next('div')
                        if prof_div:
                            nationality = nat_div.get_text().strip()
                    # find Religion
                    if div_data.startswith("Religion"):
                        rel_div = div.find_next('div').find_all('p')
                        if prof_div:
                            religion = rel_div[0].get_text().strip()
                    # find Famous for
                    if div_data.startswith("Awards"):
                        fam_div = div.find_next('div')
                        if fam_div:
                            famous_for = fam_div.get_text().strip()
                except:
                    continue

        

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
    get_celeb_names_urls(male_url, "male", ALL_PROXIES)
    get_celeb_names_urls(female_url, "female", ALL_PROXIES)
    print("-"*20, "All data has been scraped succeessfully!", "-"*20)