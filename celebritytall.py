from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from _Proxies import ProxiesCrawler
import requests
import random
import re
import time
import json

main_url = "https://celebritytall.com/category-sitemap.xml"

# This function will ectract and retuurn category from given url
def extract_category(url):
    parsed = urlparse(url)
    parts = parsed.path.strip('/').split('/')
    
    # Find 'category' and get the next part
    if 'category' in parts:
        idx = parts.index('category')
        if idx + 1 < len(parts):
            return parts[idx + 1]
    return None

# This function will return category name and links using "sitemap"
def get_cat_url(url, Proxies):
    cat_urls = []
    cat_names = []
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
        urls = [loc.text for loc in soup.find_all('loc')]

        # Filter category URLs (if needed)
        category_urls = [url for url in urls if '/category/' in url]

        for url in category_urls:
            cat_name_data = extract_category(url)
            cat_name = str(cat_name_data).replace("-"," ")
            # apppend data in list
            cat_urls.append(url)
            cat_names.append(cat_name)
        
        return cat_urls, cat_names
            

    except Exception as error:
        print("Error: in get_cat_url()", error)
        return cat_urls, cat_names


# This function will check page exists or not
def check_page_exists(soup):
    try:
        page_nav = soup.find('nav', attrs={'id':'nav-below'})
        if page_nav:
            nav_link_div = page_nav.find('div', attrs={'class':'nav-links'})
            anchor_tags = nav_link_div.find_all_next('a', attrs={'class':'page-numbers'})
            if anchor_tags:
                last_page_link = anchor_tags[-2].get('href')
                # extract page number from it
                match = re.search(r'/page/(\d+)/', last_page_link)
                if match:
                    number = int(match.group(1))
                    return number
                return None
        else:
            return 0

    except Exception as error:
        print("Error: in check_page_exists()", error)
        return 0

def get_personality_details(url,cat_name, Proxies):
    try:
        ua = UserAgent()
        headers = {
            'User-Agent': ua.random
        }
        RandomProxy = random.choice(Proxies)
        response = requests.get(url, proxies={RandomProxy[1]:RandomProxy[0]}, headers=headers)

        soup = BeautifulSoup(response.text, 'html.parser')

        # find main div
        main_div = soup.find('div', attrs={'class':'entry-content'})
        
        # check there is table or not
        table = ""
        try:
            table = main_div.find('table', attrs={'class':'tablepress'})
        except Exception as er:
            pass 

        # get image
        image = main_div.find('img', attrs={'class':'alignnone'}).get('src')
        name = ""
        nationality = ""
        born_date = ""
        occupation = ""
        religion = ""
        description = ""

        if table:
            description = main_div.find_all('p')[0].get_text().strip()
            for tr in table.find('tbody').find_all('tr'):
                td = tr.find_all('td')[0].get_text().strip()
                # get name
                if td.startswith("Real Name"):
                    name = tr.find_all('td')[1].get_text().strip()
                # get occupation
                if td.startswith("Profession"):
                    occupation = tr.find_all('td')[1].get_text().strip()
                # get date of birth
                if td.startswith("Date of Birth"):
                    born_date = tr.find_all('td')[1].get_text().strip()
                # get nationality
                if td.startswith("Birth Place"):
                    nationality = tr.find_all('td')[1].get_text().strip()

            # save data in json file
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
            with open("json_data/data.jsonl", "a", encoding="utf-8") as file:
                json.dump(obj, file, ensure_ascii=False)
                file.write("\n")
            print("Added data in jsonl file")

            
        else:
            # find all paragraphs
            all_p_tags = main_div.find_all('p')
            # get description
            if all_p_tags:
                description = all_p_tags[0].get_text().strip()
            for p in all_p_tags:
                data = p.get_text().strip()
                # get name
                if data.startswith("Real Name:"):
                    name = data.replace("Real Name:","").strip()
                if data.startswith("Birth Name"):
                    name = data.replace("Birth Name:","").strip()
                # get occupation
                if data.startswith("Occupation:"):
                    occupation = data.replace("Occupation:","").strip()
                # get date of birth
                if data.startswith("Date Of Birth:"):
                    born_date = data.replace("Date Of Birth:","").strip()
                # get nationality
                if data.startswith("Nationality:"):
                    nationality = data.replace("Nationality:","").strip()
                # get religion
                if data.startswith("Religion:"):
                    religion = data.replace("Religion:","").strip()

            # add data in json file
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
            with open("json_data/data.jsonl", "a", encoding="utf-8") as file:
                json.dump(obj, file, ensure_ascii=False)
                file.write("\n")
            print("Added data in jsonl file")


    except Exception as error:
        print("Error: in get_personality_details()", error)


def save_personalities(url,cat_name, Proxies):
    try:
        ua = UserAgent()
        headers = {
            'User-Agent': ua.random
        }
        RandomProxy = random.choice(Proxies)
        response = requests.get(url, proxies={RandomProxy[1]:RandomProxy[0]}, headers=headers)

        soup = BeautifulSoup(response.text, 'html.parser')

        # check more than one page or not
        number = check_page_exists(soup)
        print("-"*15, f"Total Pages are {number}", "-"*15)
        if number:
            for u in range(1,number+1):
                if u == 3:
                    break
                print("-"*10, f"visiting page-{u}", "-"*10)

                page_url = f"{url}page/{u}/"
                time.sleep(2)

                ua = UserAgent()
                headers = {
                    'User-Agent': ua.random
                }
                RandomProxy = random.choice(Proxies)
                try:
                    response = requests.get(page_url, proxies={RandomProxy[1]:RandomProxy[0]}, headers=headers) 

                    soup = BeautifulSoup(response.text, 'html.parser')

                    # find url of each person
                    all_h2s = soup.find_all('h2', attrs={'class':'entry-title'})
                    print(f"Total Personality on this page ({len(all_h2s)})")

                    for h2 in all_h2s:
                        link = h2.find('a').get('href')
                        time.sleep(2)
                        # Get specific person data and save it in json file
                        get_personality_details(link,cat_name, Proxies)

                except Exception as e:
                    continue

    except Exception as error:
        print("Error: in get_personaliities()", error)    
    

if __name__ == "__main__":
    ALL_PROXIES = ProxiesCrawler().get_proxies(0,10)
    cat_urls, cat_names = get_cat_url(main_url, ALL_PROXIES)
    if cat_urls:
        for cat_url, cat_name in zip(cat_urls, cat_names):
            print("-"*30,cat_name,"-"*30)
            # get the list of category's personality urls
            time.sleep(1)
            save_personalities(cat_url,cat_name, ALL_PROXIES)
            break