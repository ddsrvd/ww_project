from aiogram.fsm.state import StatesGroup, State
class Create(StatesGroup):
    get_name = State()
    get_author = State()

class Create_rev(StatesGroup):
    id_song = State()
    get_comment = State()

class Search(StatesGroup):
    s_name = State()
    s_author = State()

class UserMenu(StatesGroup):
    MAIN_MENU = State()
    SEARCHING = State()
    ADDING = State()
    CREATING_REVIEW = State()
    WATCH_REVIEW = State()
