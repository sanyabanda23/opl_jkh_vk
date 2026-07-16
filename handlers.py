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
from state import (Info_pay_mon, Info_pay_year, Vhod, Opl_kr_dm, 
                   Opl_kr_fr, Opl_kr_in, Opl_kr_pt, Opl_gb_dm, Opl_gb_in,
                   Opl_yk_dm, Opl_yk_fr, Opl_yk_in, Opl_wm_in, Opl_wt_dm,
                   Opl_wt_in, Opl_wt_pt, Opl_gz_dm, Opl_gz_fr, Opl_lt_dm,
                   Opl_lt_pt)

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
    logger.info(
            "DEBUG CATCH-ALL: peer_id=%d, chat_id=%r, from_id=%d, text=%r, payload=%r",
            message.peer_id,
            getattr(message, "chat_id", None),
            message.from_id,
            message.text,
            message.payload,
        )
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
    await message.answer('⏳ Отчет формируется')
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
    await message.answer('Выбери квартиру', keyboard=kb.vibor_kv_info_kb())
    await vk_bot.state_dispenser.set(message.peer_id, Info_pay_year.KF)

@vk_bot.on.message(MyRule(), state=Info_pay_year.KF)
async def info_pay_year(message: Message):
    payload = json.loads(message.payload)
    cmd = payload["cmd"]
    if not cmd.startswith("kf_"):
        await message.answer('Выбери квартиру из списка')
        return
    kf = cmd.split("_")[1]
    logger.debug(f"Выбрана квартира с ключом: {kf}")
    ctx.set("kf", kf)
    await message.answer('Выбери поставщика', keyboard=kb.vibor_post_info_kb())
    await vk_bot.state_dispenser.set(message.peer_id, Info_pay_year.KP)

@vk_bot.on.message(MyRule(), state=Info_pay_year.KP)
async def info_pay_year(message: Message):
    payload = json.loads(message.payload)
    cmd = payload["cmd"]
    if not cmd.startswith("kp_"):
        return
    kp = cmd.split("_")[1]
    logger.debug(f"Выбран поставщик с ключом: {kp}")
    ctx.set("kp", kp)
    await message.answer(text.info_pay_year)
    await vk_bot.state_dispenser.set(message.peer_id, Info_pay_year.YEAR)

@vk_bot.on.message(MyRule(), state=Info_pay_year.YEAR)
async def info_pay_year(message: Message):        
    year = message.text
    kp = ctx.get('kp')
    kf = ctx.get('kf')
    await message.answer('⏳ Отчет формируется')
    utils.select_from_pay_year(kf=kf, kp=kp, year=year)
    doc = await doc_uploader.upload(
            file_source="year_pay.pdf",
            peer_id=message.peer_id,
        )
    await message.answer('Отправляю вам отчет в формате PDF', attachment=doc)
    await vk_bot.state_dispenser.delete(message.peer_id)

### Вход в Сбербанк оннлайнн
@vk_bot.on.message(MyRule(), PayloadABCRule('start_sbol'))
async def start_vhod_sbol(message: Message):
    try:
        await vk_bot.state_dispenser.delete(message.peer_id)
    except KeyError:
        pass  # Состояние не найдено — игнорируем
    await message.answer('Начата процедура входа')
    if driver_jkh.initialize_driver():
        driver_jkh.open_website(settings.URL_vhod)
        await message.answer('Введите пароль из СМС-сообщения')
        if driver_jkh.vhod_tel_parol():
            await vk_bot.state_dispenser.set(message.peer_id, Vhod.SMS_PASWORD)
        else:
            driver_jkh.close_driver()
            await message.answer(text.falling_vhod, keyboard=kb.start_kb())

@vk_bot.on.message(MyRule(), state=Vhod.SMS_PASWORD)
async def input_sms(message: Message):
    pasword = message.text
    await message.answer('Код из СМС принят')
    if driver_jkh.vvod_is_sms(pasword):
        await message.answer(text.success_vhod, keyboard=kb.vibor_kv_kb())
        await vk_bot.state_dispenser.delete(message.peer_id)
    else:
        await vk_bot.state_dispenser.delete(message.peer_id)
        driver_jkh.close_driver()
        await message.answer(text.falling_vhod, keyboard=kb.start_kb())

### Реакция на кнопки в клавиатуре выбор квартиры
@vk_bot.on.message(MyRule(), PayloadABCRule('dm'))
async def opl_zkh_dm(message: Message):
    try:
        await vk_bot.state_dispenser.delete(message.peer_id)
    except KeyError:
        pass  # Состояние не найдено — игнорируем
    connection = con.connect(
      host=settings.con_sql[0],
      user=settings.con_sql[1],
      password=settings.con_sql[2],
      database=settings.con_sql[3]
    )
    cursor = connection.cursor()
    select = ''' SELECT name FROM flat_ls WHERE kf = 'dm' '''
    cursor.execute(select)
    data = cursor.fetchall()
    connection.commit()
    print('Данные получены')
    cursor.close()
    connection.close()
    await message.answer(text.oplata_za.format(data[0][0]), keyboard=kb.opl_zkh_dm())

@vk_bot.on.message(MyRule(), PayloadABCRule('pt'))
async def opl_zkh_dm(message: Message):
    try:
        await vk_bot.state_dispenser.delete(message.peer_id)
    except KeyError:
        pass  # Состояние не найдено — игнорируем
    connection = con.connect(
      host=settings.con_sql[0],
      user=settings.con_sql[1],
      password=settings.con_sql[2],
      database=settings.con_sql[3]
    )
    cursor = connection.cursor()
    select = ''' SELECT name FROM flat_ls WHERE kf = 'pt' '''
    cursor.execute(select)
    data = cursor.fetchall()
    connection.commit()
    print('Данные получены')
    cursor.close()
    connection.close()
    await message.answer(text.oplata_za.format(data[0][0]), keyboard=kb.opl_zkh_pt())

@vk_bot.on.message(MyRule(), PayloadABCRule('fr'))
async def opl_zkh_dm(message: Message):
    try:
        await vk_bot.state_dispenser.delete(message.peer_id)
    except KeyError:
        pass  # Состояние не найдено — игнорируем
    connection = con.connect(
      host=settings.con_sql[0],
      user=settings.con_sql[1],
      password=settings.con_sql[2],
      database=settings.con_sql[3]
    )
    cursor = connection.cursor()
    select = ''' SELECT name FROM flat_ls WHERE kf = 'fr' '''
    cursor.execute(select)
    data = cursor.fetchall()
    connection.commit()
    print('Данные получены')
    cursor.close()
    connection.close()
    await message.answer(text.oplata_za.format(data[0][0]), keyboard=kb.opl_zkh_fr())

@vk_bot.on.message(MyRule(), PayloadABCRule('in'))
async def opl_zkh_dm(message: Message):
    try:
        await vk_bot.state_dispenser.delete(message.peer_id)
    except KeyError:
        pass  # Состояние не найдено — игнорируем
    connection = con.connect(
      host=settings.con_sql[0],
      user=settings.con_sql[1],
      password=settings.con_sql[2],
      database=settings.con_sql[3]
    )
    cursor = connection.cursor()
    select = ''' SELECT name FROM flat_ls WHERE kf = 'in' '''
    cursor.execute(select)
    data = cursor.fetchall()
    connection.commit()
    print('Данные получены')
    cursor.close()
    connection.close()
    await message.answer(text.oplata_za.format(data[0][0]), keyboard=kb.opl_zkh_in())

###### Реакция кнопок в клавиатуре оплата ЖКХ
# Обратно для выбора квартиры
@vk_bot.on.message(MyRule(), PayloadABCRule('vibor_kv_menu')) 
async def back_vibor_kv(message: Message):
    try:
        await vk_bot.state_dispenser.delete(message.peer_id)
    except KeyError:
        pass  # Состояние не найдено — игнорируем
    await message.answer('Выбери квартиру для оплаты услуг ЖКХ', keyboard=kb.vibor_kv_kb())

### Оплата кап ремонт Петровская
@vk_bot.on.message(MyRule(), PayloadABCRule('krpt'))
async def opl_kr_pt_preparetion(message: Message):
    try:
        await vk_bot.state_dispenser.delete(message.peer_id)
    except KeyError:
        pass  # Состояние не найдено — игнорируем
    connection = con.connect(
      host=settings.con_sql[0],
      user=settings.con_sql[1],
      password=settings.con_sql[2],
      database=settings.con_sql[3]
    )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, kap_rem, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'pt' AND postavshiki.kp = 'kr' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        summ = str(data[0][2])
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await message.answer(text.preparation_pay)
    input_value = driver_jkh.oplata_kr(inn=inn, l_sch=l_sch, summ=summ)
    if input_value[0] is True:
        await message.answer(text.question_pay.format(input_value[1]), keyboard=kb.yes_no_kb())
        await vk_bot.state_dispenser.set(message.peer_id, Opl_kr_pt.PREPARATION)
    else:
        await message.answer(text.falling_pay, keyboard=kb.opl_zkh_pt())

@vk_bot.on.message(MyRule(), PayloadABCRule('yes'), state=Opl_kr_pt.PREPARATION)
async def opl_kr_pt(message: Message):        
    if driver_jkh.oplata_kr_yes():    
        rekviz = utils.get_info_from_chek()
        if rekviz:
            num = rekviz[0]
            date = rekviz[1]
            usl = rekviz[2]
            card = rekviz[3]
            summ = rekviz[4]
            pokaz = rekviz[5]
            chek = f'*******Чек по операции*******\n' \
                   f'Дата и время платежа\n' \
                   f'{date:>45}\n' \
                   f'Идентификатор платежа\n' \
                   f'{num:>45}\n' \
                   f'Вид услуги\n' \
                   f'{usl:>30}\n' \
                   f'Показания счетчика\n' \
                   f'{pokaz:>45}\n' \
                   f'Способ оплаты\n' \
                   f'{card:>30} \n' \
                   f'Сумма платежа\n' \
                   f'{summ:>45} руб.'
            date_time_sql = utils.form_date(date)
            summ_sq = str(summ).replace(',', '.')
            summ_sql = str(summ_sq).replace(' ', '')
            connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
            cursor = connection.cursor()
            try:
                new_pay = (num, date_time_sql, usl, card, summ_sql, 'pt', 'kr', pokaz)
                request_to_insert_data = ''' INSERT INTO pay (num, date, usl, card, summ, kf, kp, pokaz) VALUES (%s, %s, %s, %s, %s, %s, %s, %s); '''
                cursor.execute(request_to_insert_data, new_pay)
                connection.commit()
                print('Данные введены')
            except Exception as e:
                # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
                connection.rollback()
                print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")
            finally:
                # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
                cursor.close()
                connection.close()
            await message.answer(chek, keyboard=kb.opl_zkh_pt())
            await vk_bot.state_dispenser.delete(message.peer_id)
        else:
            print('Данные из чека не извлечены')
            await message.answer(text.falling_chek, keyboard=kb.opl_zkh_pt())
            await vk_bot.state_dispenser.delete(message.peer_id)    
    else:
        await message.answer(text.falling_pay, keyboard=kb.opl_zkh_pt())
        await vk_bot.state_dispenser.delete(message.peer_id)

@vk_bot.on.message(MyRule(), PayloadABCRule('no'), state=Opl_kr_pt.PREPARATION)
async def opl_kr_pt(message: Message):        
    await message.answer('Укажи сумму, которую собираешься оплатить.')
    await vk_bot.state_dispenser.set(message.peer_id, Opl_kr_pt.SUMM)

@vk_bot.on.message(MyRule(), state=Opl_kr_pt.SUMM)
async def opl_kr_pt(message: Message):        
    data_summ = message.text
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, kap_rem, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'pt' AND postavshiki.kp = 'kr' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await message.answer(text.preparation_pay)
    input_value = driver_jkh.oplata_kr(inn=inn, l_sch=l_sch, summ=data_summ)
    if input_value[0] is True:
        await message.answer(text.question_pay.format(input_value[1]), keyboard=kb.yes_no_kb())
        await vk_bot.state_dispenser.set(message.peer_id, Opl_kr_pt.PREPARATION)
    else:
        await message.answer(text.falling_pay, keyboard=kb.opl_zkh_pt())

# Оплата кап ремонт Фрунзе
@vk_bot.on.message(MyRule(), PayloadABCRule('krfr'))
async def opl_kr_fr_preparetion(message: Message):
    try:
        await vk_bot.state_dispenser.delete(message.peer_id)
    except KeyError:
        pass  # Состояние не найдено — игнорируем
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, kap_rem, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'fr' AND postavshiki.kp = 'kr' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        summ = str(data[0][2])
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await message.answer(text.preparation_pay)
    input_value = driver_jkh.oplata_kr(inn=inn, l_sch=l_sch, summ=summ)
    if input_value[0] is True:
        await message.answer(text.question_pay.format(input_value[1]), keyboard=kb.yes_no_kb())
        await vk_bot.state_dispenser.set(message.peer_id, Opl_kr_fr.PREPARATION)
    else:
        await message.answer(text.falling_pay, keyboard=kb.opl_zkh_fr())

@vk_bot.on.message(MyRule(), PayloadABCRule('no'), state=Opl_kr_fr.PREPARATION)
async def opl_kr_fr(message: Message):        
    await message.answer('Укажи сумму, которую собираешься оплатить.')
    await vk_bot.state_dispenser.set(message.peer_id, Opl_kr_fr.SUMM)

@vk_bot.on.message(MyRule(), PayloadABCRule('yes'), state=Opl_kr_fr.PREPARATION)
async def opl_kr_fr(message: Message):
    if driver_jkh.oplata_kr_yes():    
        rekviz = utils.get_info_from_chek()
        if rekviz:
            num = rekviz[0]
            date = rekviz[1]
            usl = rekviz[2]
            card = rekviz[3]
            summ = rekviz[4]
            pokaz = rekviz[5]
            chek = f'*******Чек по операции*******\n' \
                   f'Дата и время платежа\n' \
                   f'{date:>45}\n' \
                   f'Идентификатор платежа\n' \
                   f'{num:>45}\n' \
                   f'Вид услуги\n' \
                   f'{usl:>30}\n' \
                   f'Показания счетчика\n' \
                   f'{pokaz:>45}\n' \
                   f'Способ оплаты\n' \
                   f'{card:>30} \n' \
                   f'Сумма платежа\n' \
                   f'{summ:>45} руб.'
            date_time_sql = utils.form_date(date)
            summ_sq = str(summ).replace(',', '.')
            summ_sql = str(summ_sq).replace(' ', '')
            connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
            cursor = connection.cursor()
            try:
                new_pay = (num, date_time_sql, usl, card, summ_sql, 'fr', 'kr', pokaz)
                request_to_insert_data = ''' INSERT INTO pay (num, date, usl, card, summ, kf, kp, pokaz) VALUES (%s, %s, %s, %s, %s, %s, %s, %s); '''
                cursor.execute(request_to_insert_data, new_pay)
                connection.commit()
                print('Данные введены')
            except Exception as e:
                # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
                connection.rollback()
                print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")
            finally:
                # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
                cursor.close()
                connection.close()
            await message.answer(chek, keyboard=kb.opl_zkh_fr())
            await vk_bot.state_dispenser.delete(message.peer_id)
        else:
            print('Данные из чека не извлечены')
            await message.answer(text.falling_chek, keyboard=kb.opl_zkh_fr())
            await vk_bot.state_dispenser.delete(message.peer_id)    
    else:
        await message.answer(text.falling_pay, keyboard=kb.opl_zkh_fr())
        await vk_bot.state_dispenser.delete(message.peer_id)

@vk_bot.on.message(MyRule(), state=Opl_kr_fr.SUMM)
async def opl_kr_fr(message: Message):        
    data_summ = message.text
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, kap_rem, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'fr' AND postavshiki.kp = 'kr' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await message.answer(text.preparation_pay)
    input_value = driver_jkh.oplata_kr(inn=inn, l_sch=l_sch, summ=data_summ)
    if input_value[0] is True:
        await message.answer(text.question_pay.format(input_value[1]), keyboard=kb.yes_no_kb())
        await vk_bot.state_dispenser.set(message.peer_id, Opl_kr_fr.PREPARATION)
    else:
        await message.answer(text.falling_pay, keyboard=kb.opl_zkh_fr())

# Оплата кап ремонт Инструментальная
@vk_bot.on.message(MyRule(), PayloadABCRule('krin'))
async def opl_kr_in_preparetion(message: Message):
    try:
        await vk_bot.state_dispenser.delete(message.peer_id)
    except KeyError:
        pass  # Состояние не найдено — игнорируем
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, kap_rem, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'in' AND postavshiki.kp = 'kr' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        summ = str(data[0][2])
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await message.answer(text.preparation_pay)
    input_value = driver_jkh.oplata_kr(inn=inn, l_sch=l_sch, summ=summ)
    if input_value[0] is True:
        await message.answer(text.question_pay.format(input_value[1]), keyboard=kb.yes_no_kb())
        await vk_bot.state_dispenser.set(message.peer_id, Opl_kr_in.PREPARATION)
    else:
        await message.answer(text.falling_pay, keyboard=kb.opl_zkh_in())

@vk_bot.on.message(MyRule(), PayloadABCRule('yes'), state=Opl_kr_in.PREPARATION)
async def opl_kr_in(message: Message):
    if driver_jkh.oplata_kr_yes():    
        rekviz = utils.get_info_from_chek()
        if rekviz:
            num = rekviz[0]
            date = rekviz[1]
            usl = rekviz[2]
            card = rekviz[3]
            summ = rekviz[4]
            pokaz = rekviz[5]
            chek = f'*******Чек по операции*******\n' \
                   f'Дата и время платежа\n' \
                   f'{date:>45}\n' \
                   f'Идентификатор платежа\n' \
                   f'{num:>45}\n' \
                   f'Вид услуги\n' \
                   f'{usl:>30}\n' \
                   f'Показания счетчика\n' \
                   f'{pokaz:>45}\n' \
                   f'Способ оплаты\n' \
                   f'{card:>30} \n' \
                   f'Сумма платежа\n' \
                   f'{summ:>45} руб.'
            date_time_sql = utils.form_date(date)
            summ_sq = str(summ).replace(',', '.')
            summ_sql = str(summ_sq).replace(' ', '')
            connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
            cursor = connection.cursor()
            try:
                new_pay = (num, date_time_sql, usl, card, summ_sql, 'in', 'kr', pokaz)
                request_to_insert_data = ''' INSERT INTO pay (num, date, usl, card, summ, kf, kp, pokaz) VALUES (%s, %s, %s, %s, %s, %s, %s, %s); '''
                cursor.execute(request_to_insert_data, new_pay)
                connection.commit()
                print('Данные введены')
            except Exception as e:
                # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
                connection.rollback()
                print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")
            finally:
                # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
                cursor.close()
                connection.close()
            await message.answer(chek, keyboard=kb.opl_zkh_in())
            await vk_bot.state_dispenser.delete(message.peer_id)
        else:
            print('Данные из чека не извлечены')
            await message.answer(text.falling_chek, keyboard=kb.opl_zkh_in())
            await vk_bot.state_dispenser.delete(message.peer_id)    
    else:
        await message.answer(text.falling_pay, keyboard=kb.opl_zkh_in())
        await vk_bot.state_dispenser.delete(message.peer_id)

@vk_bot.on.message(MyRule(), PayloadABCRule('no'), state=Opl_kr_in.PREPARATION)
async def opl_kr_in(message: Message):
    await message.answer('Укажи сумму, которую собираешься оплатить.')
    await vk_bot.state_dispenser.set(message.peer_id, Opl_kr_in.SUMM)

@vk_bot.on.message(MyRule(), state=Opl_kr_in.SUMM)
async def opl_kr_in(message: Message):
    data_summ = message.text
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, kap_rem, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'in' AND postavshiki.kp = 'kr' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await message.answer(text.preparation_pay)
    input_value = driver_jkh.oplata_kr(inn=inn, l_sch=l_sch, summ=data_summ)
    if input_value[0] is True:
        await message.answer(text.question_pay.format(input_value[1]), keyboard=kb.yes_no_kb())
        await vk_bot.state_dispenser.set(message.peer_id, Opl_kr_in.PREPARATION)
    else:
        await message.answer(text.falling_pay, keyboard=kb.opl_zkh_in())

# Оплата кап ремонт Дом
@vk_bot.on.message(MyRule(), PayloadABCRule('krdm'))
async def opl_kr_dm_preparetion(message: Message):
    try:
        await vk_bot.state_dispenser.delete(message.peer_id)
    except KeyError:
        pass  # Состояние не найдено — игнорируем
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, kap_rem, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'dm' AND postavshiki.kp = 'kr' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        summ = str(data[0][2])
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await message.answer(text.preparation_pay)
    input_value = driver_jkh.oplata_kr_dm(inn=inn, l_sch=l_sch, summ=summ)
    if input_value[0] is True:
        await message.answer(text.question_pay.format(input_value[1]), keyboard=kb.yes_no_kb())
        await vk_bot.state_dispenser.set(message.peer_id, Opl_kr_dm.PREPARATION)
    else:
        await message.answer(text.falling_pay, keyboard=kb.opl_zkh_dm())

@vk_bot.on.message(MyRule(), PayloadABCRule('yes'), state=Opl_kr_dm.PREPARATION)
async def opl_kr_dm(message: Message):
    if driver_jkh.oplata_kr_yes():    
        rekviz = utils.get_info_from_chek()
        if rekviz:
            num = rekviz[0]
            date = rekviz[1]
            usl = rekviz[2]
            card = rekviz[3]
            summ = rekviz[4]
            pokaz = rekviz[5]
            chek = f'*******Чек по операции*******\n' \
                   f'Дата и время платежа\n' \
                   f'{date:>45}\n' \
                   f'Идентификатор платежа\n' \
                   f'{num:>45}\n' \
                   f'Вид услуги\n' \
                   f'{usl:>30}\n' \
                   f'Показания счетчика\n' \
                   f'{pokaz:>45}\n' \
                   f'Способ оплаты\n' \
                   f'{card:>30} \n' \
                   f'Сумма платежа\n' \
                   f'{summ:>45} руб.'
            date_time_sql = utils.form_date(date)
            summ_sq = str(summ).replace(',', '.')
            summ_sql = str(summ_sq).replace(' ', '')
            connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
            cursor = connection.cursor()
            try:
                new_pay = (num, date_time_sql, usl, card, summ_sql, 'dm', 'kr', pokaz)
                request_to_insert_data = ''' INSERT INTO pay (num, date, usl, card, summ, kf, kp, pokaz) VALUES (%s, %s, %s, %s, %s, %s, %s, %s); '''
                cursor.execute(request_to_insert_data, new_pay)
                connection.commit()
                print('Данные введены')
            except Exception as e:
                # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
                connection.rollback()
                print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")
            finally:
                # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
                cursor.close()
                connection.close()
            await message.answer(chek, keyboard=kb.opl_zkh_dm())
            await vk_bot.state_dispenser.delete(message.peer_id)
        else:
            print('Данные из чека не извлечены')
            await message.answer(text.falling_chek, keyboard=kb.opl_zkh_dm())
            await vk_bot.state_dispenser.delete(message.peer_id)    
    else:
        await message.answer(text.falling_pay, keyboard=kb.opl_zkh_dm())
        await vk_bot.state_dispenser.delete(message.peer_id)

@vk_bot.on.message(MyRule(), PayloadABCRule('no'), state=Opl_kr_dm.PREPARATION)
async def opl_kr_dm(message: Message):
    await message.answer('Укажи сумму, которую собираешься оплатить.')
    await vk_bot.state_dispenser.set(message.peer_id, Opl_kr_dm.SUMM)

@vk_bot.on.message(MyRule(), state=Opl_kr_dm.SUMM)
async def opl_kr_dm(message: Message):
    data_summ = message.text
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, kap_rem, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'dm' AND postavshiki.kp = 'kr' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await message.answer(text.preparation_pay)
    input_value = driver_jkh.oplata_kr(inn=inn, l_sch=l_sch, summ=data_summ)
    if input_value[0] is True:
        await message.answer(text.question_pay.format(input_value[1]), keyboard=kb.yes_no_kb())
        await vk_bot.state_dispenser.set(message.peer_id, Opl_kr_dm.PREPARATION)
    else:
        await message.answer(text.falling_pay, keyboard=kb.opl_zkh_dm())

### Оплата вывоз ТКО Дом
@vk_bot.on.message(MyRule(), PayloadABCRule('gbdm'))
async def opl_gb_dm_preparetion(message: Message):
    try:
        await vk_bot.state_dispenser.delete(message.peer_id)
    except KeyError:
        pass  # Состояние не найдено — игнорируем
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, garbage, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'dm' AND postavshiki.kp = 'gb' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        summ = str(data[0][2])
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await message.answer(text.preparation_pay)
    input_value = driver_jkh.oplata_gb(inn=inn, l_sch=l_sch, summ=summ)
    if input_value[0] is True:
        await message.answer(text.question_pay.format(input_value[1]), keyboard=kb.yes_no_kb())
        await vk_bot.state_dispenser.set(message.peer_id, Opl_gb_dm.PREPARATION)
    else:
        await message.answer(text.falling_pay, keyboard=kb.opl_zkh_dm())

@vk_bot.on.message(MyRule(), PayloadABCRule('yes'), state=Opl_gb_dm.PREPARATION)
async def opl_gb_dm(message: Message):
    if driver_jkh.oplata_gb_yes():    
        rekviz = utils.get_info_from_chek()
        if rekviz:
            num = rekviz[0]
            date = rekviz[1]
            usl = rekviz[2]
            card = rekviz[3]
            summ = rekviz[4]
            pokaz = rekviz[5]
            chek = f'*******Чек по операции*******\n' \
                   f'Дата и время платежа\n' \
                   f'{date:>45}\n' \
                   f'Идентификатор платежа\n' \
                   f'{num:>45}\n' \
                   f'Вид услуги\n' \
                   f'{usl:>30}\n' \
                   f'Показания счетчика\n' \
                   f'{pokaz:>45}\n' \
                   f'Способ оплаты\n' \
                   f'{card:>30} \n' \
                   f'Сумма платежа\n' \
                   f'{summ:>45} руб.'
            date_time_sql = utils.form_date(date)
            summ_sq = str(summ).replace(',', '.')
            summ_sql = str(summ_sq).replace(' ', '')
            connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
            cursor = connection.cursor()
            try:
                new_pay = (num, date_time_sql, usl, card, summ_sql, 'dm', 'gb', pokaz)
                request_to_insert_data = ''' INSERT INTO pay (num, date, usl, card, summ, kf, kp, pokaz) VALUES (%s, %s, %s, %s, %s, %s, %s, %s); '''
                cursor.execute(request_to_insert_data, new_pay)
                connection.commit()
                print('Данные введены')
            except Exception as e:
                # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
                connection.rollback()
                print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")
            finally:
                # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
                cursor.close()
                connection.close()
            await message.answer(chek, keyboard=kb.opl_zkh_dm())
            await vk_bot.state_dispenser.delete(message.peer_id)
        else:
            print('Данные из чека не извлечены')
            await message.answer(text.falling_chek, keyboard=kb.opl_zkh_dm())
            await vk_bot.state_dispenser.delete(message.peer_id)    
    else:
        await message.answer(text.falling_pay, keyboard=kb.opl_zkh_dm())
        await vk_bot.state_dispenser.delete(message.peer_id)

@vk_bot.on.message(MyRule(), PayloadABCRule('no'), state=Opl_gb_dm.PREPARATION)
async def opl_gb_dm(message: Message):
    await message.answer('Укажи сумму, которую собираешься оплатить.')
    await vk_bot.state_dispenser.set(message.peer_id, Opl_gb_dm.SUMM)

@vk_bot.on.message(MyRule(), state=Opl_gb_dm.SUMM)
async def opl_gb_dm(message: Message):
    data_summ = message.text
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, garbage, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'dm' AND postavshiki.kp = 'gb' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await message.answer(text.preparation_pay)
    input_value = driver_jkh.oplata_gb(inn=inn, l_sch=l_sch, summ=data_summ)
    if input_value[0] is True:
        await message.answer(text.question_pay.format(input_value[1]), keyboard=kb.yes_no_kb())
        await vk_bot.state_dispenser.set(message.peer_id, Opl_gb_dm.PREPARATION)
    else:
        await message.answer(text.falling_pay, keyboard=kb.opl_zkh_dm())

### Оплата вывоз ТКО Инструментальная
@vk_bot.on.message(MyRule(), PayloadABCRule('gbin'))
async def opl_gb_in_preparetion(message: Message):
    try:
        await vk_bot.state_dispenser.delete(message.peer_id)
    except KeyError:
        pass  # Состояние не найдено — игнорируем
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, garbage, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'in' AND postavshiki.kp = 'gb' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        summ = str(data[0][2])
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await message.answer(text.preparation_pay)
    input_value = driver_jkh.oplata_gb(inn=inn, l_sch=l_sch, summ=summ)
    if input_value[0] is True:
        await message.answer(text.question_pay.format(input_value[1]), keyboard=kb.yes_no_kb())
        await vk_bot.state_dispenser.set(message.peer_id, Opl_gb_in.PREPARATION)
    else:
        await message.answer(text.falling_pay, keyboard=kb.opl_zkh_in())

@vk_bot.on.message(MyRule(), PayloadABCRule('yes'), state=Opl_gb_in.PREPARATION)
async def opl_gb_in(message: Message):
    if driver_jkh.oplata_gb_yes():    
        rekviz = utils.get_info_from_chek()
        if rekviz:
            num = rekviz[0]
            date = rekviz[1]
            usl = rekviz[2]
            card = rekviz[3]
            summ = rekviz[4]
            pokaz = rekviz[5]
            chek = f'*******Чек по операции*******\n' \
                   f'Дата и время платежа\n' \
                   f'{date:>45}\n' \
                   f'Идентификатор платежа\n' \
                   f'{num:>45}\n' \
                   f'Вид услуги\n' \
                   f'{usl:>30}\n' \
                   f'Показания счетчика\n' \
                   f'{pokaz:>45}\n' \
                   f'Способ оплаты\n' \
                   f'{card:>30} \n' \
                   f'Сумма платежа\n' \
                   f'{summ:>45} руб.'
            date_time_sql = utils.form_date(date)
            summ_sq = str(summ).replace(',', '.')
            summ_sql = str(summ_sq).replace(' ', '')
            connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
            cursor = connection.cursor()
            try:
                new_pay = (num, date_time_sql, usl, card, summ_sql, 'in', 'gb', pokaz)
                request_to_insert_data = ''' INSERT INTO pay (num, date, usl, card, summ, kf, kp, pokaz) VALUES (%s, %s, %s, %s, %s, %s, %s, %s); '''
                cursor.execute(request_to_insert_data, new_pay)
                connection.commit()
                print('Данные введены')
            except Exception as e:
                # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
                connection.rollback()
                print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")
            finally:
                # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
                cursor.close()
                connection.close()
            await message.answer(chek, keyboard=kb.opl_zkh_in())
            await vk_bot.state_dispenser.delete(message.peer_id)
        else:
            print('Данные из чека не извлечены')
            await message.answer(text.falling_chek, keyboard=kb.opl_zkh_in())
            await vk_bot.state_dispenser.delete(message.peer_id)    
    else:
        await message.answer(text.falling_pay, keyboard=kb.opl_zkh_in())
        await vk_bot.state_dispenser.delete(message.peer_id)

@vk_bot.on.message(MyRule(), PayloadABCRule('no'), state=Opl_gb_in.PREPARATION)
async def opl_gb_dm(message: Message):
    await message.answer('Укажи сумму, которую собираешься оплатить.')
    await vk_bot.state_dispenser.set(message.peer_id, Opl_gb_in.SUMM)

@vk_bot.on.message(MyRule(), state=Opl_gb_in.SUMM)
async def opl_gb_dm(message: Message):
    data_summ = message.text
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, garbage, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'in' AND postavshiki.kp = 'gb' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await message.answer(text.preparation_pay)
    input_value = driver_jkh.oplata_gb(inn=inn, l_sch=l_sch, summ=data_summ)
    if input_value[0] is True:
        await message.answer(text.question_pay.format(input_value[1]), keyboard=kb.yes_no_kb())
        await vk_bot.state_dispenser.set(message.peer_id, Opl_gb_in.PREPARATION)
    else:
        await message.answer(text.falling_pay, keyboard=kb.opl_zkh_in())

### Оплата УК дом
@vk_bot.on.message(MyRule(), PayloadABCRule('ykdm'))
async def opl_yk_dm_preparetion(message: Message):
    try:
        await vk_bot.state_dispenser.delete(message.peer_id)
    except KeyError:
        pass  # Состояние не найдено — игнорируем
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, yk, schet, bik, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'dm' AND postavshiki.kp = 'ykd' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        schet = data[0][2]
        bik = data[0][3]
        summ = str(data[0][4])
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await message.answer(text.preparation_pay)
    input_value = driver_jkh.oplata_yk_dm(inn=inn, l_sch=l_sch, schet=schet, bik=bik, summ=summ)
    if input_value[0] is True:
        await message.answer(text.question_pay.format(input_value[1]), keyboard=kb.yes_no_kb())
        await vk_bot.state_dispenser.set(message.peer_id, Opl_yk_dm.PREPARATION)
    else:
        await message.answer(text.falling_pay, keyboard=kb.opl_zkh_dm())

@vk_bot.on.message(MyRule(), PayloadABCRule('yes'), state=Opl_yk_dm.PREPARATION)
async def opl_yk_dm(message: Message):
    if driver_jkh.oplata_yk_dm_yes():    
        rekviz = utils.get_info_from_chek()
        if rekviz:
            num = rekviz[0]
            date = rekviz[1]
            usl = rekviz[2]
            card = rekviz[3]
            summ = rekviz[4]
            pokaz = rekviz[5]
            chek = f'*******Чек по операции*******\n' \
                   f'Дата и время платежа\n' \
                   f'{date:>45}\n' \
                   f'Идентификатор платежа\n' \
                   f'{num:>45}\n' \
                   f'Вид услуги\n' \
                   f'{usl:>30}\n' \
                   f'Показания счетчика\n' \
                   f'{pokaz:>45}\n' \
                   f'Способ оплаты\n' \
                   f'{card:>30} \n' \
                   f'Сумма платежа\n' \
                   f'{summ:>45} руб.'
            date_time_sql = utils.form_date(date)
            summ_sq = str(summ).replace(',', '.')
            summ_sql = str(summ_sq).replace(' ', '')
            connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
            cursor = connection.cursor()
            try:
                new_pay = (num, date_time_sql, usl, card, summ_sql, 'dm', 'ykd', pokaz)
                request_to_insert_data = ''' INSERT INTO pay (num, date, usl, card, summ, kf, kp, pokaz) VALUES (%s, %s, %s, %s, %s, %s, %s, %s); '''
                cursor.execute(request_to_insert_data, new_pay)
                connection.commit()
                print('Данные введены')
            except Exception as e:
                # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
                connection.rollback()
                print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")
            finally:
                # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
                cursor.close()
                connection.close()
            await message.answer(chek, keyboard=kb.opl_zkh_dm())
            await vk_bot.state_dispenser.delete(message.peer_id)
        else:
            print('Данные из чека не извлечены')
            await message.answer(text.falling_chek, keyboard=kb.opl_zkh_dm())
            await vk_bot.state_dispenser.delete(message.peer_id)    
    else:
        await message.answer(text.falling_pay, keyboard=kb.opl_zkh_dm())
        await vk_bot.state_dispenser.delete(message.peer_id)

@vk_bot.on.message(MyRule(), PayloadABCRule('no'), state=Opl_yk_dm.PREPARATION)
async def opl_yk_dm(message: Message):
    await message.answer('Укажи сумму, которую собираешься оплатить.')
    await vk_bot.state_dispenser.set(message.peer_id, Opl_yk_dm.SUMM)

@vk_bot.on.message(MyRule(), state=Opl_yk_dm.SUMM)
async def opl_yk_dm(message: Message):
    data_summ = message.text
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, yk, schet, bik, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'dm' AND postavshiki.kp = 'ykd' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        schet = data[0][2]
        bik = data[0][3]
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await message.answer(text.preparation_pay)
    input_value = driver_jkh.oplata_yk_dm(inn=inn, l_sch=l_sch, schet=schet, bik=bik, summ=data_summ)
    if input_value[0] is True:
        await message.answer(text.question_pay.format(input_value[1]), keyboard=kb.yes_no_kb())
        await vk_bot.state_dispenser.set(message.peer_id, Opl_yk_dm.PREPARATION)
    else:
        await message.answer(text.falling_pay, keyboard=kb.opl_zkh_dm())

### Оплата УК Инструментальная
@vk_bot.on.message(MyRule(), PayloadABCRule('ykin'))
async def opl_yk_in_preparetion(message: Message):
    try:
        await vk_bot.state_dispenser.delete(message.peer_id)
    except KeyError:
        pass  # Состояние не найдено — игнорируем
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT yk, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'in' AND postavshiki.kp = 'yki' '''
        cursor.execute(select)
        data = cursor.fetchall()
        l_sch = data[0][0]
        summ = str(data[0][1])
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await message.answer(text.preparation_pay)
    input_value = driver_jkh.oplata_yk_in(l_sch=l_sch, summ=summ)
    if input_value[0] is True:
        await message.answer(text.question_pay.format(input_value[1]), keyboard=kb.yes_no_kb())
        await vk_bot.state_dispenser.set(message.peer_id, Opl_yk_in.PREPARATION)
    else:
        await message.answer(text.falling_pay, keyboard=kb.opl_zkh_in())

@vk_bot.on.message(MyRule(), PayloadABCRule('yes'), state=Opl_yk_in.PREPARATION)
async def opl_yk_in(message: Message):
    if driver_jkh.oplata_yk_in_yes():    
        rekviz = utils.get_info_from_chek()
        if rekviz:
            num = rekviz[0]
            date = rekviz[1]
            usl = rekviz[2]
            card = rekviz[3]
            summ = rekviz[4]
            pokaz = rekviz[5]
            chek = f'*******Чек по операции*******\n' \
                   f'Дата и время платежа\n' \
                   f'{date:>45}\n' \
                   f'Идентификатор платежа\n' \
                   f'{num:>45}\n' \
                   f'Вид услуги\n' \
                   f'{usl:>30}\n' \
                   f'Показания счетчика\n' \
                   f'{pokaz:>45}\n' \
                   f'Способ оплаты\n' \
                   f'{card:>30} \n' \
                   f'Сумма платежа\n' \
                   f'{summ:>45} руб.'
            date_time_sql = utils.form_date(date)
            summ_sq = str(summ).replace(',', '.')
            summ_sql = str(summ_sq).replace(' ', '')
            connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
            cursor = connection.cursor()
            try:
                new_pay = (num, date_time_sql, usl, card, summ_sql, 'in', 'yki', pokaz)
                request_to_insert_data = ''' INSERT INTO pay (num, date, usl, card, summ, kf, kp, pokaz) VALUES (%s, %s, %s, %s, %s, %s, %s, %s); '''
                cursor.execute(request_to_insert_data, new_pay)
                connection.commit()
                print('Данные введены')
            except Exception as e:
                # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
                connection.rollback()
                print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")
            finally:
                # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
                cursor.close()
                connection.close()
            await message.answer(chek, keyboard=kb.opl_zkh_in())
            await vk_bot.state_dispenser.delete(message.peer_id)
        else:
            print('Данные из чека не извлечены')
            await message.answer(text.falling_chek, keyboard=kb.opl_zkh_in())
            await vk_bot.state_dispenser.delete(message.peer_id)    
    else:
        await message.answer(text.falling_pay, keyboard=kb.opl_zkh_in())
        await vk_bot.state_dispenser.delete(message.peer_id)

@vk_bot.on.message(MyRule(), PayloadABCRule('no'), state=Opl_yk_in.PREPARATION)
async def opl_yk_in(message: Message):
    await message.answer('Укажи сумму, которую собираешься оплатить.')
    await vk_bot.state_dispenser.set(message.peer_id, Opl_yk_in.SUMM)

@vk_bot.on.message(MyRule(), state=Opl_yk_in.SUMM)
async def opl_yk_in(message: Message):
    data_summ = message.text
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT yk, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'in' AND postavshiki.kp = 'yki' '''
        cursor.execute(select)
        data = cursor.fetchall()
        l_sch = data[0][0]
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await message.answer(text.preparation_pay)
    input_value = driver_jkh.oplata_yk_in(l_sch=l_sch, summ=data_summ)
    if input_value[0] is True:
        await message.answer(text.question_pay.format(input_value[1]), keyboard=kb.yes_no_kb())
        await vk_bot.state_dispenser.set(message.peer_id, Opl_yk_in.PREPARATION)
    else:
        await message.answer(text.falling_pay, keyboard=kb.opl_zkh_in())

### Оплата УК Фрунзе
@vk_bot.on.message(MyRule(), PayloadABCRule('ykfr'))
async def opl_yk_fr_pok_lt(message: Message):
    try:
        await vk_bot.state_dispenser.delete(message.peer_id)
    except KeyError:
        pass  # Состояние не найдено — игнорируем
    await message.answer('Укажи показания счетчика электроэнергии.')
    await vk_bot.state_dispenser.set(message.peer_id, Opl_yk_fr.POK_LT)

@vk_bot.on.message(MyRule(), state=Opl_yk_fr.POK_LT)
async def opl_yk_fr_cwt(message: Message):
    ctx.set("pok_lt", message.text)
    await message.answer('Укажи показания счетчика холодной воды.')
    await vk_bot.state_dispenser.set(message.peer_id, Opl_yk_fr.POK_CWT)

@vk_bot.on.message(MyRule(), state=Opl_yk_fr.POK_CWT)
async def opl_yk_fr_hwt(message: Message):
    ctx.set("pok_cwt", message.text)
    await message.answer('Укажи показания счетчика горячей воды.')
    await vk_bot.state_dispenser.set(message.peer_id, Opl_yk_fr.POK_HWT)

@vk_bot.on.message(MyRule(), state=Opl_yk_fr.POK_HWT)
async def opl_yk_fr_preparetion(message: Message):
    ctx.set("pok_hwt", message.text)
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, yk, schet, bik, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'fr' AND postavshiki.kp = 'ykf' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        schet = data[0][2]
        bik = data[0][3]
        summ = str(data[0][4])
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    pok_lt = ctx.get('pok_lt')
    pok_cwt = ctx.get('pok_cwt')
    pok_hwt = ctx.get('pok_hwt')
    await message.answer(text.preparation_pay)
    input_value = driver_jkh.oplata_yk_fr(inn=inn, l_sch=l_sch, schet=schet, bik=bik, pok_lt=pok_lt, pok_cwt=pok_cwt, pok_hwt=pok_hwt, summ=summ)
    if input_value[0] is True:
        await message.answer(text.question_pay_fr.format(input_value[2], input_value[3], input_value[4], input_value[1]), keyboard=kb.yes_no_kb())
        await vk_bot.state_dispenser.set(message.peer_id, Opl_yk_fr.PREPARATION)
    else:
        await message.answer(text.falling_pay, keyboard=kb.opl_zkh_fr())

@vk_bot.on.message(MyRule(), PayloadABCRule('yes'), state=Opl_yk_fr.PREPARATION)
async def opl_yk_fr_preparetion(message: Message):
    if driver_jkh.oplata_yk_fr_yes():    
        rekviz = utils.get_info_from_chek()
        pokaz_lt = ctx.get('pok_lt')
        pokaz_cwt = ctx.get('pok_cwt')
        pokaz_hwt = ctx.get('pok_hwt')
        if rekviz:
            num = rekviz[0]
            date = rekviz[1]
            usl = rekviz[2]
            card = rekviz[3]
            summ = rekviz[4]
            pokaz = rekviz[5]
            chek = f'*******Чек по операции*******\n' \
                   f'Дата и время платежа\n' \
                   f'{date:>45}\n' \
                   f'Идентификатор платежа\n' \
                   f'{num:>45}\n' \
                   f'Вид услуги\n' \
                   f'{usl:>45}\n' \
                   f'Показания счетчика\n' \
                   f'{pokaz:>45}\n' \
                   f'Способ оплаты\n' \
                   f'{card:>30} \n' \
                   f'Сумма платежа\n' \
                   f'{summ:>45} руб.'
            date_time_sql = utils.form_date(date)
            summ_sq = str(summ).replace(',', '.')
            summ_sql = str(summ_sq).replace(' ', '')
            connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
            cursor = connection.cursor()
            try:
                new_pay = (num, date_time_sql, usl, card, summ_sql, 'fr', 'ykf', pokaz)
                request_to_insert_data = ''' INSERT INTO pay (num, date, usl, card, summ, kf, kp, pokaz) VALUES (%s, %s, %s, %s, %s, %s, %s, %s); '''
                cursor.execute(request_to_insert_data, new_pay)

                new_pokaz_lt = (pokaz_lt, 'fr', 'lt')
                request_to_update_pokaz_lt = "UPDATE pokazania SET pokaz = %s WHERE kf = %s AND kp = %s"
                cursor.execute(request_to_update_pokaz_lt, new_pokaz_lt)

                new_pokaz_cwt = (pokaz_cwt, 'fr', 'cwt')
                request_to_update_pokaz_cwt = "UPDATE pokazania SET pokaz = %s WHERE kf = %s AND tip_wt = %s"
                cursor.execute(request_to_update_pokaz_cwt, new_pokaz_cwt)

                new_pokaz_hwt = (pokaz_hwt, 'fr', 'hwt')
                request_to_update_pokaz_hwt = "UPDATE pokazania SET pokaz = %s WHERE kf = %s AND tip_wt = %s"
                cursor.execute(request_to_update_pokaz_hwt, new_pokaz_hwt) 
                connection.commit()
                print('Данные введены')
            except Exception as e:
                # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
                connection.rollback()
                print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")
            finally:
                # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
                cursor.close()
                connection.close()
            await message.answer(chek, keyboard=kb.opl_zkh_fr())
            await vk_bot.state_dispenser.delete(message.peer_id)
        else:
            print('Данные из чека не извлечены')
            await message.answer(text.falling_chek, keyboard=kb.opl_zkh_fr())
            await vk_bot.state_dispenser.delete(message.peer_id)    
    else:
        await message.answer(text.falling_pay, keyboard=kb.opl_zkh_fr())
        await vk_bot.state_dispenser.delete(message.peer_id)

@vk_bot.on.message(MyRule(), PayloadABCRule('no'), state=Opl_yk_fr.PREPARATION)
async def opl_yk_fr(message: Message):
    await message.answer('Укажи сумму, которую собираешься оплатить.')
    await vk_bot.state_dispenser.set(message.peer_id, Opl_yk_fr.SUMM)

@vk_bot.on.message(MyRule(), state=Opl_yk_fr.SUMM)
async def opl_yk_fr(message: Message):        
    data_summ = message.text
    pok_lt = ctx.get('pok_lt')
    pok_cwt = ctx.get('pok_cwt')
    pok_hwt = ctx.get('pok_hwt')
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, yk, schet, bik, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'fr' AND postavshiki.kp = 'ykf' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        schet = data[0][2]
        bik = data[0][3]
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await message.answer(text.preparation_pay)
    input_value = driver_jkh.oplata_yk_fr(inn=inn, l_sch=l_sch, schet=schet, bik=bik, pok_lt=pok_lt, pok_cwt=pok_cwt, pok_hwt=pok_hwt, summ=data_summ)
    if input_value[0] is True:
        await message.answer(text.question_pay_fr.format(input_value[2], input_value[3], input_value[4], input_value[1]), keyboard=kb.yes_no_kb())
        await vk_bot.state_dispenser.set(message.peer_id, Opl_yk_fr.PREPARATION)
    else:
        await message.answer(text.falling_pay, keyboard=kb.opl_zkh_fr())

# Оплата теплоэнерго Инструментальная
@vk_bot.on.message(MyRule(), PayloadABCRule('wmin'))
async def opl_wm_in_preparetion(message: Message):
    try:
        await vk_bot.state_dispenser.delete(message.peer_id)
    except KeyError:
        pass  # Состояние не найдено — игнорируем
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, warm, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'in' AND postavshiki.kp = 'wm' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        summ = str(data[0][2])
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await message.answer(text.preparation_pay)
    input_value = driver_jkh.oplata_wm(inn=inn, l_sch=l_sch, summ=summ)
    if input_value[0] is True:
        await message.answer(text.question_pay.format(input_value[1]), keyboard=kb.yes_no_kb())
        await vk_bot.state_dispenser.set(message.peer_id, Opl_wm_in.PREPARATION)
    else:
        await message.answer(text.falling_pay, keyboard=kb.opl_zkh_in())

@vk_bot.on.message(MyRule(), PayloadABCRule('yes'), state=Opl_wm_in.PREPARATION)
async def opl_wm_in(message: Message):
    if driver_jkh.oplata_wm_yes():    
        rekviz = utils.get_info_from_chek()
        if rekviz:
            num = rekviz[0]
            date = rekviz[1]
            usl = rekviz[2]
            card = rekviz[3]
            summ = rekviz[4]
            pokaz = rekviz[5]
            chek = f'*******Чек по операции*******\n' \
                   f'Дата и время платежа\n' \
                   f'{date:>45}\n' \
                   f'Идентификатор платежа\n' \
                   f'{num:>45}\n' \
                   f'Вид услуги\n' \
                   f'{usl:>30}\n' \
                   f'Показания счетчика\n' \
                   f'{pokaz:>45}\n' \
                   f'Способ оплаты\n' \
                   f'{card:>30} \n' \
                   f'Сумма платежа\n' \
                   f'{summ:>45} руб.'
            date_time_sql = utils.form_date(date)
            summ_sq = str(summ).replace(',', '.')
            summ_sql = str(summ_sq).replace(' ', '')
            connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
            cursor = connection.cursor()
            try:
                new_pay = (num, date_time_sql, usl, card, summ_sql, 'in', 'wm', pokaz)
                request_to_insert_data = ''' INSERT INTO pay (num, date, usl, card, summ, kf, kp, pokaz) VALUES (%s, %s, %s, %s, %s, %s, %s, %s); '''
                cursor.execute(request_to_insert_data, new_pay)
                connection.commit()
                print('Данные введены')
            except Exception as e:
                # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
                connection.rollback()
                print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")
            finally:
                # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
                cursor.close()
                connection.close()
            await message.answer(chek, keyboard=kb.opl_zkh_in())
            await vk_bot.state_dispenser.delete(message.peer_id)
        else:
            print('Данные из чека не извлечены')
            await message.answer(text.falling_chek, keyboard=kb.opl_zkh_in())
            await vk_bot.state_dispenser.delete(message.peer_id)    
    else:
        await message.answer(text.falling_pay, keyboard=kb.opl_zkh_in())
        await vk_bot.state_dispenser.delete(message.peer_id)

@vk_bot.on.message(MyRule(), PayloadABCRule('no'), state=Opl_wm_in.PREPARATION)
async def opl_wm_in(message: Message):
    await message.answer('Укажи сумму, которую собираешься оплатить.')
    await vk_bot.state_dispenser.set(message.peer_id, Opl_wm_in.SUMM)

@vk_bot.on.message(MyRule(), state=Opl_wm_in.SUMM)
async def opl_wm_in(message: Message):
    data_summ = message.text
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, warm, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'in' AND postavshiki.kp = 'wm' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await message.answer(text.preparation_pay)
    input_value = driver_jkh.oplata_wm(inn=inn, l_sch=l_sch, summ=data_summ)
    if input_value[0] is True:
        await message.answer(text.question_pay.format(input_value[1]), keyboard=kb.yes_no_kb())
        await vk_bot.state_dispenser.set(message.peer_id, Opl_wm_in.PREPARATION)
    else:
        await message.answer(text.falling_pay, keyboard=kb.opl_zkh_in())

### Оплата Водоснабжение Дом
@vk_bot.on.message(MyRule(), PayloadABCRule('wtdm'))
async def opl_wt_dm_pok(message: Message):
    try:
        await vk_bot.state_dispenser.delete(message.peer_id)
    except KeyError:
        pass  # Состояние не найдено — игнорируем
    await message.answer('Укажи показания счетчика воды.')
    await vk_bot.state_dispenser.set(message.peer_id, Opl_wt_dm.POK_WT)

@vk_bot.on.message(MyRule(), state=Opl_wt_dm.POK_WT)
async def opl_wt_dm_preparetion(message: Message):
    ctx.set("pok_wt", message.text)
    data_pokaz = message.text
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, water, pokaz, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'dm' AND postavshiki.kp = 'wt' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        pok = data[0][2]
        summ = str(data[0][3])
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await message.answer(text.preparation_pay)
    input_value = driver_jkh.oplata_wt(inn=inn, l_sch=l_sch, pok=data_pokaz, summ=summ)
    if input_value[0] is True:
        await message.answer(text.question_pay_wt.format(input_value[2], input_value[1]), keyboard=kb.yes_no_kb())
        await vk_bot.state_dispenser.set(message.peer_id, Opl_wt_dm.PREPARATION)
    else:
        await message.answer(text.falling_pay, kb=kb.opl_zkh_dm())

@vk_bot.on.message(MyRule(), PayloadABCRule('yes'), state=Opl_wt_dm.PREPARATION)
async def opl_wt_dm(message: Message):
    if driver_jkh.oplata_wt_yes():    
        rekviz = utils.get_info_from_chek()
        data_pokaz = ctx.get('pok_wt')
        if rekviz:
            num = rekviz[0]
            date = rekviz[1]
            usl = rekviz[2]
            card = rekviz[3]
            summ = rekviz[4]
            pokaz = data_pokaz
            chek = f'*******Чек по операции*******\n' \
                   f'Дата и время платежа\n' \
                   f'{date:>45}\n' \
                   f'Идентификатор платежа\n' \
                   f'{num:>45}\n' \
                   f'Вид услуги\n' \
                   f'{usl:>30}\n' \
                   f'Показания счетчика\n' \
                   f'{pokaz:>45}\n' \
                   f'Способ оплаты\n' \
                   f'{card:>30} \n' \
                   f'Сумма платежа\n' \
                   f'{summ:>45} руб.'
            date_time_sql = utils.form_date(date)
            summ_sq = str(summ).replace(',', '.')
            summ_sql = str(summ_sq).replace(' ', '')
            connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
            cursor = connection.cursor()
            try:
                new_pay = (num, date_time_sql, usl, card, summ_sql, 'dm', 'wt', pokaz)
                request_to_insert_data = ''' INSERT INTO pay (num, date, usl, card, summ, kf, kp, pokaz) VALUES (%s, %s, %s, %s, %s, %s, %s, %s); '''
                cursor.execute(request_to_insert_data, new_pay)

                connection.commit()
                print('Данные введены')
            except Exception as e:
                # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
                connection.rollback()
                print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")
            finally:
                # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
                cursor.close()
                connection.close()
            await message.answer(chek, keyboard=kb.opl_zkh_dm())
            await vk_bot.state_dispenser.delete(message.peer_id)
        else:
            print('Данные из чека не извлечены')
            await message.answer(text.falling_chek, keyboard=kb.opl_zkh_dm())
            await vk_bot.state_dispenser.delete(message.peer_id)    
    else:
        await message.answer(text.falling_pay, keyboard=kb.opl_zkh_dm())
        await vk_bot.state_dispenser.delete(message.peer_id)

@vk_bot.on.message(MyRule(), PayloadABCRule('no'), state=Opl_wt_dm.PREPARATION)
async def opl_wt_dm(message: Message):
    await message.answer('Укажи сумму, которую собираешься оплатить.')
    await vk_bot.state_dispenser.set(message.peer_id, Opl_wt_dm.SUMM)

@vk_bot.on.message(MyRule(), state=Opl_wt_dm.SUMM)
async def opl_wt_dm(message: Message):
    data_summ = message.text
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, water, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'dm' AND postavshiki.kp = 'wt' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await message.answer(text.preparation_pay)
    input_value = driver_jkh.oplata_wt(inn=inn, l_sch=l_sch, pok=ctx.get('pok_wt'), summ=data_summ)
    if input_value[0] is True:
        await message.answer(text.question_pay_wt.format(input_value[2], input_value[1]), keyboard=kb.yes_no_kb())
        await vk_bot.state_dispenser.set(message.peer_id, Opl_wt_dm.PREPARATION)
    else:
        await message.answer(text.falling_pay, keyboard=kb.opl_zkh_dm())
        await vk_bot.state_dispenser.delete(message.peer_id)

# Оплата Водоснабжения Петровская
@vk_bot.on.message(MyRule(), PayloadABCRule('wtpt'))
async def opl_wt_pt_preparetion(message: Message):
    try:
        await vk_bot.state_dispenser.delete(message.peer_id)
    except KeyError:
        pass  # Состояние не найдено — игнорируем
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, water, pokaz, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'pt' AND postavshiki.kp = 'wt' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        pok = data[0][2]
        summ = str(data[0][3])
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await message.answer(text.preparation_pay)
    input_value = driver_jkh.oplata_wt(inn=inn, l_sch=l_sch, pok=pok, summ=summ)
    if input_value[0] is True:
        await message.answer(text.question_pay.format(input_value[1]), keyboard=kb.yes_no_kb())
        await vk_bot.state_dispenser.set(message.peer_id, Opl_wt_pt.PREPARATION)
    else:
        await message.answer(text.falling_pay, keyboard=kb.opl_zkh_pt())

@vk_bot.on.message(MyRule(), PayloadABCRule('yes'), state=Opl_wt_pt.PREPARATION)
async def opl_wt_pt_preparetion(message: Message):
    if driver_jkh.oplata_wt_yes():    
        rekviz = utils.get_info_from_chek()
        if rekviz:
            num = rekviz[0]
            date = rekviz[1]
            usl = rekviz[2]
            card = rekviz[3]
            summ = rekviz[4]
            pokaz = rekviz[5]
            chek = f'*******Чек по операции*******\n' \
                   f'Дата и время платежа\n' \
                   f'{date:>45}\n' \
                   f'Идентификатор платежа\n' \
                   f'{num:>45}\n' \
                   f'Вид услуги\n' \
                   f'{usl:>30}\n' \
                   f'Показания счетчика\n' \
                   f'{pokaz:>45}\n' \
                   f'Способ оплаты\n' \
                   f'{card:>30} \n' \
                   f'Сумма платежа\n' \
                   f'{summ:>45} руб.'
            date_time_sql = utils.form_date(date)
            summ_sq = str(summ).replace(',', '.')
            summ_sql = str(summ_sq).replace(' ', '')
            connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
            cursor = connection.cursor()
            try:
                new_pay = (num, date_time_sql, usl, card, summ_sql, 'pt', 'wt', pokaz)
                request_to_insert_data = ''' INSERT INTO pay (num, date, usl, card, summ, kf, kp, pokaz) VALUES (%s, %s, %s, %s, %s, %s, %s, %s); '''
                cursor.execute(request_to_insert_data, new_pay)
                connection.commit()
                print('Данные введены')
            except Exception as e:
                # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
                connection.rollback()
                print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")
            finally:
                # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
                cursor.close()
                connection.close()
            await message.answer(chek, keyboard=kb.opl_zkh_pt())
            await vk_bot.state_dispenser.delete(message.peer_id)
        else:
            print('Данные из чека не извлечены')
            await message.answer(text.falling_chek, keyboard=kb.opl_zkh_pt())
            await vk_bot.state_dispenser.delete(message.peer_id)    
    else:
        await message.answer(text.falling_pay, keyboard=kb.opl_zkh_pt())
        await vk_bot.state_dispenser.delete(message.peer_id)

@vk_bot.on.message(MyRule(), PayloadABCRule('no'), state=Opl_wt_pt.PREPARATION)
async def opl_wt_pt(message: Message):
    await message.answer('Укажи сумму, которую собираешься оплатить.')
    await vk_bot.state_dispenser.set(message.peer_id, Opl_wt_pt.SUMM)

@vk_bot.on.message(MyRule(), state=Opl_wt_pt.SUMM)
async def opl_wt_pt(message: Message):
    data_summ = message.text
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, water, pokaz, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'pt' AND postavshiki.kp = 'wt' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        pok = data[0][2]
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await message.answer(text.preparation_pay)
    input_value = driver_jkh.oplata_wt(inn=inn, l_sch=l_sch, pok=pok, summ=data_summ)
    if input_value[0] is True:
        await message.answer(text.question_pay.format(input_value[1]), keyboard=kb.yes_no_kb())
        await vk_bot.state_dispenser.set(message.peer_id, Opl_wt_pt.PREPARATION)
    else:
        await message.answer(text.falling_pay, keyboard=kb.opl_zkh_pt())

# Оплата Водоснабжения Инструментальная
@vk_bot.on.message(MyRule(), PayloadABCRule('wtin'))
async def opl_wt_in_hwt(message: Message):
    try:
        await vk_bot.state_dispenser.delete(message.peer_id)
    except KeyError:
        pass  # Состояние не найдено — игнорируем
    await message.answer('Укажи показания счетчика горячей воды.')
    await vk_bot.state_dispenser.set(message.peer_id, Opl_wt_in.POK_HWT)

@vk_bot.on.message(MyRule(), state=Opl_wt_in.POK_HWT)
async def opl_wt_in_cwt(message: Message):
    ctx.set("pok_hwt", message.text)
    await message.answer('Укажи показания счетчика холодной воды.')
    await vk_bot.state_dispenser.set(message.peer_id, Opl_wt_in.POK_CWT)

@vk_bot.on.message(MyRule(), state=Opl_wt_in.POK_CWT)
async def opl_wt_in_preparetion(message: Message):    
    ctx.set("pok_cwt", message.text)
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, water, pokaz, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'in' AND postavshiki.kp = 'wt' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        summ = str(data[0][3])
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await message.answer(text.preparation_pay)
    input_value = driver_jkh.oplata_wt_in(inn=inn, l_sch=l_sch, c_pok=ctx.get('pok_cwt'), h_pok=ctx.get('pok_hwt'), summ=summ)
    if input_value[0] is True:
        await message.answer(text.question_pay_wt_in.format(input_value[2], input_value[3], input_value[1]), keyboard=kb.yes_no_kb())
        await vk_bot.state_dispenser.set(message.peer_id, Opl_wt_in.PREPARATION)
    else:
        await message.answer(text.falling_pay, keyboard=kb.opl_zkh_in())

@vk_bot.on.message(MyRule(), PayloadABCRule('yes'), state=Opl_wt_in.PREPARATION)
async def opl_wt_in(message: Message):
    if driver_jkh.oplata_wt_yes():    
        rekviz = utils.get_info_from_chek()
        if rekviz:
            num = rekviz[0]
            date = rekviz[1]
            usl = rekviz[2]
            card = rekviz[3]
            summ = rekviz[4]
            pokaz = rekviz[5]
            pokaz_cwt = ctx.get('pok_cwt')
            pokaz_hwt = ctx.get('pok_hwt')
            chek = f'*******Чек по операции*******\n' \
                   f'Дата и время платежа\n' \
                   f'{date:>45}\n' \
                   f'Идентификатор платежа\n' \
                   f'{num:>25}\n' \
                   f'<b>Вид услуги</b>\n' \
                   f'{usl:>35}\n' \
                   f'Показания счетчика холодной воды\n' \
                   f'{pokaz_cwt:>45}\n' \
                   f'Показания счетчика горячей воды\n' \
                   f'{pokaz_hwt:>45}\n' \
                   f'Способ оплаты\n' \
                   f'{card:>30} \n' \
                   f'Сумма платежа\n' \
                   f'{summ:>45} руб.'
            date_time_sql = utils.form_date(date)
            summ_sq = str(summ).replace(',', '.')
            summ_sql = str(summ_sq).replace(' ', '')
            connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
            cursor = connection.cursor()
            try:
                new_pay = (num, date_time_sql, usl, card, summ_sql, 'in', 'wt', pokaz_cwt)
                request_to_insert_data = ''' INSERT INTO pay (num, date, usl, card, summ, kf, kp, pokaz) VALUES (%s, %s, %s, %s, %s, %s, %s, %s); '''
                cursor.execute(request_to_insert_data, new_pay)

                new_pokaz_cwt = (pokaz_cwt, 'in', 'cwt')
                request_to_update_pokaz_cwt = "UPDATE pokazania SET pokaz = %s WHERE kf = %s AND tip_wt = %s"
                cursor.execute(request_to_update_pokaz_cwt, new_pokaz_cwt)

                new_pokaz_hwt = (pokaz_hwt, 'in', 'hwt')
                request_to_update_pokaz_hwt = "UPDATE pokazania SET pokaz = %s WHERE kf = %s AND tip_wt = %s"
                cursor.execute(request_to_update_pokaz_hwt, new_pokaz_hwt) 
                connection.commit()
                print('Данные введены')
            except Exception as e:
                # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
                connection.rollback()
                print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")
            finally:
                # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
                cursor.close()
                connection.close()
            await message.answer(chek, keyboard=kb.opl_zkh_in())
            await vk_bot.state_dispenser.delete(message.peer_id)
        else:
            print('Данные из чека не извлечены')
            await message.answer(text.falling_chek, keyboard=kb.opl_zkh_in())
            await vk_bot.state_dispenser.delete(message.peer_id)    
    else:
        await message.answer(text.falling_pay, keyboard=kb.opl_zkh_in())
        await vk_bot.state_dispenser.delete(message.peer_id)

@vk_bot.on.message(MyRule(), PayloadABCRule('no'), state=Opl_wt_in.PREPARATION)
async def opl_wt_in(message: Message):
    await message.answer('Укажи сумму, которую собираешься оплатить.')
    await vk_bot.state_dispenser.set(message.peer_id, Opl_wt_in.SUMM)


@vk_bot.on.message(MyRule(), state=Opl_wt_in.SUMM)
async def opl_wt_in(message: Message):
    data_summ = message.text
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, water, pokaz, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'in' AND postavshiki.kp = 'wt' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await message.answer(text.preparation_pay)
    input_value = driver_jkh.oplata_wt_in(inn=inn, l_sch=l_sch, c_pok=ctx.get('pok_cwt'), h_pok=ctx.get('pok_hwt'), summ=data_summ)
    if input_value[0] is True:
        await message.answer(text.question_pay_wt_in.format(input_value[2], input_value[3], input_value[1]), keyboard=kb.yes_no_kb())
        await vk_bot.state_dispenser.set(message.peer_id, Opl_wt_in.PREPARATION)
    else:
        await message.answer(text.falling_pay, keyboard=kb.opl_zkh_in())

### Оплата Электроснабжение Дом
@vk_bot.on.message(MyRule(), PayloadABCRule('ltdm'))
async def opl_lt_dm_pok(message: Message):
    try:
        await vk_bot.state_dispenser.delete(message.peer_id)
    except KeyError:
        pass  # Состояние не найдено — игнорируем
    await message.answer('Укажи показания счетчика электроэнергии.')
    await vk_bot.state_dispenser.set(message.peer_id, Opl_lt_dm.POK_LT)

@vk_bot.on.message(MyRule(), state=Opl_lt_dm.POK_LT)
async def opl_lt_dm_preparetion(message: Message):
    ctx.get("pok_lt", message.text)        
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, light, pokaz, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'dm' AND postavshiki.kp = 'lt' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        pok = data[0][2]
        summ = str(data[0][3])
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await message.answer(text.preparation_pay)
    input_value = driver_jkh.oplata_lt(inn=inn, l_sch=l_sch, pok=ctx.get('pok_lt'), summ=summ)
    if input_value[0] is True:
        await message.answer(text.question_pay_lt.format(input_value[2], input_value[1]), keyboard=kb.yes_no_kb())
        await vk_bot.state_dispenser.set(message.peer_id, Opl_lt_dm.PREPARATION)
    else:
        await message.answer(text.falling_pay, keyboard=kb.opl_zkh_dm())

@vk_bot.on.message(MyRule(), PayloadABCRule('yes'), state=Opl_lt_dm.PREPARATION)
async def opl_lt_dm(message: Message):
    if driver_jkh.oplata_lt_yes():    
        rekviz = utils.get_info_from_chek()
        if rekviz:
            num = rekviz[0]
            date = rekviz[1]
            usl = rekviz[2]
            card = rekviz[3]
            summ = rekviz[4]
            pokaz = ctx.get('pok_lt')
            chek = f'*******Чек по операции*******\n' \
                   f'Дата и время платежа\n' \
                   f'{date:>45}\n' \
                   f'Идентификатор платежа\n' \
                   f'{num:>45}\n' \
                   f'Вид услуги\n' \
                   f'{usl:>30}\n' \
                   f'Показания счетчика\n' \
                   f'{pokaz:>45}\n' \
                   f'Способ оплаты\n' \
                   f'{card:>30} \n' \
                   f'Сумма платежа\n' \
                   f'{summ:>45} руб.'
            date_time_sql = utils.form_date(date)
            summ_sq = str(summ).replace(',', '.')
            summ_sql = str(summ_sq).replace(' ', '')
            connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
            cursor = connection.cursor()
            try:
                new_pay = (num, date_time_sql, usl, card, summ_sql, 'dm', 'lt', pokaz)
                request_to_insert_data = ''' INSERT INTO pay (num, date, usl, card, summ, kf, kp, pokaz) VALUES (%s, %s, %s, %s, %s, %s, %s, %s); '''
                cursor.execute(request_to_insert_data, new_pay)

                connection.commit()
                print('Данные введены')
            except Exception as e:
                # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
                connection.rollback()
                print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")
            finally:
                # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
                cursor.close()
                connection.close()
            await message.answer(chek, keyboard=kb.opl_zkh_dm())
            await vk_bot.state_dispenser.delete(message.peer_id)
        else:
            print('Данные из чека не извлечены')
            await message.answer(text.falling_chek, keyboard=kb.opl_zkh_dm())
            await vk_bot.state_dispenser.delete(message.peer_id)    
    else:
        await message.answer(text.falling_pay, keyboard=kb.opl_zkh_dm())
        await vk_bot.state_dispenser.delete(message.peer_id)

@vk_bot.on.message(MyRule(), PayloadABCRule('no'), state=Opl_lt_dm.PREPARATION)
async def opl_lt_dm(message: Message):
    await message.answer('Укажи сумму, которую собираешься оплатить.')
    await vk_bot.state_dispenser.set(message.peer_id, Opl_lt_dm.SUMM)

@vk_bot.on.message(MyRule(), state=Opl_lt_dm.SUMM)
async def opl_lt_dm(message: Message):
    data_summ = message.text
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, light, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'dm' AND postavshiki.kp = 'lt' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await message.answer(text.preparation_pay)
    input_value = driver_jkh.oplata_lt(inn=inn, l_sch=l_sch, pok=ctx.get('pok_lt'), summ=data_summ)
    if input_value[0] is True:
        await message.answer(text.question_pay_lt.format(input_value[2], input_value[1]), keyboard=kb.yes_no_kb())
        await vk_bot.state_dispenser.set(message.peer_id, Opl_lt_dm.PREPARATION)
    else:
        await message.answer(text.falling_pay, keyboard=kb.opl_zkh_dm())

