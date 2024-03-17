def hello(username: str):
    return f"Привет, {username}."


def hello_new_user(username: str):
    return (f"Привет, {username}, вижу ты здесь впервые, давай уточним пару фактов о тебе."
            f" Сколько тебе лет?")


help_string = ("Весь список команд:\n"
               "/start - начать,\n"
               "/help - помощь,\n"
               "/profile - получить свой профиль,\n"
               "/create_journey - создать мероприятие,\n"
               "/delete_journey {ID} - удалить мероприятие,\n"
               "/my_journeys - получить список своих мероприятий,\n"
               "/journey {ID} - получить своё мероприятие по ID,\n")
location_string = "Отправь нам свою геопозицию, чтобы мы определили твоё местоположение."
bio_string = "А теперь расскажи немного о себе."
info_string = "Теперь ты можешь использовать бота для создания своих путешествий. Пиши /help, если нужна помощь."
left, right = "◀️", "▶️"
down, up = "⬇️️", "️⬆️"
weather = "⛅️"
cancel = "✖️"
