import csv
import zipfile
import os
from dotenv import load_dotenv
import logging
from ftplib import FTP
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
import csv_generate

# Креденты для ftp
ftp_cred = {
    "auto": {
        "host": "195.60.221.253",
        "port": 31006,
        "username": "sgk_auto_test_ftp",
        "password": "Abcd1234"
    },
    "rail": {
        "host": "195.60.221.253",
        "port": 31002,
        "username": "sgk_rail_test",
        "password": "Abcd1234"
    },
    "ship": {
        "host": "195.60.221.253",
        "port": 31003,
        "username": "sgk_sail_test",
        "password": "Abcd1234"
    },
    "avia": {
        "host": "195.60.221.253",
        "port": 31007,
        "username": "sgk_avia_test",
        "password": "Abcd1234"
    }
}


# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


# Открытие файла и получение API ключа
def get_api_key(filename: str) -> str:
    load_dotenv()

    try:
        telegram_token = os.getenv('TELEGRAM_TOKEN')
        if not telegram_token:
            raise ValueError("API_KEY не найден в .env файле")
    except Exception as e:
        logger.error(f"Ошибка при чтении API ключа: {e}")
        return ''
    return telegram_token


def zip_directory(directory, zip_file):
    """Функция для саоздания zip-архива с сохранением структуры папок."""
    try:
        with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, os.path.join(directory, '..'))
                    zipf.write(file_path, relative_path)
    except Exception as e:
        logger.error(f"Ошибка при создании архива: {e}")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        'Привет! Я телеграм бот ЕГИС ОТБ. Используйте меню взаимодействия со мной!.',
        reply_markup=create_menu()
    )


def create_menu() -> ReplyKeyboardMarkup:
    keyboard = [['Получить архив с 10 файлами CSV для каждого вида транспорта']]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


async def gen_any_any_to_ftp(update: Update, context: ContextTypes.DEFAULT_TYPE, num_files, segments):
    await update.message.reply_text("Начинаю генерацию файлов...")
    file_names = []

    for segment in segments:
        await update.message.reply_text(f"Начинаю генерацию файлов сегмента {segment}")

        for i in range(num_files):
            file_name = os.path.join('out', segment, csv_generate.generate_random_filename(segment))
            rows = csv_generate.generate_true_data(segment, 10)
            headers = csv_generate.headers_dict[segment]

            try:
                os.makedirs(os.path.dirname(file_name), exist_ok=True)  # Создаем директорию, если не существует
                with open(file_name, 'w', newline='') as f:
                    writer = csv.writer(f, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    writer.writerow(headers)
                    writer.writerows(rows)
                file_names.append(file_name)
                await update.message.reply_text(f"Файл {file_name} успешно сгенерирован.")
            except Exception as e:
                logger.error(f"Ошибка при записи файла {file_name}: {e}")
                await update.message.reply_text(f"Ошибка при создании файла {file_name}.")
                return

            # Отправка файла на FTP
            ftp_info = ftp_cred.get(segment)
            if ftp_info:
                try:
                    ftp = FTP()
                    ftp.connect(ftp_info['host'], ftp_info['port'])
                    ftp.login(ftp_info['username'], ftp_info['password'])

                    with open(file_name, 'rb') as f:
                        ftp.storbinary(f'STOR {os.path.basename(file_name)}', f)
                    ftp.quit()

                    await update.message.reply_text(f"Файл {file_name} успешно отправлен на FTP.")
                except Exception as e:
                    logger.error(f"Ошибка при отправке файла {file_name} на FTP: {e}")
                    await update.message.reply_text(f"Ошибка при отправке файла {file_name} на FTP.")
                    return

            if i < num_files - 1:
                await update.message.reply_text(f'Еще {num_files - 1 - i}.')

    # Удаление созданных файлов после отправки
    for file_name in file_names:
        os.remove(file_name)


async def gen_any_all_to_ftp(update: Update, context: ContextTypes.DEFAULT_TYPE, num_files, segments):
    await update.message.reply_text("Начинаю генерацию файлов...")
    file_names = []

    for segment in segments:
        await update.message.reply_text(f"Начинаю генерацию файлов сегмента {segment}")

        for i in range(num_files):
            file_name = os.path.join('out', segment, csv_generate.generate_random_filename(segment))
            rows = csv_generate.generate_true_data(segment, 10)
            headers = csv_generate.headers_dict[segment]

            try:
                os.makedirs(os.path.dirname(file_name), exist_ok=True)  # Создаем директорию, если не существует
                with open(file_name, 'w', newline='') as f:
                    writer = csv.writer(f, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    writer.writerow(headers)
                    writer.writerows(rows)
                file_names.append(file_name)
                await update.message.reply_text(f"Файл {file_name} успешно сгенерирован.")
            except Exception as e:
                logger.error(f"Ошибка при записи файла {file_name}: {e}")
                await update.message.reply_text(f"Ошибка при создании файла {file_name}.")
                return

            # Отправка файла на FTP
            ftp_info = ftp_cred.get(segment)
            if ftp_info:
                try:
                    ftp = FTP()
                    ftp.connect(ftp_info['host'], ftp_info['port'])
                    ftp.login(ftp_info['username'], ftp_info['password'])

                    with open(file_name, 'rb') as f:
                        ftp.storbinary(f'STOR {os.path.basename(file_name)}', f)
                    ftp.quit()

                    await update.message.reply_text(f"Файл {file_name} успешно отправлен на FTP.")
                except Exception as e:
                    logger.error(f"Ошибка при отправке файла {file_name} на FTP: {e}")
                    await update.message.reply_text(f"Ошибка при отправке файла {file_name} на FTP.")
                    return

            if i < num_files - 1:
                await update.message.reply_text(f'Еще {num_files - 1 - i}.')

    # Удаление созданных файлов после отправки
    for file_name in file_names:
        os.remove(file_name)

async def gen_any_any_in(update: Update, context: ContextTypes.DEFAULT_TYPE, num_files, segments):
    await update.message.reply_text("Начинаю генерацию файлов...")
    file_names = []

    for segment in segments:
        await update.message.reply_text(f"Начинаю генерацию файлов сегмента {segment}")
        for i in range(num_files):
            file_name = os.path.join('out', segment, csv_generate.generate_random_filename(segment))
            rows = csv_generate.generate_true_data(segment, 10)
            headers = csv_generate.headers_dict[segment]
            try:
                with open(file_name, 'w', newline='') as f:
                    writer = csv.writer(f, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    writer.writerow(headers)
                    writer.writerows(rows)
                file_names.append(file_name)
            except Exception as e:
                logger.error(f"Ошибка при записи файла {file_name}: {e}")
                await update.message.reply_text(f"Ошибка при создании файла {file_name}.")
                return

            if i < num_files - 1:
                await update.message.reply_text(f'Еще {num_files - 1 - i}.')

    zip_file_name = 'out.zip'
    zip_directory('out', zip_file_name)

    # Отправка архива пользователю
    try:
        await update.message.reply_document(open(zip_file_name, 'rb'))
    except Exception as e:
        logger.error(f"Ошибка при отправке архива: {e}")
        await update.message.reply_text("Ошибка при отправке архива.")

    # Удаление созданных файлов после отправки
    for file_name in file_names:
        os.remove(file_name)
    os.remove(zip_file_name)


async def to_ftp_any_any(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2 or not context.args[0].isdigit():
        await update.message.reply_text(
            "Пожалуйста, укажите правильные параметры:\n"
            "Первый параметр - натуральное число генерируемых файлов\n"
            "Второй параметр - название сегмента транспорта из ['auto', 'avia', 'ship', 'rail'].\n"
            "Пример:"
        )
        await update.message.reply_text(
            "/to_ftp_any_any 5 avia"
        )
        return

    num_files = int(context.args[0])

    if num_files <= 0 or context.args[1] not in ['auto', 'avia', 'ship', 'rail']:
        await update.message.reply_text(
            "Пожалуйста, укажите корректные параметры."
        )
        return

    segments = [context.args[1]]

    await gen_any_any_to_ftp(update, context, num_files, segments)


async def to_ftp_1_all(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await gen_any_any_to_ftp(update, context, 1, ['auto', 'avia', 'ship', 'rail'])


async def gen_any_any(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2 or not context.args[0].isdigit():
        await update.message.reply_text(
            "Пожалуйста, укажите правильные параметры:\n"
            "Первый параметр - натуральное число генерируемых файлов\n"
            "Второй параметр - название сегмента транспорта из ['auto', 'avia', 'ship', 'rail'].\n"
            "Пример:"
        )
        await update.message.reply_text(
            "/gen_any_any 5 avia"
        )
        return

    num_files = int(context.args[0])

    if num_files <= 0 or context.args[1] not in ['auto', 'avia', 'ship', 'rail']:
        await update.message.reply_text(
            "Пожалуйста, укажите корректные параметры."
        )
        return

    segments = [context.args[1]]

    await gen_any_any_in(update, context, num_files, segments)


async def gen_10_all(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    segments = ['auto', 'avia', 'ship', 'rail']
    await gen_any_any_in(update, context, 10, segments)


def main() -> None:
    api_key = get_api_key('api_key.csv')

    if not api_key:
        logger.error("API ключ не найден.")
        return

    application = Application.builder().token(api_key).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("gen_10_all", gen_10_all))
    application.add_handler(CommandHandler("gen_any_any", gen_any_any))
    application.add_handler(CommandHandler("to_ftp_any_any", to_ftp_any_any))
    application.add_handler(CommandHandler("to_ftp_1_all", to_ftp_1_all))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
