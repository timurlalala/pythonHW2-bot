from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states import *
from templates import SetProfileMessageTemplates
from keyboards import *
from handlers.utils import generate_profile_summary

rt = Router()

@rt.message(Command('start'))
async def start(message: Message, state: FSMContext):
    await message.answer(SetProfileMessageTemplates.WELCOME)
    await state.set_state(SetProfile.just_started)

@rt.message(Command("set_profile"), StateFilter(SetProfile.just_started))
async def set_profile(message: Message, state: FSMContext):
    await message.answer(SetProfileMessageTemplates.WEIGHT_REQUEST)
    await state.set_state(SetProfile.setting_weight)

@rt.message(StateFilter(SetProfile.setting_weight))
async def set_weight(message: Message, state: FSMContext):
    try:
        weight = int(message.text)
        assert 15 < weight < 500
    except (ValueError, AssertionError):
        await message.answer(SetProfileMessageTemplates.WEIGHT_ERROR)
        return
    await state.update_data({'weight': weight})

    await message.answer(SetProfileMessageTemplates.HEIGHT_REQUEST)
    await state.set_state(SetProfile.setting_height)

@rt.message(StateFilter(SetProfile.setting_height))
async def set_height(message: Message, state: FSMContext):
    try:
        height = int(message.text)
        assert 30 < height < 250
    except (ValueError, AssertionError):
        await message.answer(SetProfileMessageTemplates.HEIGHT_ERROR)
        return
    await state.update_data({'height': height})

    await message.answer(SetProfileMessageTemplates.AGE_REQUEST)
    await state.set_state(SetProfile.setting_age)

@rt.message(StateFilter(SetProfile.setting_age))
async def set_age(message: Message, state: FSMContext):
    try:
        age = int(message.text)
        assert 12 < age < 120
    except (ValueError, AssertionError):
        await message.answer(SetProfileMessageTemplates.AGE_ERROR)
        return
    await state.update_data({'age': age})

    await message.answer(SetProfileMessageTemplates.ACTIVITY_REQUEST)
    await state.set_state(SetProfile.setting_activity_rate)

@rt.message(StateFilter(SetProfile.setting_activity_rate))
async def set_activity_rate(message: Message, state: FSMContext):
    try:
        activity_rate = int(message.text)
        assert activity_rate < 1000
    except ValueError:
        await message.answer(SetProfileMessageTemplates.ACTIVITY_ERROR)
        return
    await state.update_data({'activity_rate': activity_rate})

    await message.answer(SetProfileMessageTemplates.CITY_REQUEST)
    await state.set_state(SetProfile.setting_city)

@rt.message(StateFilter(SetProfile.setting_city))
async def set_city(message: Message, state: FSMContext):
    # TODO Сделать проверку города
    await state.update_data({'city': message.text})

    state_data = await state.get_data()
    if (act_rate:=state_data['activity_rate']) < 120:
        act_level = 1.2
    elif act_rate < 240:
        act_level = 1.4
    elif act_rate < 300:
        act_level = 1.6
    else:
        act_level = 1.8
    calories = (10*state_data['weight'] + 6.25*state_data['height'] - 5*state_data['age']) * act_level
    await state.update_data({'target_calories': calories})
    await message.answer(
        SetProfileMessageTemplates.TARGET_CALORIES_CALCULATED.format(calories=calories),
        reply_markup=target_confirmation_keyboard, )
    await state.set_state(SetProfile.confirming_target_calories)

#TODO Разобраться с ветвлением

@rt.message(StateFilter(SetProfile.confirming_target_calories), F.text == 'Ввести свою цель')
async def request_calories(message: Message, state: FSMContext):

    await message.answer(SetProfileMessageTemplates.TARGET_CALORIES_REQUEST)
    await state.set_state(SetProfile.setting_target_calories)

@rt.message(StateFilter(SetProfile.setting_target_calories))
async def set_calories(message: Message, state: FSMContext):
    try:
        calories = int(message.text)
        assert calories > 1500
    except (ValueError, AssertionError):
        await message.answer(SetProfileMessageTemplates.TARGET_CALORIES_ERROR)
        return
    await state.update_data({'target_calories': calories, 'target_set_by_user': True})

    state_data = await state.get_data()
    await message.answer(SetProfileMessageTemplates.SETTING_DONE + generate_profile_summary(state_data))
    await state.set_state(SetProfile.profile_is_set)

@rt.message(StateFilter(SetProfile.confirming_target_calories), F.text == 'Сохранить')
async def request_calories(message: Message, state: FSMContext):

    await state.update_data({'target_set_by_user': False})

    state_data = await state.get_data()
    await message.answer(SetProfileMessageTemplates.SETTING_DONE + generate_profile_summary(state_data))
    await state.set_state(SetProfile.profile_is_set)

@rt.message(Command('show_profile'))
async def show_profile(message: Message, state: FSMContext):

    state_data = await state.get_data()
    await message.answer("Ваш профиль: " + generate_profile_summary(state_data))




# TODO Сделать редактирование профиля
