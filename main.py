import csv
import random
import string
import zipfile
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

import csv_generate


# Открытие файла и получение API ключа
def get_api_key(filename: str) -> str:
    with open(filename, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['Name'] == "tg":
                return row['Key']
    return None


# Создание клавиатуры с командами
def create_menu() -> ReplyKeyboardMarkup:
    keyboard = [
        ['Получить архив с 10 файлами CSV для каждого вида транспорта']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        'Привет! Я ваш телеграм бот. Используйте кнопки ниже для взаимодействия.',
        reply_markup=create_menu()
    )


# Обработка текстовых сообщений (нажатий на кнопки)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text

    if text == 'Start':
        await start(update, context)
    elif text == 'Set Name':
        await update.message.reply_text('Пожалуйста, укажите ваше имя после команды /setname.',
                                        reply_markup=create_menu())


# Генерация случайного слова
def generate_random_word(length=8):
    letters = string.ascii_lowercase  # Используем строчные буквы
    return ''.join(random.choice(letters) for _ in range(length))


# Команда gen_10_all
async def gen_10_all(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Начинаю генерацию файлов...")
    file_names = []

    # Генерация 10 текстовых файлов
    for i in range(10):
        subsystem = 'avia'
        file_name = csv_generate.generate_random_filename(subsystem)
        rows = csv_generate.generate_true_data(subsystem, 10)
        headers = csv_generate.headers_dict[subsystem]
        with open(file_name, 'w') as f:
            writer = csv.writer(f, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(headers)  # Запись заголовков
            writer.writerows(rows)  # Запись данных
        file_names.append(file_name)

        # Обновление сообщения о прогрессе
        await update.message.reply_text(
            f'Создан файл: {file_name}. Осталось сгенерировать {10-i} файлов и отправлю архив'
        )

    # Создание ZIP-архива
    zip_file_name = 'random_words.zip'
    with zipfile.ZipFile(zip_file_name, 'w') as zipf:
        for file_name in file_names:
            zipf.write(file_name)

    # Отправка архива пользователю
    await update.message.reply_document(open(zip_file_name, 'rb'))

    # Удаление созданных файлов после отправки
    for file_name in file_names:
        os.remove(file_name)
    os.remove(zip_file_name)


# Основная функция для запуска бота
def main() -> None:
    """Start the bot."""
    api_key = get_api_key('api_key.csv')

    if not api_key:
        print("API ключ не найден.")
        return

    # Создание приложения и передача токена бота
    application = Application.builder().token(api_key).build()

    # Добавление обработчиков команд
    application.add_handler(CommandHandler("start", start))

    # Обработчик текстовых сообщений для кнопок
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Обработчик команды gen_10_all
    application.add_handler(CommandHandler("gen_10_all", gen_10_all))

    # Запуск бота до тех пор, пока пользователь не нажмет Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
