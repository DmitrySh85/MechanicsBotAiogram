from aiogram.fsm.state import StatesGroup, State


class StartWorkForm(StatesGroup):
    start_work = State()


class EndWorkForm(StatesGroup):
    end_work = State()


class DateSelectState(StatesGroup):
    date_select = State()


class GeneralCleaningState(StatesGroup):
    general_cleaning = State()


class AddPhotoState(StatesGroup):
    add_photo = State()


class ShiftSupervisorState(StatesGroup):
    shift_supervisor = State()