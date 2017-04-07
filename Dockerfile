FROM python:3.6-alpine
MAINTAINER Viet Le "lttviet@gmail.com"

RUN mkdir -p /src

WORKDIR /src
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src .

EXPOSE 8000

CMD [ "gunicorn", "superlists.wsgi:application", \
      "--bind", "0.0.0.0:8000",                  \
      "--capture-output",                        \
      "--access-logfile", "-",                   \
      "--error-logfile", "-"                     \
]
VOLUME /database /static
