FROM ubuntu:18.04


# https://hub.docker.com/_/alpine
RUN apt-get update \
    && apt-get install -y --no-install-recommends mysql-client \
    && rm -rf /var/lib/apt/lists/*

RUN pip install Flask
RUN pip3 install -r requirements.txt

WORKDIR /app

COPY . /app

EXPOSE 80

CMD [ "ubuntu:18.04", "app.py"]
