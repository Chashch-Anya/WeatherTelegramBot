from aiogram import Bot, types, executor, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
import random
import datetime
import requests

WEATHER_TOKEN = "85db68485b2e8bf6e4f756b3610b815d"
TELEGRAM_TOKEN = "5658352542:AAHk8UBs7K6A52efosRMKK_NZh-8xI2EgLo"
storage = MemoryStorage()
bot = Bot('5658352542:AAHk8UBs7K6A52efosRMKK_NZh-8xI2EgLo')
dp = Dispatcher(bot, storage=storage)


class ProfileStatesGroup(StatesGroup):
    cityWeather = State()
    cityClother = State()
    cityWeatherFour = State()
    userSex = State()


def get_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(KeyboardButton('/weather'),
           KeyboardButton('/clother'), KeyboardButton('/mem'), KeyboardButton('/weatherFiveDays'))
    return kb


def get_kb_ser() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(KeyboardButton('Мужской'), KeyboardButton('Женский'))
    return kb


@dp.message_handler(commands=["help"])
async def start_command(message: types.Message):
    user_full_name = message.from_user.full_name
    await message.reply(f"<b>---Список команд---</b>\n<b>/help</b> - Вывод справки, которую ты сейчас читаешь\n<b>/start</b> - Вывод стартового сообщения\n<b>/weather</b> - Вывод погоды в данный момент времени для введенного города\n<b>/clother</b> - Вывод совета по выбору одежды, основываясь на погоде за окном\n<b>/weatherFiveDays</b> - Вывод погоды на 5 дней", reply_markup=get_kb(), parse_mode='html')


@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    user_full_name = message.from_user.full_name
    await message.reply(f"Привет,<b> {user_full_name}</b>! Хочешь получить прогноз погоды на сегодня? А может быть ты хочешь узнать, что лучше надеть сегодня? Выбери команду из списка", reply_markup=get_kb())


@dp.message_handler(commands=['weather'])
async def user_city(message: types.Message) -> None:
    await message.reply('Напиши свой город')
    await ProfileStatesGroup.cityWeather.set()


@dp.message_handler(state=ProfileStatesGroup.cityWeather)
async def get_weather(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as dataState:
        dataState['cityWeather'] = message.text
        smile_and_weather = {
            "Clear": "Ясно \U00002600",
            "Clouds": "Облачно \U00002601",
            "Rain": "Дождь \U00002614",
            "Drizzle": "Дождь \U00002614",
            "Thunderstorm": "Гроза \U000026A1",
            "Snow": "Снег \U0001F328",
            "Mist": "Туман \U0001F32B"
        }

        advice = {
            "Clear": "Не забудьте взять крем от солнца!",
            "Clouds": "Не забудьте взять крем от солнца! Облака пропускают ультрафиолет :(",
            "Rain": "Не забудьте прихватить зонт!",
            "Drizzle": "На улице очень противно, не лучшая погода для прогулок.",
            "Thunderstorm": "Будьте аккуратны! Не следует прятаться под одиноким деревом в чистом поле, будет очень неприятно :(",
            "Snow": "Обязательно наденьте шапку!",
            "Mist": "Плохая видимость, будьте аккуратны по дороге!"
        }

        try:
            r = requests.get(
                f"http://api.openweathermap.org/data/2.5/weather?q={message.text}&appid={WEATHER_TOKEN}&units=metric&lang=ru"
            )
            data = r.json()

            city = data["name"]
            current_weather = data["main"]["temp"]

            weather = data["weather"][0]["main"]
            if weather in smile_and_weather:

                wd = smile_and_weather[weather]
                ad = advice[weather]
            else:
                wd = ""
                advice = "---Хорошего дня---"

            humidity = data["main"]["humidity"]
            pressure = round(
                float(data["main"]["pressure"])*750.063783/1000, 2)
            wind = data["wind"]["speed"]

            await message.reply(f"<b>---{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}---</b>\n"
                                f"Погода в городе: {city}\nТемпература: {current_weather}C° {wd}\n"
                                f"Влажность: {humidity}%\nДавление: {pressure} мм.рт.ст\nВетер: {wind} м/с\n\n<b>---Совет дня---</b>\n{ad}", parse_mode='html'
                                )

        except:
            await message.reply("\U00002620 Проверьте название города \U00002620")
    await state.finish()


@dp.message_handler(commands=['clother'])
async def user_city(message: types.Message) -> None:
    await message.reply('Выберите свой пол', reply_markup=get_kb_ser())
    await ProfileStatesGroup.userSex.set()


@dp.message_handler(state=ProfileStatesGroup.userSex)
async def get_user(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as dataState:
        dataState['userSex'] = message.text

        await message.reply('Введите свой город')
        await ProfileStatesGroup.cityClother.set()


@dp.message_handler(state=ProfileStatesGroup.cityClother)
async def get_clother(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as dataState:
        dataState['cityClother'] = message.text
        man = {
            "Cool": "Сегодня достаточно прохладно. Обязательно возьмите с собой легкую куртку или кофту. Вниз лучше всего надеть штаны.",
            "Cold": "На улице минус, так что пора доставать зимнюю одежду. Я бы посоветовал толстовку, штаны и зимнюю куртку с шапкой.",
            "VeryCold": "Холодно. Очень-очень холодно! Лучше всего остаться дома под одеялом с чаем, но, если очень нужно, то найдите свитер потеплее и не забудьте надеть что-нибудь под штаны. Обязательно замотайтесь в шарф, натяните шапку до глаз и бегите скорее до пункта назначения.",
            "Warm": "На улице тепло! Наконец-то можно ходить без куртки кофты, но я бы посоветовал надеть наверх что-нибудь с длинным рукавом или же футболку с легкой курткой.",
            "Hot": "На улице настоящая баня! Обязательно наденьте кепку на голову и старайтесь держаться тени. Вниз лучше всего подойдут шорты, а на верх майка или футболка."
        }
        woman = {
            "Cool": "Сегодня достаточно прохладно. Обязательно возьмите с собой легкую куртку или кофту. Вниз лучше всего надеть штаны или джинсы.",
            "Cold": "На улице минус, так что пора доставать зимнюю одежду. Я бы посоветовал толстовку, штаны и зимнюю куртку с шапкой. А лучше - длинный пуховик",
            "VeryCold": "Холодно. Очень-очень холодно! Лучше всего остаться дома под одеялом с чаем, но, если очень нужно, то найдите свитер потеплее и не забудьте надеть колготки den на 100 минимум. Обязательно замотайтесь в шарф, натяните шапку до глаз и бегите скорее до пункта назначения.",
            "Warm": "На улице тепло! Наконец-то можно ходить без куртки кофты, но я бы посоветовал надеть наверх что-нибудь с длинным рукавом или же футболку с легкой курткой. Можно даже надеть платье, но лучше с колготками.",
            "Hot": "На улице настоящая баня! Обязательно наденьте кепку на голову и старайтесь держаться тени. Вниз лучше всего подойдет легкое летнее платье или шорты с майкой или футболкой."
        }

        try:
            r = requests.get(
                f"http://api.openweathermap.org/data/2.5/weather?q={message.text}&appid={WEATHER_TOKEN}&units=metric&lang=ru"
            )
            data = r.json()

            weather = data['main']['feels_like']
            if (dataState['userSex'] == 'Женский'):
                if 15 <= weather < 25:
                    clotherAdvice = woman['Warm']
                elif weather >= 25:
                    clotherAdvice = woman['Hot']
                elif 5 <= weather < 15:
                    clotherAdvice = woman['Cool']
                elif -10 < weather < 5:
                    clotherAdvice = woman['Cold']
                else:
                    clotherAdvice = woman['VeryCold']
            else:
                if 15 <= weather < 25:
                    clotherAdvice = man['Warm']
                elif weather >= 25:
                    clotherAdvice = man['Hot']
                elif 5 <= weather < 15:
                    clotherAdvice = man['Cool']
                elif -10 < weather < 5:
                    clotherAdvice = man['Cold']
                else:
                    clotherAdvice = man['VeryCold']
            print(weather)
            await message.reply(f"---{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}---\n"
                                f"Ощущается как: {weather}\n---Совет дня---\n{clotherAdvice}"
                                )

        except:
            await message.reply("\U00002620 Проверьте город\U00002620")
    await state.finish()


@dp.message_handler(commands=["mem"])
async def start_command(message: types.Message):
    num = random.randint(1, 20)
    await message.reply('Рандомный мем про погоду для вас:')
    photo = open('img/'+str(num)+'.jpg', 'rb')
    await message.answer_photo(photo)


@dp.message_handler(commands=['weatherFiveDays'])
async def city_Four(message: types.Message) -> None:
    await message.reply('Напиши свой город')
    await ProfileStatesGroup.cityWeatherFour.set()


@dp.message_handler(state=ProfileStatesGroup.cityWeatherFour)
async def get_weather_Four(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as dataState:
        dataState['cityWeatherFour'] = message.text
        smile_and_weather = {
            "Clear": "Ясно \U00002600",
            "Clouds": "Облачно \U00002601",
            "Rain": "Дождь \U00002614",
            "Drizzle": "Дождь \U00002614",
            "Thunderstorm": "Гроза \U000026A1",
            "Snow": "Снег \U0001F328",
            "Mist": "Туман \U0001F32B"
        }
        try:
            r = requests.get(
                f"https://api.openweathermap.org/data/2.5/forecast?q={message.text}&appid={WEATHER_TOKEN}&units=metric&lang=ru")

            wd = list()
            dtime = list()
            temp = list()
            data = r.json()

            for i in range(0, len(data['list'])):
                weather = data["list"][i]["weather"][0]['main']
                dtime.append(data['list'][i]['dt_txt'])
                temp.append(data['list'][i]['main']['temp'])
                if weather in smile_and_weather:

                    wd.append(smile_and_weather[weather])
                else:
                    wd.append("")

            print(wd)
            await message.reply(f"<b>---Прогноз погоды на 5 дней---</b>\n\n---{dtime[1]}---\nТемпература: {temp[1]}C° {wd[1]}\n\n---{dtime[9]}---\nТемпература:{temp[9]}C° {wd[9]}\n\n---{dtime[17]}---\nТемпература: {temp[17]}C° {wd[17]}\n\n---{dtime[25]}---\nТемпература: {temp[25]}C° {wd[25]}\n\n---{dtime[33]}---\nТемпература: {temp[33]}C° {wd[33]}", parse_mode='html')

        except:
            await message.reply("\U00002620 Проверьте название города \U00002620")
    await state.finish()


@ dp.message_handler(content_types=['text'])
async def get_user_text(message: types.Message,):

    if message.text == 'Привет':
        await message.reply('И тебе привет')
    elif message.text == 'photo':
        photo = open('VhxD7hs5Dts.jpg', 'rb')
        await message.answer_photo(photo)

    elif message.text == 'id':
        await message.reply(f'Твой ID: {message.from_user.id}', parse_mode='html')

    else:
        await message.reply(f'Я тебя не понимаю :(', parse_mode='html')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
