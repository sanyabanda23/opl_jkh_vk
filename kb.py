from vkbottle.bot import Message
from vkbottle import Keyboard, Text, OpenLink
from vkbottle.tools.keyboard.color import KeyboardButtonColor


def start_kb():
    keyboard = (
        Keyboard(one_time=False, inline=True)
        .add(Text("✅Войти в Сбербанк Онлайн", payload={"cmd": "start_sbol"}), KeyboardButtonColor.POSITIVE)
        .row()
        .add(Text("🔎Информация", payload={"cmd": "info_pay_rek"}))
    )
    return keyboard.get_json()

def yes_no_kb():
    keyboard = (
        Keyboard(one_time=True, inline=False)
        .add(Text("Да", payload={"cmd": "yes"}))
        .row()
        .add(Text("Нет", payload={"cmd": "no"}))
    )
    return keyboard.get_json()

def vibor_info_rek_kb():
    keyboard = (
        Keyboard(one_time=False, inline=True)
        .add(Text("🔎Информация о платежах", payload={"cmd": "info_pay"}))
        .row()
        .add(Text("🔎Информация о реквизитах для оплаты", payload={"cmd": "info_rek"}))
        .row()
        .add(Text("◀️ Главное меню", payload={"cmd": "main_menu_info"}), KeyboardButtonColor.PRIMARY)
    )
    return keyboard.get_json()

def vibor_info_post_lsch_kb():
    keyboard = (
        Keyboard(one_time=False, inline=True)
        .add(Text("🔎Реквизиты поставщиков", payload={"cmd": "info_pos"}))
        .row()
        .add(Text("🔎Лицевые счета для оплаты", payload={"cmd": "info_lsch"}))
        .row()
        .add(Text("◀️ Главное меню", payload={"cmd": "main_menu_info"}), KeyboardButtonColor.PRIMARY)
    )
    return keyboard.get_json()

def vibor_info_pay():
    keyboard = (
        Keyboard(one_time=False, inline=True)
        .add(Text("🔎Информация за месяц", payload={"cmd": "info_pay_mon"}))
        .row()
        .add(Text("🔎Информация по объекту и поставщику", payload={"cmd": "info_pay_kf_kp"}))
        .row()
        .add(Text("◀️ Главное меню", payload={"cmd": "main_menu_info"}), KeyboardButtonColor.PRIMARY)
    )
    return keyboard.get_json()

def vibor_kv_info_kb():
    keyboard = (
        Keyboard(one_time=False, inline=True)
        .add(Text("1-й Крепостной 24", payload={"cmd": "kf_dm"}))
        .row()
        .add(Text("Петровская 41", payload={"cmd": "kf_pt"}))
        .row()
        .add(Text("Фрунзе 79/5", payload={"cmd": "kf_fr"}))
        .row()
        .add(Text("Инструментальная 19/3", payload={"cmd": "kf_in"}))
        .row()
        .add(Text("◀️ Главное меню", payload={"cmd": "main_menu_info"}), KeyboardButtonColor.PRIMARY)
    )
    return keyboard.get_json()

def vibor_post_info_kb():
    keyboard = (
        Keyboard(one_time=False, inline=True)
        .add(Text("📦 ЕРЦ Экотранс", payload={"cmd": "kp_gb"}))
        .add(Text("🔥Газпром межрегионгаз Ростов-на-Дону", payload={"cmd": "kp_gz"}))
        .row()
        .add(Text("🏗 Фонд капиатльного ремонта", payload={"cmd": "kp_kr"}))
        .add(Text("⚡ ТНС энерго Ростов-на-Дону", payload={"cmd": "kp_lt"}))
        .row()
        .add(Text("🌡 Теплоэнерго", payload={"cmd": "kp_wm"}))
        .add(Text("💧 Управление Водоканал", payload={"cmd": "kp_wt"}))
        .row()
        .add(Text("📋 ИВЦ ЖКХ Петровский Квартал", payload={"cmd": "kp_ykd"}))
        .add(Text("📋 РЦ Континент", payload={"cmd": "kp_ykf"}))
        .row()
        .add(Text("📋 РЦ Тагансервис", payload={"cmd": "kp_yki"}))
        .add(Text("◀️ Главное меню", payload={"cmd": "main_menu_info"}), KeyboardButtonColor.PRIMARY)
    )
    return keyboard.get_json()