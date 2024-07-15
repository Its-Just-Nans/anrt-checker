import requests
from requests.adapters import HTTPAdapter, Retry
from hashlib import sha256
from json import dumps, loads
from os.path import exists
from dotenv import load_dotenv
from os import getenv
import warnings

warnings.filterwarnings("ignore")
load_dotenv()

SECRET_LOGIN = getenv("SECRET_LOGIN")
DATA = "data.json"
URL_WEBHOOK = getenv("WEBHOOK_URL")


def try_request(func, *args, **kwargs):
    res = None
    s = requests.Session()
    retries = Retry(
        total=20,
        backoff_factor=1,
        backoff_jitter=0.5,
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


# login to get the cookie
login = try_request("get", SECRET_LOGIN)
cookie = login.history[0].cookies["PHPSESSID"]


def make_sha(item):
    j = dumps(item, indent=4)
    m = sha256()
    m.update(j.encode())
    return m.hexdigest()


def load_data():
    if not exists(DATA):
        with open(DATA, "w") as file:
            file.write("[]")
    try:
        with open(DATA, "r") as file:
            loaded = loads(file.read())
    except Exception as _e:
        loaded = []
    return loaded


# get the data
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


def notify(text):
    try_request(
        "post",
        URL_WEBHOOK,
        json={
            "username": "ANTR checker",
            "content": text,
            "avatar_url": "https://offres-et-candidatures-cifre.anrt.asso.fr/public/images/logos/logo-cifre-s.png",
        },
    )


current_data = load_data()
to_add = []
try:
    resp = response.json()
except Exception as e:
    print("Error during parsing")
    print(e)
    print(response.text)
    resp = {}

if "data" not in resp:
    # notify("Invalid cookie")
    print("Cookie size: {len(cookie)}")
    exit(1)

resp = resp["data"]

found = []

for one_item in resp:
    shaed = str(make_sha(one_item))
    if shaed not in current_data:
        found.append(one_item)
        to_add.append(shaed)

print(f"Found {len(found)} new items")
for one_item in found:
    smol_item = f"{one_item['titre']}\n{one_item['ville']} - {one_item['rs']}\nhttps://offres-et-candidatures-cifre.anrt.asso.fr/espace-membre/offre/detail/{one_item['crypt']}"
    notify(smol_item + "\n-------------------")
    print("New item found")


final = current_data + to_add

with open(DATA, "w") as file:
    txt = dumps(final, indent=4)
    file.write(txt)
