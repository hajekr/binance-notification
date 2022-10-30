FROM arm64v8/python:3

ENV DB_HOST db
ENV DB_USER binance-notification
ENV DB_PASSWORD password

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./notify-slack-news.py" ]