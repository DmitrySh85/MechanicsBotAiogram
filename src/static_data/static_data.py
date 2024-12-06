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
        "readable_name": "Личный верстак",
        "text": "Проведенные работы - мойка внутри, мойка снаружи, раскладка инструмента. Загрузите фото результата "
                "проведенных работ."
    },
    {
        "name": "oil_pump",
        "readable_name": "Маслосос",
        "text": "Проведенные работы - мойка маслонасоса внутри и снаружи. Загрузите фото результата проделанных работ."
    },
    {
        "name": "personal_usage",
        "readable_name": "Личное пользование",
        "text": "В личное пользование входят набор инструментов, рефрактомер, фонарик, съемники. Пожалуйста загрузите "
                "их фото."
    },
    {
        "name": "walls_gates",
        "readable_name": "Ворота и стены",
        "text": "Пожалуйста загрузите фото ворот и стен"
    }
]

SHIFT_SUPERVISOR_CHECKLIST = [
    {
        "name": "compressors",
        "readable_name": "Компрессора",
        "text": "Проведенные работы - слив конденсата, замена масла и натяжка ремней. Загрузите фото результата "
                "проведенных работ."
    },
    {
        "name": "faulty_tools",
        "readable_name": "Выявление неисправных инструментов",
        "text": "Выявление неисправных инструментов. Отправьте фото."
    },
    {
        "name": "barrels_wall",
        "readable_name": "Стена бочек",
        "text": "Сфотографируйте стену бочек."
    },
    {
        "name": "tire_fitting_wall",
        "readable_name": "Стена шиномонтажа",
        "text": "Сфотографируйте стену шиномонтажа"
    },
    {
        "name": "tire_fitting_wall_two",
        "readable_name": "Стена шиномонтажа 2",
        "text": "Сфотографируйте вторую стену шиномонтажа"
    },
    {
        "name": "washing",
        "readable_name": "Мойка",
        "text": "Сфотографируйте мойку и отправьте фото."
    },
    {
        "name": "workbench",
        "readable_name": "Верстак",
        "text": "Сфотографируйте верстак и отправьте фото."
    },
    {
        "name": "changing_room",
        "readable_name": "Раздевалка",
        "text": "Сфотографируйте раздевалку и отправьте фото."
    }
]