import asyncio
import datetime
import json
import logging
import os
from pathlib import Path
from typing import Any

import dotenv
import aiofiles
from fastapi.params import Query
from orwynn.apiversion import ApiVersion
from orwynn.utils.types import Timestamp
from orwynn.log import Log
from orwynn.server import Server, ServerEngine
from orwynn.base import Model, Module, Service, Worker
from orwynn.boot import Boot
from orwynn.http import (Endpoint, EndpointResponse, HttpController,
                         LogMiddleware, HttpResponse, HttpRequest)
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (Application, ApplicationBuilder, CallbackContext,
                          CommandHandler, ContextTypes, ExtBot, MessageHandler,
                          filters, TypeHandler)


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


SAVE_DIR: Path = Path(
    "var"
)
SAVE_PATH: Path = Path(
    SAVE_DIR,
    "telegram.txt"
)


class TherminBot(Worker):
    def __init__(
        self,
        api_token: str,
        webhook_url: str,
        admin_chat_id: str
    ) -> None:
        super().__init__()

        self._webhook_url: str = webhook_url

        self._app: Application = ApplicationBuilder().token(
            api_token
        ).updater(None).build()

        self._app.bot_data["url"] = self._webhook_url
        self._app.bot_data["admin_chat_id"] = admin_chat_id

        self._app.add_handler(
            CommandHandler("start", start)
        )
        self._app.add_handler(
            MessageHandler(filters.TEXT & (~filters.COMMAND), accept)
        )

    @property
    def app(self) -> Application:
        return self._app

    async def initialize(self) -> None:
        await self._app.bot.set_webhook(url=self._webhook_url)


class TelegramController(HttpController):
    ROUTE = "/telegram"
    ENDPOINTS = [
        Endpoint(
            method="post"
        )
    ]

    async def post(self, request: HttpRequest) -> dict:
        data: dict = await request.json()
        Log.info(f"receive telegram data <{data}>")

        # text: str = data["message"]["text"]
        # timestamp: Timestamp = float(data["message"]["date"])

        async with aiofiles.open(SAVE_PATH, "a") as f:
            await f.write(json.dumps(data) + "\n")

        therminbot: TherminBot = TherminBot.ie()
        await therminbot.app.update_queue.put(
            Update.de_json(
                data=data,
                bot=therminbot.app.bot
            )
        )

        return {}


async def main() -> None:
    SAVE_DIR.mkdir(parents=True, exist_ok=True)

    dotenv.load_dotenv()
    api_token: str = os.environ["THERMIN_API_TOKEN"]
    admin_chat_id: str = os.environ["THERMIN_ADMIN_CHAT_ID"]
    server_host: str = os.environ["THERMIN_SERVER_HOST"]
    server_port: int = int(os.environ["THERMIN_SERVER_PORT"])
    webhook_url: str = os.environ["THERMIN_WEBHOOK_SERVER_URL"]

    therminbot: TherminBot = TherminBot(
        api_token=api_token,
        webhook_url=webhook_url,
        admin_chat_id=admin_chat_id
    )
    await therminbot.initialize()
    bot_app: Application = therminbot.app

    boot: Boot = await Boot.create(
        Module(
            "/",
            Providers=[],
            Controllers=[
                TelegramController,
            ]
        ),
        global_http_route="/api/v{version}",
        api_version=ApiVersion(supported={1}),
        global_middleware={
            # TODO(ryzhovalex): log middleware gives ValidationError on JSON
            #   parse again
            # 0
            # LogMiddleware: ["*"]
        }
    )

    server: Server = Server(
        engine=ServerEngine.Uvicorn,
        boot=boot
    )

    async with bot_app:
        await bot_app.start()
        await server.serve(
            host=server_host,
            port=server_port,
        )
        await bot_app.stop()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,  # type: ignore
        text="WOW! Hello!"
    )


async def accept(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,  # type: ignore
        text=f"Entry <{update.message.text}> is accepted"  # type: ignore
    )


if __name__ == "__main__":
    asyncio.run(main())
