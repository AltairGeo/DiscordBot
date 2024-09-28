# Run
1. Clone repo.
```
https://github.com/AltairGeo/DiscordBot/edit/master/README.md
```
2. Create .env file
```
cd DiscordBot
vim .env
```
And fill it out as follows
```
DISCORD_TOKEN="Your discord bot token"
YANDEX_MAP=<"Your token for yandex-map-static from here https://yandex.ru/maps-api/products/static-api">
```

3. Install dependency
```
python -m venv .venv # create virtual enviroment

source .venv/bin/activate # For linux

pip install -r requirements.txt
```
4. Run
You can just run it manually with the ```python bot.py command```, but I recommend using the systemd daemon:
```
cd /etc/systemd/system/
sudo vim bot.service
```
And add as follows
```
[Unit]
Description=Discord bot
After=multi-user.target

[Service]
ExecStart=/<path_to_your_bot_folder>/DiscordBot/.venv/bin/python3 /<path_to_your_bot_folder>/DiscordBot/bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```
Start systemd daemon
```
systemctl enable bot # enable bot service

systemctl start bot # start bot service
```
Done!

# Docker (Recommended)

```
docker build -t <your_image_name> .

docker run -e DISCORD_TOKEN=<your_token> -e YANDEX_MAP=<your yandex map static api> <your_image_name>  # YANDEX_MAP from here https://yandex.ru/maps-api/products/static-api
```
