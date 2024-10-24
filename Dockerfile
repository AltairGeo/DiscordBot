FROM python:3.9-slim


RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . /bot
WORKDIR /bot


CMD ["python", "./src/bot.py"]
