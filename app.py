from flask import Flask
from datetime import datetime

app = Flask(__name__)


@app.route("/")
def main_route():
    html = """<h4>Авторы:</h4>
    <p>Исайчев Данила</p>
    <p>Мельников Фёдор</p>
    <p>Шумякин Илья</p>"""

    return html


@app.route("/get_currencies")
def get_currencies():
    pass


@app.route("/get_currency/<int:day_start>.<int:month_start>.<int:year_start>/<int:day_end>.<int:month_end>.<int:year_end>")
def get_currency_by_date(day_start, month_start, year_start, year_end, month_end, day_end):
    start = datetime(year_start, month_start, day_start)

    end = datetime(year_end, month_end, day_end)

    if end < start:
        return "The start date should be earlier than the end date"
    else:
        return f"""<p>{start}</p>
    <p>{end}</p>"""


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)