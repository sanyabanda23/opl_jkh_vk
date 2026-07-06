import asyncio
import time
import json
import logging
# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

from vkbottle.framework.labeler import BotLabeler
from vkbottle.bot import Message
from vkbottle.dispatch.rules.base import ABCRule
from vkbottle import CtxStorage, DocMessagesUploader

import mysql.connector as con
import utils, text, kb
from config import settings

# Создаём Labeler (аналог Dispatcher в aiogram)
router = BotLabeler()
# это хранилище для временного сохранения данных в рамках диалога
ctx = CtxStorage()