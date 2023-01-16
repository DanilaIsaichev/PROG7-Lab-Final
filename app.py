from datetime import datetime
from flask import Flask, jsonify
from os import getenv
from requests import request
from time import sleep

import xml.etree.ElementTree as ET
import json


def create_app():
    """Функция создания приложения"""

    app = Flask("Currencies")
    app.config["JSON_AS_ASCII"] = False

    return app


def get_counter():
    """Функция получения значения счётчика"""

    # Считываем значения из файла
    with open("./counter.json", "r") as file:

        counter = json.loads(file.read())
        counter["last_request"] = datetime.fromisoformat(counter["last_request"])
        counter["date"] = datetime.fromisoformat(counter["date"])

        # проверяем, не изменился ли день
        if counter["date"].day != datetime.now().day or counter["date"].month != datetime.now().month or counter["date"].year != datetime.now().year:
            counter["date"] = datetime.now()
            counter["total_requests"] = 0

    return counter


app = create_app()

counter = get_counter()


@app.route("/")
def main_route():
    """Маршрут с информацией об авторах"""

    html = """<h4>Авторы:</h4>
    <p>Исайчев Данила</p>
    <p>Мельников Фёдор</p>
    <p>Суркова Елизавета</p>
    <p>Шумякин Илья</p>"""

    return html


@app.route("/get_currencies")
def get_currencies():
    """Маршрут с информацией об актуальном курсе валют"""

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

        result = request("GET", "http://www.cbr.ru/scripts/XML_daily.asp")

        # Проверяем результат запроса
        if result.status_code == 200:

            valutes_data = ET.fromstring(result.content).findall("Valute")

            valutes_list = []

            for valute in valutes_data:
                val_code = valute.find("CharCode").text
                val_id = valute.get("ID")
                val_name = valute.find("Name").text

                # Сколько стоит в рублях одна единица валюты
                val_value = float(valute.find("Value").text.replace(",",".")) / float(valute.find("Nominal").text.replace(",","."))

                valutes_list.append({"Code": val_code, "ID": val_id,"Name": val_name, "Value": val_value})

            return jsonify(valutes_list)

        # ошибка при получении данных
        else:
            return result.status_code

    # Превышено суточное количество запросов
    else:
        return "Too many requests for today"


@app.route("/get_currency/<string:val_code>/<int:day_start>.<int:month_start>.<int:year_start>/<int:day_end>.<int:month_end>.<int:year_end>")
def get_currency_by_date(val_code: str, day_start: int, month_start: int, year_start: int, year_end: int, month_end: int, day_end:int):
    """Маршрут с информанией о курсах определённой валюты за промежуток времени между двумя датами"""

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

        result = request("GET", f"http://www.cbr.ru/scripts/XML_dynamic.asp?date_req1={day_start}/{month_start}/{year_start}&date_req2={day_end}/{month_end}/{year_end}&VAL_NM_RQ={val_code}")

        # Проверяем результат запроса
        if result.status_code == 200:

            records_list = []

            records = ET.fromstring(result.content).findall("Record")
            if records == []:
                return "No data about this currency"
            else:
                for record in records:
                    records_list.append({"Date": record.get('Date'), "Value": float(record.find('Value').text.replace(",",".")) / float(record.find('Nominal').text.replace(",","."))})

                return jsonify({"ID": val_code, "Records": records_list})

        # ошибка при получении данных
        else:
            return result.status_code

    # Превышено суточное количество запросов
    else:
        return "Too many requests for today"


if __name__ == "__main__":
    port = getenv("PORT")
    if port is None:
        app.run(host="0.0.0.0", port=80)
    else:
        app.run(host="0.0.0.0", port=port)
