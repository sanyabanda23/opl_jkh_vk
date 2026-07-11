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

from vkbottle import Bot as VKBot
from vkbottle.framework.labeler import BotLabeler
from vkbottle.bot import Message
from vkbottle.dispatch.rules.base import ABCRule
from vkbottle import CtxStorage, DocMessagesUploader

import mysql.connector as con
import utils, text, kb
from config import settings
from state import Info_pay_mon, Info_pay_year

vk_bot = VKBot(token=settings.BOT_TOKEN_VK)

ctx = CtxStorage()
driver_jkh = utils.SBOL()
# Создаём загрузчик документов
doc_uploader = DocMessagesUploader(vk_bot.api)

# Функция для проверки чата
class MyRule(ABCRule[Message]):
    async def check(self, event: Message) -> bool:
        # Здесь можно добавить свою логику проверки чата
        # Например, проверка ID чата
        if event.chat_id == 1 and event.from_id == 9028754:  # Замените на ID вашего чата
            return True
        return False

# Функция для хендлера payload. Аналог callback 
class PayloadABCRule(ABCRule[Message]):
    async def check(self, message: Message) -> bool:
        payload = message.payload
        if not payload:
            return False
        else:
            payload_dict = json.loads(payload)
        
        # Проверяем, что payload - это JSON
        if isinstance(payload_dict, dict):
            cmd_value = payload_dict.get("cmd")
            return cmd_value == self.cmd if cmd_value else False
        else:
            return False

    def __init__(self, cmd: str):
        self.cmd = cmd

    
@vk_bot.on.message(MyRule(), text="/start")
async def start_handler(message: Message):
    try:
        await vk_bot.state_dispenser.delete(message.peer_id)
    except KeyError:
        pass  # Состояние не найдено — игнорируем
    logger.info("Вызвано главное меню")
    await message.answer(text.hello_text, keyboard=kb.start_kb())

### Реакция на кнопку гравное меню
@vk_bot.on.message(MyRule(), PayloadABCRule('main_menu'))
async def main_menu(message: Message):
    try:
        await vk_bot.state_dispenser.delete(message.peer_id)
    except KeyError:
        pass  # Состояние не найдено — игнорируем
    driver_jkh.quit_driver()
    logger.info("Вызвано главное меню")
    await message.answer('Главное меню', keyboard=kb.start_kb())

@vk_bot.on.message(MyRule(), PayloadABCRule('main_menu_info'))
async def main_menu_info(message: Message):
    try:
        await vk_bot.state_dispenser.delete(message.peer_id)
    except KeyError:
        pass  # Состояние не найдено — игнорируем
    logger.info("Вызвано главное меню")
    await message.answer('Главное меню', keyboard=kb.start_kb())


### Формирование отчетов
@vk_bot.on.message(MyRule(), PayloadABCRule('info_pay_rek'))
async def vibor_info(message: Message):
    logger.debug(f"Вызвано меню отчетов. cmd={message.payload}")
    try:
        await vk_bot.state_dispenser.delete(message.peer_id)
    except KeyError:
        pass  # Состояние не найдено — игнорируем
    await message.answer(text.vibor_info, keyboard=kb.vibor_info_rek_kb())

@vk_bot.on.message(MyRule(), PayloadABCRule('info_rek'))
async def vibor_info_rek(message: Message):
    logger.debug(f"Информация о реквизитах. cmd={message.payload}")
    try:
        await vk_bot.state_dispenser.delete(message.peer_id)
    except KeyError:
        pass  # Состояние не найдено — игнорируем
    await message.answer('Выбери тип отчета о реквизитах', keyboard=kb.vibor_info_post_lsch_kb())

@vk_bot.on.message(MyRule(), PayloadABCRule('info_pay'))
async def vibor_info_pay(message: Message):
    logger.debug(f"Информация о платежах. cmd={message.payload}")
    try:
        await vk_bot.state_dispenser.delete(message.peer_id)
    except KeyError:
        pass  # Состояние не найдено — игнорируем
    await message.answer('Выбери тип отчета о платежах', keyboard=kb.vibor_info_pay())

@vk_bot.on.message(MyRule(), PayloadABCRule('info_pos'))
async def vibor_rek_pos_info(message: Message):
    logger.debug(f"Реквизиты поставщиков. cmd={message.payload}")
    try:
        await vk_bot.state_dispenser.delete(message.peer_id)
    except KeyError:
        pass  # Состояние не найдено — игнорируем
    await message.answer('Отчет формируется')
    utils.select_from_postav()
    doc = await doc_uploader.upload(
            file_source="postavshiki.pdf",
            peer_id=message.peer_id,
            )
    await message.answer('Отправляю вам отчет в формате PDF', attachment=doc)

@vk_bot.on.message(MyRule(), PayloadABCRule('info_lsch'))
async def vibor_rek_lsch_info(message: Message):
    logger.debug(f"Лицевые счета. cmd={message.payload}")
    try:
        await vk_bot.state_dispenser.delete(message.peer_id)
    except KeyError:
        pass  # Состояние не найдено — игнорируем
    await message.answer('Отчет формируется')
    utils.select_from_lsch()
    # Загружаем документ
    upload_start = time.time()
    doc = await doc_uploader.upload(
            file_source="l_sch.pdf",
            peer_id=message.peer_id,
        )
    upload_end = time.time()
    logger.debug(f"Загрузка файла: {upload_end - upload_start:.2f} сек")
    await message.answer('Отправляю вам отчет в формате PDF', attachment=doc)

@vk_bot.on.message(payload={"cmd": "info_pay_mon"})
async def info_pay_mon(message: Message):
    logger.debug(f"Лицевые счета. cmd={message.payload}")
    try:
        await vk_bot.state_dispenser.delete(message.peer_id)
    except KeyError:
        pass  # Состояние не найдено — игнорируем
    await message.answer(text.info_pay_mon)
    await vk_bot.state_dispenser.set(message.peer_id, Info_pay_mon.MON)

@vk_bot.on.message(state=Info_pay_mon.MON)
async def info_pay_mon_1(message: Message):
    data_mon = message.text
    await message.answer('Отчет формируется')
    summ = utils.select_from_pay_month(month=data_mon)
    doc = await doc_uploader.upload(
            file_source="month_pay.pdf",
            peer_id=message.peer_id,
        )
    await message.answer(f'Cумма платежей составила - {summ}')
    await message.answer('Отправляю вам отчет в формате PDF', attachment=doc)
    await vk_bot.state_dispenser.delete(message.peer_id)

@vk_bot.on.message(MyRule(), PayloadABCRule('info_pay_kf_kp'))
async def info_pay_year(message: Message):
    try:
        await vk_bot.state_dispenser.delete(message.peer_id)
    except KeyError:
        pass  # Состояние не найдено — игнорируем
    await message.answer('Выбери квартиру', reply_markup=kb.vibor_kv_info_kb())
    await vk_bot.state_dispenser.set(Info_pay_year.KF)

@vk_bot.on.message(payload={"cmd": "info_pay_mon"})
@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'dm', Info_pay_year.kf)
async def info_pay_year(call: CallbackQuery, state: FSMContext):
    await state.update_data(kf='dm')
    await call.message.edit_text('Выбери поставщика', reply_markup=kb_jkh.vibor_post_info_kb())
    await state.set_state(Info_pay_year.KP)

@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'pt', Info_pay_year.kf)
async def info_pay_year(call: CallbackQuery, state: FSMContext):
    await state.update_data(kf='pt')
    await call.message.edit_text('Выбери поставщика', reply_markup=kb_jkh.vibor_post_info_kb())
    await state.set_state(Info_pay_year.kp)

@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'fr', Info_pay_year.kf)
async def info_pay_year(call: CallbackQuery, state: FSMContext):
    await state.update_data(kf='fr')
    await call.message.edit_text('Выбери поставщика', reply_markup=kb_jkh.vibor_post_info_kb())
    await state.set_state(Info_pay_year.kp)

@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'in', Info_pay_year.kf)
async def info_pay_year(call: CallbackQuery, state: FSMContext):
    await state.update_data(kf='in')
    await call.message.edit_text('Выбери поставщика', reply_markup=kb_jkh.vibor_post_info_kb())
    await state.set_state(Info_pay_year.kp)

@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'gb', Info_pay_year.kp)
async def info_pay_year(call: CallbackQuery, state: FSMContext):
    await state.update_data(kp='gb')
    await call.message.answer(text_jkh.info_pay_year)
    await state.set_state(Info_pay_year.year)

@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'gz', Info_pay_year.kp)
async def info_pay_year(call: CallbackQuery, state: FSMContext):
    await state.update_data(kp='gz')
    await call.message.answer(text_jkh.info_pay_year)
    await state.set_state(Info_pay_year.year)

@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'kr', Info_pay_year.kp)
async def info_pay_year(call: CallbackQuery, state: FSMContext):
    await state.update_data(kp='kr')
    await call.message.answer(text_jkh.info_pay_year)
    await state.set_state(Info_pay_year.year)

@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'lt', Info_pay_year.kp)
async def info_pay_year(call: CallbackQuery, state: FSMContext):
    await state.update_data(kp='lt')
    await call.message.answer(text_jkh.info_pay_year)
    await state.set_state(Info_pay_year.year)

@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'wm', Info_pay_year.kp)
async def info_pay_year(call: CallbackQuery, state: FSMContext):
    await state.update_data(kp='wm')
    await call.message.answer(text_jkh.info_pay_year)
    await state.set_state(Info_pay_year.year)

@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'ykd', Info_pay_year.kp)
async def info_pay_year(call: CallbackQuery, state: FSMContext):
    await state.update_data(kp='ykd')
    await call.message.answer(text_jkh.info_pay_year)
    await state.set_state(Info_pay_year.year)

@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'ykf', Info_pay_year.kp)
async def info_pay_year(call: CallbackQuery, state: FSMContext):
    await state.update_data(kp='ykf')
    await call.message.answer(text_jkh.info_pay_year)
    await state.set_state(Info_pay_year.year)

@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'yki', Info_pay_year.kp)
async def info_pay_year(call: CallbackQuery, state: FSMContext):
    await state.update_data(kp='yki')
    await call.message.answer(text_jkh.info_pay_year)
    await state.set_state(Info_pay_year.year)

@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'wt', Info_pay_year.kp)
async def info_pay_year(call: CallbackQuery, state: FSMContext):
    await state.update_data(kp='wt')
    await call.message.answer(text_jkh.info_pay_year)
    await state.set_state(Info_pay_year.year)

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text, Info_pay_year.year)
async def info_pay_year(msg: Message, state: FSMContext):        
    await state.update_data(year=msg.text)
    data = await state.get_data()
    await msg.answer('Отчет формируется')
    utils_jkh.select_from_pay_year(kf=data.get('kf'), kp=data.get('kp'), year=data.get('year'))
    doc = FSInputFile('year_pay.pdf')
    await msg.answer_photo(photo=doc)
    await b.send_document(msg.chat.id, document=doc)  
    await msg.answer('Отправляю вам отчет в формате PDF')
    await state.clear()
