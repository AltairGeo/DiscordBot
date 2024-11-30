import os
from dotenv import load_dotenv 

load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DB = os.getenv("DB_DB")
TOKEN = os.getenv("DISCORD_TOKEN")
apikey_yandex_map_static = os.getenv("YANDEX_MAP")
WIKI_URL = "https://ru.wikipedia.org/wiki/%D0%A1%D0%BB%D1%83%D0%B6%D0%B5%D0%B1%D0%BD%D0%B0%D1%8F:%D0%A1%D0%BB%D1%83%D1%87%D0%B0%D0%B9%D0%BD%D0%B0%D1%8F_%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B8%D1%86%D0%B0"
ENABLE_WIKI_MODULE = 1

SERVER_ID = "1020730255742341151"
MOD_ID = "1135691288117776394"
news_id = "1266831631474360502"
colorscheme = [
"#A2C3DB",
"#8871A0",
"#8AAF22",
"#DCB12D",
"#3F9F9F",
"#e77c8d",
"#937860",
]
log_channel_id = "1135697257761611816"
