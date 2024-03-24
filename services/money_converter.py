from decimal import Decimal

from currency_converter import CurrencyConverter
from loguru import logger


class MoneyConverterAPI:
    def clc_usd(self, s: str, currency: str):
        if currency == "RUB":
            return Decimal(s)/Decimal("92.40")
        converter = CurrencyConverter(decimal=True)
        try:
            return converter.convert(float(s), currency, "USD")
        except Exception as error:
            logger.error(error)
            return None
