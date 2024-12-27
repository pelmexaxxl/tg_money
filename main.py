import telebot  # Импортируем библиотеку pyTelegramBotAPI для работы с Telegram Bot API
import sqlite3  # Импортируем библиотеку sqlite3 для работы с базой данных
from telebot import types  # Импортируем модуль types для создания кнопок и других Telegram объектов
from datetime import datetime, timedelta

API_TOKEN = 'Ваш_токен_здесь'

# Инициализируем объект бота
bot = telebot.TeleBot("8166374262:AAFqzaC7zN50VBji0a8E78NXMD6gA__Y9qU") 

# Подключаемся к базе данных SQLite
conn = sqlite3.connect('expenses.db', check_same_thread=False)  # check_same_thread=False позволяет работать с базой из нескольких потоков
cursor = conn.cursor()  # Создаем курсор для выполнения SQL-запросов

# Создаем таблицу для хранения расходов, если она не существует
cursor.execute('''CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,       -- Уникальный идентификатор для каждой записи
    user_id INTEGER,                            -- ID пользователя Telegram
    category TEXT,                              -- Категория расхода (например, "еда")
    amount REAL,                                -- Сумма расхода
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP    -- Время записи (по умолчанию текущее время)
)''')
conn.commit()  # Применяем изменения в базе данных

# Функция для создания главной клавиатуры
def main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)  # Создаем клавиатуру с автоадаптацией размера
    keyboard.add(
        types.KeyboardButton("Добавить трату"), 
        types.KeyboardButton("Показать статистику"),
        types.KeyboardButton("Очистить все записи")
    )  # Добавляем кнопки
    return keyboard  # Возвращаем готовую клавиатуру

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Привет! Я бот для отслеживания расходов. Нажми кнопку, чтобы добавить трату, посмотреть статистику или очистить записи.",
        reply_markup=main_keyboard()
    )

# Обработчик команды "Показать статистику"
@bot.message_handler(func=lambda message: message.text == "Показать статистику")
def show_statistics(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
        types.KeyboardButton("За неделю"), 
        types.KeyboardButton("За месяц"),
        types.KeyboardButton("Главное меню")
    )
    bot.send_message(
        message.chat.id, 
        "Выберите период:", 
        reply_markup=keyboard
    )

# Обработчик периода статистики
@bot.message_handler(func=lambda message: message.text in ["За неделю", "За месяц"])
def statistics_period(message):
    user_id = message.from_user.id
    now = datetime.now()
    if message.text == "За неделю":
        since_date = now - timedelta(days=7)
    elif message.text == "За месяц":
        since_date = now - timedelta(days=30)

    cursor.execute('SELECT category, SUM(amount) FROM expenses WHERE user_id = ? AND date >= ? GROUP BY category', (user_id, since_date))
    stats = cursor.fetchall()

    if stats:
        response = "Статистика расходов:\n"
        for category, total in stats:
            response += f"{category}: {total:.2f} руб.\n"
        bot.send_message(message.chat.id, response)
    else:
        bot.send_message(message.chat.id, "У вас нет записей за выбранный период.")

# Обработчик команды "Главное меню"
@bot.message_handler(func=lambda message: message.text == "Главное меню")
def main_menu(message):
    bot.send_message(
        message.chat.id,
        "Вы вернулись в главное меню. Выберите действие.",
        reply_markup=main_keyboard()
    )

# Обработчик команды "Очистить все записи"
@bot.message_handler(func=lambda message: message.text == "Очистить все записи")
def clear_records(message):
    user_id = message.from_user.id
    cursor.execute('DELETE FROM expenses WHERE user_id = ?', (user_id,))
    conn.commit()
    bot.send_message(message.chat.id, "Все ваши записи были удалены.")

# Обработчик команды "Добавить трату"
@bot.message_handler(func=lambda message: message.text == "Добавить трату")
def add_expense(message):
    bot.send_message(
        message.chat.id,
        "Введите сумму и категорию траты в формате: `<сумма> <категория>`. Например: `500 еда`",
        parse_mode="Markdown"
    )
    
'''
# Обработчик для текста, который не распознан
@bot.message_handler(func=lambda message: True)
def fallback(message):
    bot.send_message(
        message.chat.id, 
        "Я вас не понял. Используйте кнопки или введите данные корректно."
    )
'''

# Обработчик текста для сохранения траты
@bot.message_handler(func=lambda message: True)
def save_expense(message):
    try:
        if len(message.text.split()) != 2:
            raise ValueError("Неверный формат ввода")

        amount, category = message.text.split()
        amount = float(amount)
        user_id = message.from_user.id

        if amount <= 0:
            raise ValueError("Сумма должна быть больше нуля")

        cursor.execute('INSERT INTO expenses (user_id, category, amount) VALUES (?, ?, ?)', (user_id, category, amount))
        conn.commit()

        bot.send_message(message.chat.id, f"Трата добавлена: {amount} руб. на {category}.")
    except ValueError as e:
        bot.send_message(
            message.chat.id,
            f"Ошибка! {str(e)}. Убедитесь, что вы ввели данные в формате: `<сумма> <категория>`.",
            parse_mode="Markdown"
        )
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"Произошла ошибка: {str(e)}"
        )

# Запуск бота
if __name__ == '__main__':
    bot.polling(none_stop=True)
