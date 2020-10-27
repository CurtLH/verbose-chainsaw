import json
from bs4 import BeautifulSoup as bs
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# create a session
s = requests.Session()
retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
s.mount("http://", HTTPAdapter(max_retries=retries))
s.headers.update(
    {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
    }
)

# submit a request for the first page of ads
r = s.get("http://boston.skipthegames.com/")

# get the URLs to all of the ads
urls = []
soup = bs(r.content, "html.parser", from_encoding="iso-8859-1")
gallery = soup.find("div", {"class": "clsfds-display-mode gallery"})
href = gallery.find_all(href=True)
for h in href:
    if h.get("href") not in urls:
        urls.append(h.get("href"))
    else:
        pass

def lambda_handler(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps(f"There are {len(urls)} found")
}
