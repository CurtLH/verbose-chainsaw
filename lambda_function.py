import logging
import os
from datetime import datetime
from bs4 import BeautifulSoup as bs
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import boto3

# set up basic logging
logging.basicConfig(format="%(asctime)s %(message)s", level=logging.INFO)


def create_session():

    # create a session
    s = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
    s.mount("http://", HTTPAdapter(max_retries=retries))

    return s


def submit_request(s, url):

    # submit the request
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
    }
    r = s.get(url, headers=headers)

    # if not successful, raise an error
    if r.status_code != 200:
        raise ValueError("Request not successful")

    # if successful, return the response
    else:
        return r


def get_urls(s, url):

    r = submit_request(s, url)
    soup = bs(r.content, "html.parser", from_encoding="iso-8859-1")
    gallery = soup.find("div", {"class": "clsfds-display-mode gallery"})
    href = gallery.find_all(href=True)
    urls = set([h.get("href") for h in href])

    return urls


def lambda_handler(event, context):
    """
    Run scraper for a given city and write files to S3
    """

    # define configuation values
    city = "baton-rouge"
    city_code = "BAT"
    max_page_num = 1
    s3_bucket = "squeekyduck"

    # create S3 client
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("aws_access_key_id"),
        aws_secret_access_key=os.getenv("aws_secret_access_key"),
    )

    # add 1 to the max page number
    max_page_num = max_page_num + 1

    # create a directory for the results
    now = datetime.strftime(datetime.now(), "%Y%m%d%H%M")

    # create the base file name for S3
    base_fname = f"skipthegames/{city}/{now}"

    # define the base URL
    base_url = f"http://{city}.skipthegames.com/"

    # create a web session
    s = create_session()

    # get all of the URLs for a given city
    urls = set()
    for page_num in range(1, max_page_num):
        try:
            gallery_url = f"{base_url}?area[]=.{city_code}&p={page_num}"
            tmp = get_urls(s, gallery_url)
            urls.update(tmp)
        except Exception:
            pass
    print(f"There are {len(urls)} URLs found")

    # download the page content for each ad
    counter = 0
    for url in list(urls)[:5]:
        ad_url = base_url + url.split("/")[-1]
        r = submit_request(s, ad_url)
        if r.status_code == 200:
            data = r.text.encode("utf-8")
            filename = url.split("/")[-1] + ".html"
            s3.put_object(
                Body=data, Bucket=s3_bucket, Key=f"{base_fname}/{filename}",
            )
            counter += 1
        else:
            logging.warning(f"Unable to retreive {ad_url}")
            pass

    print(f"Successfully retreived {counter} ads")

    return {
        "statusCode": 200,
        "city": city,
        "urls_found": len(urls),
        "ads_collected": counter,
    }
