"""anrt_checker lib"""

from os import getenv
from os.path import exists
from hashlib import sha256
import warnings
from json import dumps, loads
import requests
from requests.adapters import HTTPAdapter, Retry
from dotenv import load_dotenv


def try_request(func, *args, **kwargs):
    """try request"""
    res = None
    s = requests.Session()
    retries = Retry(
        total=20,
        backoff_factor=1.5,
        status_forcelist=[500, 502, 503, 504],
    )
    s.mount("https://", HTTPAdapter(max_retries=retries))

    try:
        if func == "get":
            res = s.get(*args, **kwargs, timeout=1)
        else:
            res = s.post(*args, **kwargs, timeout=1)
    except Exception as _e:
        print("Error during request")
        # print(_e)
        exit(1)
    return res


def make_sha(item):
    """return a sha256 hash"""
    j = dumps(item, indent=4)
    m = sha256()
    m.update(j.encode())
    return m.hexdigest()


def load_data(path_to_filename):
    """load the data"""
    if not exists(path_to_filename):
        with open(path_to_filename, "w", encoding="utf-8") as file:
            file.write("[]")
    try:
        with open(path_to_filename, "r", encoding="utf-8") as file:
            loaded = loads(file.read())
    except Exception as _e:
        loaded = []
    return loaded


def notify(url, text):
    """webhook notify"""
    try_request(
        "post",
        url,
        json={
            "username": "ANRT checker",
            "content": text,
            "avatar_url": "https://offres-et-candidatures-cifre.anrt.asso.fr/public/images/logos/logo-cifre-s.png",
        },
    )


def main():
    """main function"""
    warnings.filterwarnings("ignore")
    load_dotenv()
    data_filename = getenv("DATA_FILENAME")
    if data_filename is None:
        data_filename = "data.json"
    secret_login = getenv("SECRET_LOGIN")
    if secret_login is None:
        print("No secret login in env SECRET_LOGIN")
        exit(1)
    webhook_url = getenv("WEBHOOK_URL")
    if webhook_url is None:
        print("No webhook url in env WEBHOOK_URL")
        exit(1)

    login = try_request("get", secret_login)
    cookie = login.history[0].cookies["PHPSESSID"]

    response = try_request(
        "post",
        "https://offres-et-candidatures-cifre.anrt.asso.fr/espace-membre/offre/dtList",
        cookies={
            "PHPSESSID": cookie,
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={
            "draw": "1",
            "offreType": "entreprise",
        },
    )

    current_data = load_data(data_filename)
    to_add = []
    try:
        resp = response.json()
    except Exception as e:
        print("Error during parsing")
        print(e)
        print(response.text)
        resp = {}

    if "data" not in resp:
        # notify(webhook_url, "Invalid cookie")
        print("Cookie size: {len(cookie)}")
        exit(1)

    resp = resp["data"]

    found = []

    for one_item in resp:
        result_sha = str(make_sha(one_item))
        if result_sha not in current_data:
            found.append(one_item)
            to_add.append(result_sha)

    print(f"Found {len(found)} new items")
    for one_item in found:
        smol_item = f"{one_item['titre']}\n{one_item['ville']} - {one_item['rs']}\n"
        smol_item += f"https://offres-et-candidatures-cifre.anrt.asso.fr/espace-membre/offre/detail/{one_item['crypt']}"
        smol_item += "\n-------------------"
        notify(webhook_url, smol_item)
        print("New item found")

    final = current_data + to_add

    with open(data_filename, "w", encoding="utf-8") as file:
        txt = dumps(final, indent=4)
        file.write(txt)
