FROM python:3.6-alpine
MAINTAINER Viet Le "lttviet@gmail.com"

ENV STAGING_SERVER superlists-staging.lttviet.com

RUN mkdir -p /usr/src/app

WORKDIR /usr/src/app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD [ "python", "source/manage.py", "runserver", "0.0.0.0:8000"]
