import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


def lambda_handler(event, context):
    """
    Run scraper for a given city and write files to S3
    """

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.5",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "DNT": "1",
        "Host": "boston.skipthegames.com",
        "TE": "Trailers",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:83.0) Gecko/20100101 Firefox/83.0",
    }

    # create a web session
    s = requests.Session()
    retries = Retry(total=4, backoff_factor=1, status_forcelist=[502, 503, 504])
    s.mount("http://", HTTPAdapter(max_retries=retries))
    print("The session has been created")

    # submit a request
    #r = s.get("https://boston.skipthegames.com/710916219561", headers=headers)
    r = s.get("https://httpbin.org/uuid", headers=headers)
    print(r.status_code)

    return {"statusCode": r.status_code}
