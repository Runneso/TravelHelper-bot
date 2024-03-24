from random import choice
from string import ascii_letters


class InviteTokensAPI:
    async def get_token(self):
        code = str()
        for _ in range(10):
            code += choice(ascii_letters)
        return code
