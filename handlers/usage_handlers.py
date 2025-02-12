from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states import *
from templates import UsageMessageTemplates
from handlers.utils import *

rt = Router()

@rt.message(Command("check_progress"), StateFilter(SetProfile.profile_is_set))
async def check_progress(message: Message, state: FSMContext):
    state_data = await state.get_data()
    balance_calories = state_data['consumed_calories'] - state_data['burned_calories']
    water_left = state_data['target_water'] - state_data['consumed_water']
    ans = UsageMessageTemplates.CHECK_PROGRESS.format(balance_calories=balance_calories, water_left=water_left, **state_data)
    await message.answer(ans)


@rt.message(Command("log_water"), StateFilter(SetProfile.profile_is_set))
async def log_water(message: Message, state: FSMContext):
    msg_split = message.text.split()
    amount = int(msg_split[1]) if len(msg_split) > 1 else None
    if not amount:
        await message.answer(UsageMessageTemplates.LOG_WATER_ERROR)
        return

    state_data = await state.get_data()
    state_data['consumed_water'] += amount

    await state.update_data(state_data)
    water_left = state_data['target_water'] - state_data['consumed_water']
    ans = UsageMessageTemplates.LOG_WATER.format(amount=amount, water_left=water_left, **state_data)
    await message.answer(ans)


@rt.message(Command("log_food"), StateFilter(SetProfile.profile_is_set))
async def log_food_begin(message: Message, state: FSMContext):
    msg_split = message.text.split()
    food_name = ' '.join(msg_split[1:]) if len(msg_split) > 1 else None
    if not food_name:
        await message.answer(UsageMessageTemplates.LOG_FOOD_NO_FOOD)
        return
    food_info = await get_food_info(food_name)
    if not food_info:
        await message.answer(UsageMessageTemplates.LOG_FOOD_NO_FOOD)
        return
    await message.answer(UsageMessageTemplates.LOG_FOOD_ASK_AMOUNT.format(**food_info))
    await state.update_data({"food_calories": food_info['norm_calories']})
    await state.set_state(SetProfile.waiting_for_food_amount)


@rt.message(StateFilter(SetProfile.waiting_for_food_amount))
async def log_food_finish(message: Message, state: FSMContext):
    try:
        amount = int(message.text)
    except ValueError:
        await message.answer(UsageMessageTemplates.LOG_FOOD_WRONG_AMOUNT)
        return
    state_data = await state.get_data()
    food_cal_calculated = (amount * state_data['food_calories']) / 100
    ans = UsageMessageTemplates.LOG_FOOD_SAVED.format(food_cal_calculated=food_cal_calculated)
    await message.answer(ans)

    consumed_calories = state_data.get('consumed_calories', 0) + food_cal_calculated
    await state.update_data({
        'consumed_calories': consumed_calories,
        'food_calories': None
    })
    await state.set_state(SetProfile.profile_is_set)


@rt.message(Command("log_workout"), StateFilter(SetProfile.profile_is_set))
async def log_workout(message: Message, state: FSMContext):
    msg_split = message.text.split()
    if len(msg_split) != 3:
        await message.answer(UsageMessageTemplates.LOG_WORKOUT_WRONG_FORMAT)
        return
    state_data = await state.get_data()
    weight = state_data["weight"]
    try:
        workout_met = float(msg_split[1])
    except ValueError:
        workout_met = workout_met_mapping.get(msg_split[1].lower(), None)
        if not workout_met:
            await message.answer(UsageMessageTemplates.LOG_WORKOUT_UNKNOWN_EXERCISE)
            return
    try:
        minutes = int(msg_split[2])
    except ValueError:
        await message.answer(UsageMessageTemplates.LOG_WORKOUT_WRONG_FORMAT)
        return

    calories_burnt = calculate_burnt_calories(workout_met, weight, minutes)
    ans = UsageMessageTemplates.LOG_WORKOUT_SAVED.format(minutes=minutes, calories_burnt=calories_burnt)
    if (water_multiplier := minutes // 30) >= 1:
        water = 200 * water_multiplier
        state_data['target_water'] += water
        ans += UsageMessageTemplates.LOG_WORKOUT_ADD_WATER.format(water=water)
    await message.answer(ans)
    state_data['burned_calories'] += calories_burnt
    await state.update_data(state_data)


@rt.message(Command("new_day"), StateFilter(SetProfile.profile_is_set))
async def new_day(message: Message, state: FSMContext):
    state_data = await state.get_data()

    temperature = await get_city_temperature(state_data['city'])
    water = state_data['weight'] * 30 + 500 * int(temperature > 25 if temperature else 0)
    state_data.update({
        'target_water': water,
        'consumed_water': 0,
        'consumed_calories': 0,
        'burned_calories': 0
    })
    await state.update_data(state_data)
    ans = UsageMessageTemplates.NEW_DAY
    balance_calories = state_data['consumed_calories'] - state_data['burned_calories']
    water_left = state_data['target_water'] - state_data['consumed_water']
    ans += UsageMessageTemplates.CHECK_PROGRESS.format(balance_calories=balance_calories, water_left=water_left,
                                                      **state_data)
    await message.answer(ans)
