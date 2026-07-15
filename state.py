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

### Оплата УК
class Opl_yk_dm(BaseStateGroup):
    PREPARATION = 'preparation'
    SUMM = 'summ'

class Opl_yk_in(BaseStateGroup):
    PREPARATION = 'preparation'
    SUMM = 'summ'

class Opl_yk_fr(BaseStateGroup):
    POK_LT = 'pok_lt'
    POK_CWT = 'pok_cwt'
    POK_HWT = 'pok_hwt'
    PREPARATION = 'preparation'
    SUMM = 'summ'

class Opl_wm_in(BaseStateGroup):
    PREPARATION = 'preparation'
    SUMM = 'summ'

### Оплата Водоканал
class Opl_wt_dm(BaseStateGroup):
    POK_WT = 'pok_wt'
    PREPARATION = 'preparation'
    SUMM = 'summ'

class Opl_wt_pt(BaseStateGroup):
    PREPARATION = 'preparation'
    SUMM = 'summ'

class Opl_wt_in(BaseStateGroup):
    POK_CWT = 'pok_cwt'
    POK_HWT = 'pok_hwt'
    PREPARATION = 'preparation'
    SUMM = 'summ'

### Оплата ТНС Энерго
class Opl_lt_dm(BaseStateGroup):
    POK_LT = 'pok_lt'
    PREPARATION = 'preparation'
    SUMM = 'summ'

class Opl_lt_pt(BaseStateGroup):
    POK_LT = 'pok_lt'
    PREPARATION = 'preparation'
    SUMM = 'summ'

### Оплата Газпром
class Opl_gz_dm(BaseStateGroup):
    POK_GZ = 'pok_gz'
    PREPARATION = 'preparation'
    SUMM = 'summ'

class Opl_gz_fr(BaseStateGroup):
    PREPARATION = 'preparation'
    SUMM = 'summ'