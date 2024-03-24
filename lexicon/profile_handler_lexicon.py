from database import Users


class Emojis:
    person = "👤"


def profile(user: Users) -> str:
    return (f"<b>ПРОФИЛЬ {Emojis.person}</b>\n\n"
            f"ID: {user.user_id}\n"
            f"Никнейм: {user.username}\n"
            f"Возраст: {user.age} лет\n"
            f"Местоположение: {user.location}\n"
            f"Биография: {user.biography}"
            )


correct_age = "Вы успешно сменили возраст."
correct_biography = "Вы успешно сменили биографию."
correct_location = "Вы успешно сменили местоположение."

age_string = "Отправь новое значение возраста."
biography_string = "Отправь свою новую биографию."
location_string = ("Отправь своё новое местоположение используя клавиатуру или с помощью сообщения в формате {город}, "
                   "{страна}.")
