from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def getScreenReviewShots(url):
    with sync_playwright() as p:
        browser = p.webkit.launch()
        page =  browser.new_page()        
        page.evaluate("() => { document.body.style.zoom=0.25; }")
        page.goto(url)
        # page.screenshot(path="sheesh.png")
        # ua = page.query_selector(".user-agent");
        html = page.content()        
        browser.close()
        return html

# print(

base_url = 'https://www.google.com/maps/search/stores/'
long, lat = 24.9227085,67.1284716
url = f"{base_url}@{long},{lat},20z"
print(url)
html = getScreenReviewShots(url)
searchSoup = BeautifulSoup(html, features="lxml")
# )
results_div = searchSoup.find("div", {"aria-label":"Results for stores"})
if results_div:
    results_a = results_div.findAll("a")
    for i in results_a:
        print(i["href"])
else: 
    print(results_div, len(html.__str__().find("Results for stores")))

