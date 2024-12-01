# Run
## 1. Clone repo.
  ```
  https://github.com/AltairGeo/DiscordBot/edit/master/README.md
  ```
## 2. Create .env file
  ```
  cd DiscordBot
  vim .env
  ```
And fill it out as follows
  ```
  DISCORD_TOKEN="Your discord bot token"
  YANDEX_MAP=<"Your token for yandex-map-static from here https://yandex.ru/maps-api/products/static-api">
  ```

## 3. Install dependency
  ```
  python -m venv .venv # create virtual enviroment
  
  source .venv/bin/activate # For linux
  
  pip install -r requirements.txt
  ```
## 4. Run
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
  ExecStart=/<path_to_your_bot_folder>/DiscordBot/.venv/bin/python3 /<path_to_your_bot_folder>/DiscordBot/src/bot.py
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

## Clone repo
```
git clone https://github.com/AltairGeo/DiscordBot
```
## Move to directory with bot
```
cd DiscordBot
```
## Build image
```
docker build -t <your_image_name> .
```
## Run
```
docker run -e -d DISCORD_TOKEN=<Your-Discord-Bot-Token> \
-e YANDEX_MAP=<Your-Yandex-Map-Static-Api-Key> \
-e DB_HOST=<IP-Your-DataBase \
-e DB_PORT=<Your-DB-Port> \
-e DB_USER=<Your-DB-User> \
-e DB_PASSWORD=<Your-DB-Password> \
-e DB_DB=ds-bot \
--restart unless-stopped <your-image-name>
```

<p>Use Mysql or Mariadb for database</p>

<p>YANDEX_MAP from here https://yandex.ru/maps-api/products/static-api</p>
