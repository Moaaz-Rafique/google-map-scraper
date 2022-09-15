from email import header
from gettext import gettext
import sys
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import csv
import re
import time
def deEmojify(text):
    regrex_pattern = re.compile(pattern = "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags = re.UNICODE)
    return regrex_pattern.sub(r'',text)

def getPageHtml(url):
    with sync_playwright() as p:
        browser = p.webkit.launch()
        page =  browser.new_page()        
        # page.evaluate("() => { document.body.style.zoom=0.25; }")
        page.goto(url)
        # time.sleep(5) #uncomment to if network is slow
        html = page.content()        
        browser.close()
        return html
def getSearchPageHtml(url, term):
    with sync_playwright() as p:
        browser = p.webkit.launch(headless=False)
        page =  browser.new_page()        
        page.goto(url)
        
        print('Waiting for page to load...')
        # page.hover(f"[aria-label='Results for {term}']")
        page.hover(f"canvas")
        print('Loading map...')
        page.mouse.wheel(0, 50)
        time.sleep(3)
        page.locator(f"button:has-text('Search this area')").click()                
        time.sleep(3)        
        page.hover(f"[aria-label='Results for {term}']")
        #uncomment to if network is slow
        print('Scrolling Now...')
        for i in range(30): ### increase for more data
            # print(i)        
            page.mouse.wheel(0, 5000)   
            time.sleep(1)
        html = page.content()        
        browser.close()
        return html

def findnth(string, substring, n):
    parts = string.split(substring, n + 1)
    if len(parts) <= n + 1:
        return -1
    return len(string) - len(parts[-1]) - len(substring)

search_term = "stores" # you can change the term for different Items


base_url = f"https://www.google.com/maps/search/{search_term}/"
# long, lat = 24.9227021,67.1200746 # change the longitude  and latitude values
get_link = input("Paste Your Url Here: ")
long=get_link[get_link.find('@')+1:get_link.find(',')]
lat=get_link[get_link.find(',')+1:findnth( get_link,',',1)]
zoom = input("Enter zoom value: ")
url = f"{base_url}@{long},{lat},{zoom}z"
print(url)
html = getSearchPageHtml(url, search_term)
searchSoup = BeautifulSoup(html, features="html.parser")

results_div = searchSoup.find("div", {"aria-label":f"Results for {search_term}"})

records = []
if results_div:
    results_a = results_div.findAll("a")
    print(f"Getting Data for {len(results_a)} stores")
    
    for i in results_a:
        record = dict()
        html = getPageHtml(i["href"])
        res_soup = BeautifulSoup(html, features='html.parser')    

        
        if res_soup:
            data_div = res_soup.find("div", {"class": "m6QErb WNBkOb"})         
            record["store name"] = res_soup.find("h1").getText()
            print("Loading data for", record["store name"])
            links = []
            try:
                record["store type"] = data_div.find("button",{"jsaction":"pane.rating.category"}).getText()
            except Exception as e:
                print("Type Not obtained for", record["store name"])                                
                # print(e)
            try:
                record["store Address"] = data_div.find("button",{"data-item-id":"address"}).getText()
            except Exception as e:
                print("Address Not obtained")
                # print(e)
            try:
                record["store website url"] = data_div.find("a",{"data-tooltip":"Open website"})["href"]
            except Exception as e:
                print("Website Not obtained for", record["store name"])                             
            try:
                record["store phone number"] = data_div.find("button",{"data-tooltip":"Copy phone number"}).getText()
            except Exception as e:
                print("store phone number Not obtained for", record["store name"])                                

           
            sub_data=data_div.findAll("div", {"class": "Io6YTe fontBodyMedium"})            
            record["google maps url"] = i["href"]
            for j in res_soup.findAll("img"):    
                try:
                    if "https://lh5" in j["src"]:
                        links.append(j['src'])
                except :
                    pass
            record["Links for Images of Store"] = links
            record["ExtraData"] = []
            for j in sub_data:
                record["ExtraData"].append(deEmojify(j.getText()))
        else:
            print("Page Did not load correctly")
        records.append(record)
        # store name
        # jsaction="pane.rating.category"
        # store type
        # store Address
        # store website url
        # store phone number
        # google maps url
else:     
    print("The link was not loaded properly")
    print("Aborting...")
    sys.exit(1)

# To save the list of records to a csv file

keys = [
    'store name',
    'store type',
    'store Address',
    'store website url',
    'store phone number',
    'google maps url',
    'Links for Images of Store',
    'ExtraData'
]
with open('Places2.csv', 'w',encoding="utf-8", errors='surrogatepass', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(records)


