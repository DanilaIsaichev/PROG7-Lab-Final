from flask import Flask, jsonify
from datetime import datetime
from requests import request
from time import sleep

import json

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

counter = {}

# Считываем значения из файла
with open("./counter.json", "r") as file:

    counter = json.loads(file.read())
    counter["last_request"] = datetime.fromisoformat(counter["last_request"])
    counter["date"] = datetime.fromisoformat(counter["date"])

    # проверяем, не изменился ли день
    if counter["date"].day != datetime.now().day and counter["date"].month != datetime.now().month:
        counter["date"] = datetime.now()
        counter["total_requests"] = 0


@app.route("/")
def main_route():
    html = """<h4>Авторы:</h4>
    <p>Исайчев Данила</p>
    <p>Мельников Фёдор</p>
    <p>Шумякин Илья</p>"""

    return html


@app.route("/get_currencies")
def get_currencies():

    # Не больше 10000 запросов в сутки
    if counter["total_requests"] < 10000:

        # Не больше одного запроса в секунду
        if (datetime.now() - counter["last_request"]).seconds <= 1:
            sleep((datetime.now() - counter["last_request"]).seconds)

        counter["last_request"] = datetime.now()
        counter["total_requests"] += 1

        # Обновляем содержимое файла
        with open("./counter.json", "w") as file:
            file.write(json.dumps({"last_request": str(counter["last_request"]), "total_requests": counter["total_requests"], "date": str(counter["date"])}))

        result = request("GET", "https://www.cbr-xml-daily.ru/daily_json.js")

        # Проверяем результат запроса
        if result.status_code == 200:
            print(result.status_code)

            data = result.json()["Valute"]

            valutes = []

            for val in data:

                # Получаем объект валюты по ключу
                val_dict = data[val]

                val_code = val_dict["CharCode"]
                val_name = val_dict["Name"]

                # Сколько стоит в рублях одна единица валюты
                val_value = val_dict["Value"] / val_dict["Nominal"]

                valutes.append({"Code": val_code, "Name": val_name, "Value": val_value})

            return jsonify(valutes)

        # ошибка при получении данных
        else:
            return result.status_code
    else:
        return "Too many requests for today"


@app.route("/get_currency/<string:val>/<int:day_start>.<int:month_start>.<int:year_start>/<int:day_end>.<int:month_end>.<int:year_end>")
def get_currency_by_date(val: str, day_start: int, month_start: int, year_start: int, year_end: int, month_end: int, day_end:int):
    start = datetime(year_start, month_start, day_start)

    end = datetime(year_end, month_end, day_end)

    if end < start:
        return "The start date should be earlier than the end date"
    else:
        return f"""<h4>{val}</h4>
    <p>{start}</p>
    <p>{end}</p>"""


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)