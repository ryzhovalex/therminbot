import os

from aiogram import Bot, Dispatcher, executor, types

from .domain import Domain
from ...helpers.logger import logger


class Thermin(metaclass=Domain):
    """Core bot based on Aiogram.
    
    Attributes:
        api_token: Token of Telegram bot to work with."""
    def __init__(
        self,
        api_token: str
    ) -> None:
        self.bot = Bot(token=api_token) 
        self.dispatcher = Dispatcher(self.bot)

    def start(self) -> None:
        """Start bot executor."""
        executor.start_polling(self.dispatcher, skip_updates=True)