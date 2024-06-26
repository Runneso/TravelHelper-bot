def delay(node_name: str) -> str:
    return f"Теперь введи количество дней, которые ты хочешь провести в {node_name}."


class Errors:
    invalid_transport_type = "Выбери тип транспорта с помощью клавиатуры."
    invalid_datetime_start = "Укажи верную даты в формате {день}/{месяц}/{год} {часы}:{минуты}."
    invalid_length = "Отправь верное количество пунктов."
    invalid_node_name = "Данная локация не найдена."
    invalid_node_delay = "Отправь верное количество дней."


start_creation = "Вижу ты решил отправиться в путешествие. Круто! Укажи название путешествия."
transport_string = "Теперь укажи тип транспорта. (От этого будет зависеть время в пути)."
start_datetime = ("Теперь укажи дату начала поездки в формате {день}/{месяц}/{год} {часы}:{минуты}.\n"
                  "Например 10/10/2021 13:15")
length_string = ("Со временем определились, теперь время определится с длинной поездки.\n"
                 "Сколько пунктов ты хочешь посетить в процессе путешествия? (от 1 до 30)")
node_name_string = ("Теперь введи название пункта в формате {название}, {город}, {страна}.\n"
                    "Например: Малиновка, Калининград, Россия")
end_creation = ("Путешествие успешно добавлено, чтобы посмотреть свои путешествия используй команду /my_journeys.\n\n"
                "Чтобы получить доступ к определённому путешествию по ID, используй /journey {ID}.\n\n")
