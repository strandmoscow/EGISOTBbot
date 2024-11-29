import csv
import random
import string
import zipfile
import os
from telegram import Update, ReplyKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, InlineQueryHandler

import csv_generate


# Открытие файла и получение API ключа
def get_api_key(filename: str) -> str:
    with open(filename, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['Name'] == "tg":
                return row['Key']
    return None


def zip_directory(directory, zip_file):
    """
    Функция для создания zip-архива с сохранением структуры папок.

    Аргументы:
    directory (str): Путь к директории, которую нужно заархивировать.
    zip_file (str): Имя создаваемого архива.

    Возвращает:
    None
    """
    with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(directory):  # Итерация по всем файлам и подпапкам
            for file in files:
                file_path = os.path.join(root, file)  # Полный путь к текущему файлу
                # Относительный путь файла относительно директории, которую мы архивируем
                relative_path = os.path.relpath(file_path, os.path.join(directory, '..'))
                zipf.write(file_path, relative_path)  # Добавление файла в архив


# Создание клавиатуры с командами
def create_menu() -> ReplyKeyboardMarkup:
    keyboard = [
        ['Получить архив с 10 файлами CSV для каждого вида транспорта']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        'Привет! Я телеграм бот ЕГИС ОТБ. Используйте меню взаимодействия со мной!.',
        reply_markup=create_menu()
    )


async def gen_any_any_in(update: Update, context: ContextTypes.DEFAULT_TYPE, num_files, segments):
    await update.message.reply_text("Начинаю генерацию файлов...")
    file_names = []

    for segment in segments:
        await update.message.reply_text(f"Начинаю генерацию файлов сегмента {segment}")
        # Генерация 10 текстовых файлов
        for i in range(num_files):
            file_name = os.path.join('out', segment, csv_generate.generate_random_filename(segment))
            rows = csv_generate.generate_true_data(segment, 10)
            headers = csv_generate.headers_dict[segment]
            with open(file_name, 'w') as f:
                writer = csv.writer(f, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(headers)  # Запись заголовков
                writer.writerows(rows)  # Запись данных
            file_names.append(file_name)

            # Обновление сообщения о прогрессе
            if i < num_files - 1:
                await update.message.reply_text(
                    f'Еще {num_files - 1 - i}.'
                )

    # Создание ZIP-архива
    zip_file_name = 'out.zip'
    with zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_name in file_names:
            zipf.write(file_name)

    # Отправка архива пользователю
    await update.message.reply_document(open(zip_file_name, 'rb'))

    # Удаление созданных файлов после отправки
    for file_name in file_names:
        os.remove(file_name)
    os.remove(zip_file_name)


async def gen_any_any(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        await update.message.reply_text(
            "Пожалуйста, укажите правильные параметры:\n"
            "Первый параметр - натуральное число генерируемых файлов\n"
            "Второй параметр - название сегмента транспорта, для которого "
            "необходимо сгенерировать файлы из списка ниже\n"
            "['auto', 'avia', 'ship', 'rail']\n\n"
            "Пример: /gen_any_any 5 avia"
        )
        return
    
    if not context.args[0].isdigit():
        await update.message.reply_text(
            "Пожалуйста, укажите количество файлов для генерации.\n\nНапример: /gen_any_any 5 avia"
        )
        return

    num_files = int(context.args[0])

    if num_files <= 0:
        await update.message.reply_text("Количество файлов должно быть положительным числом.")
        return
    
    if not context.args[1] in ['auto', 'avia', 'ship', 'rail']:
        await update.message.reply_text(
            "Пожалуйста, укажите сегмент транспорта из ['auto', 'avia', 'ship', 'rail'].\n\n"
            "Например: /gen_any_any 5 avia"
        )
        return

    segments = [context.args[1]]

    await gen_any_any_in(update, context, num_files, segments)


# Команда gen_10_all
async def gen_10_all(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    segments = ['auto', 'avia', 'ship', 'rail']
    await gen_any_any_in(update, context, 10, segments)


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

    # Обработчик команды gen_10_all
    application.add_handler(CommandHandler("gen_10_all", gen_10_all))

    # Обработчик команды gen_10_all
    application.add_handler(CommandHandler("gen_any_any", gen_any_any))

    # Запуск бота до тех пор, пока пользователь не нажмет Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
