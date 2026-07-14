from vkbottle import BaseStateGroup

class Info_pay_mon(BaseStateGroup):
    MON = 'mon'

class Clear(BaseStateGroup):
    DELETE = 'delete'

class Info_pay_year(BaseStateGroup):
    YEAR = 'year'
    KF = 'kf'
    KP = 'kp'

class Vhod(BaseStateGroup):
    SMS_PASWORD = 'sms_pasword'

### Оплата капитального ремонта
class Opl_kr_pt(BaseStateGroup):
    PREPARATION = 'preparation'
    SUMM = 'summ'

class Opl_kr_fr(BaseStateGroup):
    PREPARATION = 'preparation'
    SUMM = 'summ'

class Opl_kr_in(BaseStateGroup):
    PREPARATION = 'preparation'
    SUMM = 'summ'

class Opl_kr_dm(BaseStateGroup):
    PREPARATION = 'preparation'
    SUMM = 'summ'

### Оплата вывоз ТКО
class Opl_gb_dm(BaseStateGroup):
    PREPARATION = 'preparation'
    SUMM = 'summ'

class Opl_gb_in(BaseStateGroup):
    PREPARATION = 'preparation'
    SUMM = 'summ'