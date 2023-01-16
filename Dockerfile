FROM python:3.11-alpine

WORKDIR /app

COPY . /app

RUN pip3 install -r requirements.txt

EXPOSE 80

CMD ["python3", "app.py"]
