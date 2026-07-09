import logging
# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

from handlers import vk_bot

def run_bot():
    """Асинхронная функция запуска бота"""
    logger.info("Запуск VK‑бота...")
    try:
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