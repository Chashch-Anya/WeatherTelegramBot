import requests
import datetime
from config import TELEGRAM_TOKEN, WEATHER_TOKEN
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor


bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
 user_full_name = message.from_user.full_name
 await message.reply(f"Привет, {user_full_name}! Хочешь получить прогноз погоды на сегодня? Отправь мне название города")


@dp.message_handler()
async def get_weather(message: types.Message):
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
        "Clear": "",
        "Clouds": "",
        "Rain": "Не забудьте прихватить зонт",
        "Drizzle": "",
        "Thunderstorm": "",
        "Snow": "",
        "Mist": ""
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
            advice = advice[weather]
        else:
            wd = ""
            advice = "---Хорошего дня---"

        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        wind = data["wind"]["speed"]

        await message.reply(f"---{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}---\n"
              f"Погода в городе: {city}\nТемпература: {current_weather}C° {wd}\n"
              f"Влажность: {humidity}%\nДавление: {pressure} мм.рт.ст\nВетер: {wind} м/с\n{advice}"
              )

    except:
        await message.reply("\U00002620 Проверьте название города \U00002620")


if __name__ == '__main__':
    executor.start_polling(dp)