import logging
import os
import json
import shutil
import tarfile
from bs4 import BeautifulSoup as bs
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

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
    urls = set([h.get("href") for h in urls])

    return urls


def make_tarfile(output_filename, source_dir):

    # create a tar.gz file
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))


def lambda_handler(event, context):
    """
    Run scraper for a given city and write files to S3
    """

    # define configuation values
    city = "baton-rouge"
    city_code = "BAT"
    max_page_num = 15
    s3_bucket = "htprawscrapes"

    # add 1 to the max page number
    max_page_num = max_page_num + 1

    # create a directory for the results
    now = datetime.strftime(datetime.now(), "%Y%m%d%H%M")

    # make a folder for the output
    folder_name = f"skipthegames_{city}_{now}"
    os.makedirs(folder_name, exist_ok=True)
    logging.info(f"{folder_name} created for the ads")

    # define the filenames
    tar_filename = f"{folder_name}.tar.gz"
    s3_key = tar_filename.replace("_", "/")

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
    logging.info(f"There are {len(urls)} URLs found")

    # download the page content for each ad
    counter = 0
    for url in urls:
        try:
            ad_url = base_url + url.split("/")[-1]
            filename = url.split("/")[-1] + ".html"
            r = submit_request(s, ad_url)
            fpath = folder_name + "/" + filename
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(str(r.text))
            counter += 1

        except Exception:
            logging.warning(f"Unable to retreive {ad_url}")
            pass

    logging.info(f"Successfully retreived {counter} ads")

    # compress the results into a tarfile
    make_tarfile(tar_filename, folder_name)
    logging.info(f"{tar_filename} created")

    # upload the tarfile to S3
    # s3.upload_file(tar_filename, s3_bucket, s3_key)
    # logging.info(f"{s3_key} uploaded to S3")

    # remove the tar file
    # os.remove(tar_filename)
    # logging.info(f"{tar_filename} removed")

    # remove the directory of files
    # shutil.rmtree(folder_name)
    # logging.info(f"{folder_name} removed")

    return {
        "statusCode": 200,
        "city": city,
        "urls_found": len(urls),
        "ads_collected": counter,
    }
