def hello_first_name_last_name(first_name: str, last_name: str) -> str:
    return f"Привет, {first_name} {last_name}."


def hello_username(username: str) -> str:
    return f"Привет, @{username}."


def hello_new_first_name_last_name(first_name: str, last_name: str) -> str:
    return (f"Привет, {first_name} {last_name}, вижу ты здесь впервые, давай уточним пару фактов о тебе."
            f" Сколько тебе лет?")


def hello_new_user_username(username: str) -> str:
    return (f"Привет, @{username}, вижу ты здесь впервые, давай уточним пару фактов о тебе."
            f" Сколько тебе лет?")


location_string = (
    "Теперь отправь нам свою геопозицию, чтобы мы могли определить начальную метку твоих путешествий или "
    "просто отправь сообщение в формате {город}, {страна}.")
biography_string = "А теперь расскажи немного о себе."
info_string = "Теперь ты можешь использовать бота для создания своих путешествий. Пиши /help, если нужна помощь."
help_string = ("Весь список команд:\n"
               "/start - начать,\n"
               "/help - помощь,\n"
               "/profile - получить свой профиль,\n"
               "/create_journey - создать мероприятие,\n"
               "/my_journeys - получить список своих мероприятий,\n"
               "/journey {ID} - получить своё мероприятие по ID,\n"
               "/cancel - отменить любое действие,\n")
correct_invite = "Вы успешно присоединились к путешествию."
cancel = "Вы отменили все действия."


class Errors:
    already_take_part = "Вы уже участвуете в этом путешествие."
    invalid_age = "Укажи правильный возраст."
    invalid_token = "Данное приглашение не действительно или уже было использовано."
    invalid_invite = "Сначала пройдите регистрацию, чтобы принять приглашение."
    invalid_text_location = "Укажи верное место жительства в формате {город}, {страна}."
