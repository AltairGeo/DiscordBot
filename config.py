import os
from dotenv import load_dotenv 

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
apikey_yandex_map_static = os.getenv("YANDEX_MAP")
path_to_db = "warns.db"
path_to_hist_db = "hist.db"
WIKI_URL = "https://ru.wikipedia.org/wiki/%D0%A1%D0%BB%D1%83%D0%B6%D0%B5%D0%B1%D0%BD%D0%B0%D1%8F:%D0%A1%D0%BB%D1%83%D1%87%D0%B0%D0%B9%D0%BD%D0%B0%D1%8F_%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B8%D1%86%D0%B0"
ENABLE_WIKI_MODULE = 1

model = "qwen2.5:0.5b"#"llama3.1"
ai_url = "http://localhost:11434/v1/chat/completions"
SERVER_ID = "1020730255742341151"
MOD_ID = "1135691288117776394"
news_id = "1266831631474360502"
