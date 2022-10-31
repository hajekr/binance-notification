FROM python:3

ENV DB_HOST db
ENV DB_USER binance-notification
ENV DB_PASSWORD password
ENV DB_NAME binance-notification

WORKDIR /src

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get -y update && apt-get -y upgrade
RUN apt-get install -y cron
RUN crontab crontab.txt

RUN ["chmod", "+x", "/src/entrypoint.sh"]

CMD ["/src/entrypoint.sh"]