import asyncio
import logging
from vkbottle import Bot as VKBot
from vkbottle.bot import Message
from vkbottle import BuiltinStateDispenser
# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

from config import settings
from handlers import router

# Создание VK‑бота
vk_bot = VKBot(token=settings.BOT_TOKEN_VK)
vk_bot.state_dispenser = BuiltinStateDispenser()

def run_bot():
    """Асинхронная функция запуска бота"""
    logger.info("Запуск VK‑бота...")
    try:
        # Загружаем обработчики
        vk_bot.labeler.load(router)
        logger.info("Обработчики загружены")

        # Запускаем polling — vkbottle сам управляет event loop
        vk_bot.run_forever()
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
    finally:
        logger.info("VK‑бот остановлен")

if __name__ == "__main__":
    # Один-единственный запуск event loop на всё приложение
    run_bot()