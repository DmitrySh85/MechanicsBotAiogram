from typing import TypedDict


class GeneralCleaningDict(TypedDict):
    name: str
    readable_name: str
    text: str


class ShiftSupervisorDict(GeneralCleaningDict):
    pass


GENERAL_CLEANING_CHECKLIST = [
    {
        "name": "workbench",
        "readable_name": "Личный верстак/тумба",
        "text": "Проведенные работы - мойка внутри, мойка снаружи, раскладка инструмента. Загрузите фото результата "
                "проведенных работ."
    },
    {
        "name": "oil_pump",
        "readable_name": "Маслосос",
        "text": "Проведенные работы - мойка маслонасоса внутри и снаружи. Загрузите фото результата проделанных работ."
    },
    {
        "name": "transmission_rack",
        "readable_name": "Стойка трансмиссионнная",
        "text": "Сфотографируйте и загрузите трансмиссионную стойку. "
    },
    {
        "name": "personal_usage",
        "readable_name": "Личный инструмент",
        "text": "В личное пользование входят набор инструментов, рефрактомер, фонарик, съемники. Пожалуйста загрузите "
                "их фото."
    },
    {
        "name": "walls_gates",
        "readable_name": "Ворота и стены",
        "text": "Пожалуйста загрузите фото ворот и стен"
    },
    {
        "name": "faulty_tools",
        "readable_name": "Инструмент на замену/ремонт",
        "text": "Выявление неисправных инструментов. Отправьте фото."
    },
]

SHIFT_SUPERVISOR_CHECKLIST = [
    {
        "name": "compressor",
        "readable_name": "Обслуживание винтового компрессора",
        "text": "Проведенные работы - слив конденсата, замена масла и натяжка ремней. Загрузите фото результата "
                "проведенных работ."
    },
    {
        "name": "rolling_devices",
        "readable_name": "Подкатные аппараты",
        "text": "Сфотографируйте подкатные аппараты и загрузите фото сюда."
    },
    {
        "name": "press",
        "readable_name": "Пресс",
        "text": "Сфотографируйте пресс и загрузите фото."
    },
    {
        "name": "special_equipment_stand",
        "readable_name": "Стенд спецоборудования",
        "text": "Сфотографируйте стенд спецоборудования и загрузите фото."
    },
    {
        "name": "barrels_stand",
        "readable_name": "Стенд разливного масла",
        "text": "Сфотографируйте стенд бочек."
    },
    {
        "name": "tire_fitting_stand",
        "readable_name": "Стенд шиномонтажный",
        "text": "Сфотографируйте стенд шиномонтажа и отправьте фото."
    },
    {
        "name": "balance_stand",
        "readable_name": "Стенд балансировочный",
        "text": "Сфотографируйте балансировочный стенд и отправьте фото."
    },
    {
        "name": "vulcanisator",
        "readable_name": "Вулканизатор",
        "text": "Пожалуйста сфотографируйте вулканизатор и отправьте фото сюда."
    },
    {
        "name": "washing",
        "readable_name": "Мойка колес",
        "text": "Сфотографируйте мойку колес и отправьте фото."
    },
    {
        "name": "utility_room",
        "readable_name": "Хозпомещение",
        "text": "Сфотографируйте хозпомещение и отправьте фото."
    },
    {
        "name": "changing_room",
        "readable_name": "Раздевалка",
        "text": "Сфотографируйте раздевалку и отправьте фото."
    },
    {
        "name": "wc",
        "readable_name": "Туалет",
        "text": "Сфотографируйте туалет и отправьте фото."
    }
]