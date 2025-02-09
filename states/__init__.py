from aiogram.fsm.state import State, StatesGroup


class SetProfile(StatesGroup):
    just_started = State()
    setting_weight = State()
    setting_height = State()
    setting_age = State()
    setting_activity_rate = State()
    setting_city = State()
    confirming_target_calories = State()
    setting_target_calories = State()
    profile_is_set = State()