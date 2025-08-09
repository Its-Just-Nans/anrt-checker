# anrt-checker [![pypi version](https://img.shields.io/pypi/v/anrt-checker)](https://pypi.org/project/anrt-checker/) ![pypi downloads](https://img.shields.io/pypi/dm/anrt-checker)

- <https://pypi.org/project/anrt-checker/> - pypi page
- <https://pypistats.org/packages/anrt-checker> - pypi stats
- <https://github.com/Its-Just-Nans/anrt-checker> - repo

Scrap PhD offers from [ANRT website](https://offres-et-candidatures-cifre.anrt.asso.fr) and send them to a discord channel.

The discord server: **project is not enabled anymore, you can fork it and enable again the cron**

## Usage

```sh
export WEBHOOK_URL="https://discord.com/api/webhooks/....."
export SECRET_LOGIN="https://offres-et-candidatures-cifre.anrt.asso.fr/autoconnect/..."
# or use a .env file
python -m anrt_checker
```

## LICENSE

- [MIT](LICENSE)
