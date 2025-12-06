from aiogram.fsm.state import StatesGroup, State
class Create(StatesGroup):
    get_name = State()
    get_comment = State()
