from aiogram.fsm.state import StatesGroup, State


class StartWorkForm(StatesGroup):
    start_work = State()


class EndWorkForm(StatesGroup):
    end_work = State()


class DateSelectState(StatesGroup):
    date_select = State()


class GeneralCleaningState(StatesGroup):
    general_cleaning_select_date = State()
    general_cleaning = State()


class AddPhotoState(StatesGroup):
    add_photo = State()


class ShiftSupervisorState(StatesGroup):
    shift_supervisor = State()


class MastersSelectState(StatesGroup):
    master_select = State()


class VacationSelectState(StatesGroup):
    vacation_select = State()


class DayOffSelectState(StatesGroup):
    day_off_select = State()


class GeneralCleaningRejectState(StatesGroup):
    reject_cleaning = State()