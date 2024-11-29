import csv
import os
import random
from datetime import datetime, timedelta
from faker import Faker
from faker_airtravel import AirTravelProvider
from transliterate import translit
import bcrypt
from tqdm import tqdm

# Создание экземпляра Faker
fake = Faker('ru_RU')
fake.add_provider(AirTravelProvider)

# Генерация соли для генерации хеша
salt = bcrypt.gensalt()

# Заголовки для разных подсистем
headers_dict = {
    'auto': [
        'surname', 'name', 'patronymic', 'birthdate', 'docType', 'docNumber',
        'departPlace', 'arrivePlace', 'routeType', 'citizenship',
        'gender', 'recType', 'rank', 'phoneNumber', 'email', 'accountLogin', 'accountPasswordHash',
        'internetInformation', 'payInfoOrganization', 'payInfoAccountNumber',
        'operationType', 'operatorId', 'placeId', 'route', 'places',
        'buyDate', 'ticket', 'amount', 'currency', 'travelClass', 'termNumOrSurname',
        'departDate', 'arriveDate', 'grz', 'model', 'registerTimeIS', 'operatorVersion'
    ],
    'avia': [
        'surname', 'name', 'patronymic', 'birthdate', 'docType', 'docNumber',
        'departPlace', 'arrivePlace', 'transfer', 'overFlight',
        'gender', 'citizenship', 'typePDP', 'crewRoleCode', 'crewRole', 'phoneNumber',
        'email', 'accountLogin', 'accountPasswordHash', 'internetInformation', 'payInfoOrganization',
        'payInfoAccountNumber', 'operationType', 'registerTimeIS', 'airlineCode', 'flightNum',
        'pnrId', 'operSuff', 'ticket', 'places', 'amount', 'currency', 'travelClass',
        'departDateTime', 'arriveDateTime'
    ],
    'ship': [
        'surname', 'name', 'patronymic', 'birthdate', 'docType', 'docNumber',
        'documentAdditionalInfo', 'route', 'departPlace', 'arrivePlace', 'departDate',
        'arriveDate', 'routeType', 'citizenship', 'gender', 'recType', 'rank',
        'operationType', 'operatorId', 'places', 'reservedSeatsCount', 'buyDate',
        'termNumOrSurname', 'shipClass', 'shipNumber', 'shipName', 'flagState',
        'registerTimeIS', 'operatorVersion', 'phoneNumber', 'email', 'accountLogin', 'accountPasswordHash',
        'internetInformation', 'payInfoOrganization', 'payInfoAccountNumber', 'ticket', 'amount', 'currency',
        'travelClass', 'speId', 'gpeId'
    ],
    'rail': [
        'surname', 'name', 'patronymic', 'gender', 'birthdate', 'docType', 'docNumber',
        'departPlace', 'arrivePlace', 'departDate', 'recType', 'rank', 'operationType',
        'operatorId', 'route', 'places', 'arriveDate', 'registerTimeIS', 'operatorVersion',
        'routeType', 'citizenship', 'buyDate', 'coach', 'termNumOrSurname', 'getIVC',
        'sellIVC', 'thread', 'phoneNumber', 'email', 'accountLogin', 'accountPasswordHash', 'internetInformation',
        'payInfoOrganization', 'payInfoAccountNumber', 'ticket', 'amount', 'currency', 'travelClass'
    ]
}


# Функция для генерации случайного названия файла
def generate_random_filename(subsystem):
    if subsystem == 'auto':
        sys_number = "21000"
    elif subsystem == 'avia':
        sys_number = "11000"
    elif subsystem == 'ship':
        sys_number = "31000"
    elif subsystem == 'rail':
        sys_number = "41000"
    else:
        raise ValueError("Неверная подсистема")
    current_time = datetime.now()
    timestamp = current_time.strftime("%Y_%m_%d_%H_%M_%S_%f")[:-3]
    filename = f"{sys_number}_{timestamp}.csv"
    return filename

# Функция для генерации случайных данных для авто
def generate_auto_data():
    gender = random.choice(['M', 'F'])
    stations = ["#50520", "#69193", "#46009", "#50468", "#50355",
                "#24173", "#24125", "#50544", "#46012", "#69186", "#69183"]
    routes = [
        {"route_name": "20099", "operatorId": "20072",
         "departPlace": "#77001", "departTime": "2024-10-01T14:00Z",
         "arrivePlace": "#78001", "arriveTime": "2024-10-01T16:00Z"}
    ]
    route = routes[0]

    time_a = fake.date_time_this_year()
    time_b = time_a + timedelta(hours=10, minutes=15)
    # birthdate_is_correct = bool(random.getrandbits(1))
    birthdate_is_correct = True
    if birthdate_is_correct:
        birthdate_raw = fake.date_of_birth(minimum_age=18, maximum_age=90).strftime("%Y-%m-%d")
        birthdate = birthdate_raw
    else:
        birthdate_raw = f'{random.choice(range(1950, 2020))}-XX-XX'
        birthdate = ''
    pwd = f'{fake.password()}'

    return [
        fake.last_name_male() if gender == 'M' else fake.last_name_female(),
        fake.first_name_male() if gender == 'M' else fake.first_name_female(),
        fake.middle_name_male() if gender == 'M' else fake.middle_name_female(),
        birthdate_raw, 0, fake.random_number(digits=10, fix_len=True),
        route["departPlace"], route["arrivePlace"], random.choice([0, 1, 2]),
        "РОССИЯ", gender, random.choice([0, 1]), random.randint(1, 20),
        fake.phone_number(), fake.email(), fake.user_name(),
        bcrypt.hashpw(bytes(fake.password(), 'utf-8'), salt), f'{fake.ipv4_public()} {random.choice(range(1, 9999))}',
        random.choice(["ПАО Сбербанк", "АО \"АЛЬФА-БАНК\"", "АО \"ТБанк\""]),
        random.randint(1000, 5000), 19,
        route["operatorId"], 20001, route["route_name"],
        random.randint(1, 100), fake.date_time_this_year().strftime("%Y-%m-%dT%H:%MZ"),
        f"A{fake.random_number(digits=7, fix_len=True)}",
        random.randint(500, 20000), "RUB", random.choice(["Эконом", "Бизнес", "Первый"]), fake.name(),
        route["departTime"], route["arriveTime"],
        "A777AA777", "ПАЗ", datetime.now().strftime("%Y-%m-%dT%H:%MZ"), 20
    ]

# Функция для генерации данных для реальных рейсов для авто
def generate_true_auto_data():
    gender = random.choice(['M', 'F'])
    stations = ["#50520", "#69193", "#46009", "#50468", "#50355",
                "#24173", "#24125", "#50544", "#46012", "#69186", "#69183"]
    routes = [
        {"route": "20099", "operatorId": "20072",
         "departPlace": "#77001", "departDate": "2024-10-01T14:00Z",
         "arrivePlace": "#78001", "arriveDate": "2024-10-01T16:00Z"},
        {"route": "#24.77.78", "operatorId": "20072",
         "departPlace": "#77001", "departDate": "2024-11-08T08:00Z",
         "arrivePlace": "#78001", "arriveDate": "2024-11-08T20:00Z"}
    ]
    route = routes[1]
    birthdate_is_correct = True
    if birthdate_is_correct:
        birthdate_raw = fake.date_of_birth(minimum_age=18, maximum_age=90).strftime("%Y-%m-%d")
    else:
        birthdate_raw = f'{random.choice(range(1950, 2020))}-XX-XX'
    rec_type = random.choice([0, 1])
    if rec_type == 0:
        operation_code = 4
    if rec_type == 1:
        operation_code = 19

    return [
        fake.last_name_male() if gender == 'M' else fake.last_name_female(),
        fake.first_name_male() if gender == 'M' else fake.first_name_female(),
        fake.middle_name_male() if gender == 'M' else fake.middle_name_female(),
        birthdate_raw, 0, fake.random_number(digits=10, fix_len=True),
        route["departPlace"], route["arrivePlace"], 2,
        "РОССИЯ", gender, rec_type, random.randint(1, 20),
        fake.phone_number(), fake.email(), fake.user_name(),
        bcrypt.hashpw(bytes(fake.password(), 'utf-8'), salt), f'{fake.ipv4_public()} {random.choice(range(1, 9999))}',
        random.choice(["ПАО Сбербанк", "АО \"АЛЬФА-БАНК\"", "АО \"ТБанк\""]),
        random.randint(1000, 5000), operation_code, route["operatorId"], 20001, route["route"],
        random.randint(1, 100), fake.date_time_this_year().strftime("%Y-%m-%dT%H:%MZ"),
        f"A{fake.random_number(digits=7, fix_len=True)}", random.randint(500, 20000),
        "RUB", random.choice(["Эконом", "Бизнес", "Первый"]), fake.name(),
        route["departDate"], route["arriveDate"], "A777AA777",
        "ПАЗ", datetime.now().strftime("%Y-%m-%dT%H:%MZ"), 20
    ]

# Функция для генерации случайных данных для авиа
def generate_avia_data():
    gender = random.choice(['M', 'F'])
    city_a = fake.airport_iata()
    city_b = fake.airport_iata()
    dep_time = datetime.now() - timedelta(days=random.randint(0, 28), hours=random.randint(0, 19))
    arr_date = dep_time+timedelta(hours=random.randint(0, 19))
    birthdate_is_correct = bool(random.getrandbits(1))
    if birthdate_is_correct:
        birthdate_raw = fake.date_of_birth(minimum_age=18, maximum_age=90).strftime("%d.%m.%Y")
        birthdate = birthdate_raw
    else:
        birthdate_raw = f'XX.XX.{random.choice(range(1950, 2020))}'
        birthdate = ''

    return [
        translit(fake.last_name_male() if gender == 'M' else fake.last_name_female(), reversed=True),
        translit(fake.first_name_male() if gender == 'M' else fake.first_name_female(), reversed=True),
        translit(fake.middle_name_male() if gender == 'M' else fake.middle_name_female(), reversed=True),
        birthdate_raw, random.choice([1, 2, 4, 5, 7]), fake.ssn(), city_a, city_b,
        0, 0, gender, random.choice(['RUS']), 1, "", "",
        fake.phone_number(), fake.email(), fake.user_name(), bcrypt.hashpw(bytes(fake.password(), 'utf-8'), salt),
        f'{fake.ipv4_public()} {random.choice(range(1, 9999))}',
        random.choice(["ПАО Сбербанк", "АО \"АЛЬФА-БАНК\"", "АО \"ТБанк\""]),
        random.randint(1000, 9999), random.choice([random.randint(0, 18), 20, 19]),
        fake.date_time_this_year().strftime("%Y-%m-%dT%H:%MZ"), "SU", random.randint(1000, 9999),
        fake.bothify(text='??####'), random.choice(["B", "G", "D", "E", "F"]),
        random.randint(10000000, 99999999),
        f'{random.randint(1, 32)}{random.choice(["A", "B", "C", "D", "E", "F"])}',
        f"{random.randint(1000, 9999)}.{random.randint(10, 99)}", random.choice(['RUB', 'USD']),
        random.choice(['Эконом', 'Эконом+', 'Бизнес']),
        dep_time.strftime("%Y-%m-%dT%H:%MZ"), arr_date.strftime("%Y-%m-%dT%H:%MZ")
    ]

# Функция для генерации данных для реальных рейсов для авиа
def generate_true_avia_data():
    routes = [
        {
            "routeNumber": "S73741",
            "itch": 9402,
            "routeShortNumber": "3741",
            "planDepartDate": "2024.12.12 14:20",
            "planArriveDate": "2024.12.12 19:10",
            "departAirportNameRu": "AYT",
            "arriveAirportNameRu": "DME"
        }
    ]
    route = routes[0]

    gender = random.choice(['M', 'F'])
    city_a = route["departAirportNameRu"]
    city_b = route["arriveAirportNameRu"]
    dep_time = datetime.strptime(route["planDepartDate"], "%Y.%m.%d %H:%M")
    arr_date = datetime.strptime(route["planArriveDate"], "%Y.%m.%d %H:%M")
    birthdate_is_correct = True
    if birthdate_is_correct:
        birthdate_raw = fake.date_of_birth(minimum_age=18, maximum_age=90).strftime("%d.%m.%Y")
        birthdate = birthdate_raw
    else:
        birthdate_raw = f'XX.XX.{random.choice(range(1950, 2020))}'
        birthdate = ''

    return [
        translit(fake.last_name_male() if gender == 'M' else fake.last_name_female(), reversed=True),
        translit(fake.first_name_male() if gender == 'M' else fake.first_name_female(), reversed=True),
        translit(fake.middle_name_male() if gender == 'M' else fake.middle_name_female(), reversed=True),
        birthdate_raw, random.choice([1, 2, 4, 5, 7]), fake.ssn(), city_a, city_b,
        0, 0, gender, random.choice(['RUS']), 1, "", "",
        fake.phone_number(), fake.email(), fake.user_name(), bcrypt.hashpw(bytes(fake.password(), 'utf-8'), salt),
        f'{fake.ipv4_public()} {random.choice(range(1, 9999))}', random.choice(["ПАО Сбербанк", "АО \"АЛЬФА-БАНК\"", "АО \"ТБанк\""]),
        random.randint(1000, 9999), random.choice([random.randint(0, 18), 20, 19]),
        fake.date_time_this_month().strftime("%Y-%m-%dT%H:%MZ"), "S7", route['routeShortNumber'],
        fake.bothify(text='??####'), random.choice(["B", "G", "D", "E", "F"]),
        random.randint(10000000, 99999999),
        f'{random.randint(1, 32)}{random.choice(["A", "B", "C", "D", "E", "F"])}',
        f"{random.randint(1000, 9999)}.{random.randint(10, 99)}", random.choice(['RUB', 'USD']),
        random.choice(['Эконом', 'Эконом+', 'Бизнес']),
        dep_time.strftime("%Y-%m-%dT%H:%MZ"), arr_date.strftime("%Y-%m-%dT%H:%MZ")
    ]

# Функция для генерации случайных данных для моря (9, 19)
def generate_ship_data():
    gender = random.choice(['M', 'F'])
    city_a = fake.city_name()
    city_b = fake.city_name()
    dep_time = datetime.now() - timedelta(days=random.randint(0, 28), hours=random.randint(0, 19))
    arr_date = dep_time+timedelta(hours=random.randint(0, 19))
    birthdate_is_correct = bool(random.getrandbits(1))
    if birthdate_is_correct:
        birthdate_raw = fake.date_of_birth(minimum_age=18, maximum_age=90).strftime("%Y-%m-%d")
        birthdate = birthdate_raw
    else:
        birthdate_raw = f'{random.choice(range(1950, 2020))}-XX-XX'
        birthdate = ''

    return [
        fake.last_name_male() if gender == 'M' else fake.last_name_female(),
        fake.first_name_male() if gender == 'M' else fake.first_name_female(),
        fake.middle_name_male() if gender == 'M' else fake.middle_name_female(),
        birthdate_raw, random.randint(0, 10), fake.ssn(), '',
        f"{city_a} - {fake.city_name()} - {city_b}", city_a, city_b,
        dep_time.strftime("%Y-%m-%dT%H:%MZ"), arr_date.strftime("%Y-%m-%dT%H:%MZ"), 1, "РОССИЯ", gender,
        random.randint(0,5), '', random.choice([9, 19]),
        random.randint(1, 32), random.randint(0, 100), 1, fake.date_time_this_year().strftime("%Y-%m-%dT%H:%MZ"),
        fake.last_name_male() if gender == 'M' else fake.last_name_female(),
        random.choice(['Эконом', 'Бизнес']), random.randint(1000, 9999),
        random.choice(['Победа', 'Крузенштерн']), "РОССИЯ",
        fake.date_time_this_year().strftime("%Y-%m-%dT%H:%MZ"), "Инфофлот", fake.phone_number(),
        fake.email(), fake.user_name(), bcrypt.hashpw(bytes(fake.password(), 'utf-8'), salt),
        f'{fake.ipv4_public()} {random.choice(range(1, 9999))}',
        random.choice(["ПАО Сбербанк", "АО \"АЛЬФА-БАНК\"", "АО \"ТБанк\""]), random.randint(1000, 5000),
        fake.credit_card_number(), random.randint(1000, 9999), random.choice(['RUB', 'USD']),
        random.choice(['Эконом', 'Бизнес']), random.randint(0, 5), random.randint(0, 5)
        ]

def generate_true_ship_data():
    return generate_ship_data()

# Функция для генерации случайных данных для жд
def generate_rail_data():
    gender = random.choice(['M', 'F'])
    city_a = fake.city_name()
    city_b = fake.city_name()
    dep_time = datetime.now() - timedelta(days=random.randint(0, 28), hours=random.randint(0, 19))
    arr_date = dep_time + timedelta(hours=random.randint(0, 19))
    birthdate_is_correct = bool(random.getrandbits(1))
    if birthdate_is_correct:
        birthdate_raw = fake.date_of_birth(minimum_age=18, maximum_age=90).strftime("%Y-%m-%d")
        birthdate = birthdate_raw
    else:
        birthdate_raw = f'{random.choice(range(1950, 2020))}-XX-XX'
        birthdate = ''

    return [
        fake.last_name_male() if gender == 'M' else fake.last_name_female(),
        fake.first_name_male() if gender == 'M' else fake.first_name_female(),
        fake.middle_name_male() if gender == 'M' else fake.middle_name_female(),
        gender, birthdate_raw,
        random.randint(0, 10), fake.ssn(), city_a, city_b,
        dep_time.strftime("%Y-%m-%dT%H:%MZ"), random.randint(0, 5),
        '', random.randint(0, 19), random.randint(1, 50),
        f"{city_a} - {fake.city_name()} - {city_b}", random.randint(1, 64),
        dep_time.strftime("%Y-%m-%dT%H:%MZ"), fake.date_time_this_year().strftime("%Y-%m-%dT%H:%MZ"),
        random.randint(1, 30), random.randint(0, 1), 'RUS',
        fake.date_time_this_year().isoformat(), random.randint(1, 30),
        random.randint(1, 10), random.randint(1, 5), random.randint(1, 5),
        random.randint(1, 5), fake.phone_number(), fake.email(),
        fake.user_name(), bcrypt.hashpw(bytes(fake.password(), 'utf-8'), salt),
        f'{fake.ipv4_public()} {random.choice(range(1, 9999))}',
        random.choice(["ПАО Сбербанк", "АО \"АЛЬФА-БАНК\"", "АО \"ТБанк\""]),
        random.randint(1000, 5000), fake.credit_card_number(), random.randint(1000, 5000),
        random.choice(['RUB', 'USD']), random.choice(['Эконом', 'Бизнес'])
        ]

def generate_true_rail_data():
    gender = random.choice(['M', 'F'])
    route = {
        "operatorId": "41001", "route": "147Я", "departPlace": "2010090", "departDate": "2024-10-30T20:55Z",
        "arrivePlace": "2000002", "arriveDate": "2024-10-31T02:43Z", "operationType": random.choice([1, 2, 3, 4, 17])
    }
    city_a = route["departPlace"]
    city_b = route["arrivePlace"]
    dep_time = route["departDate"]
    arr_date = route["arriveDate"]
    birthdate_is_correct = True
    if birthdate_is_correct:
        birthdate_raw = fake.date_of_birth(minimum_age=18, maximum_age=90).strftime("%Y-%m-%d")
        birthdate = birthdate_raw
    else:
        birthdate_raw = f'{random.choice(range(1950, 2020))}-XX-XX'
        birthdate = ''

    return [
        fake.last_name_male() if gender == 'M' else fake.last_name_female(),
        fake.first_name_male() if gender == 'M' else fake.first_name_female(),
        fake.middle_name_male() if gender == 'M' else fake.middle_name_female(),
        gender, birthdate_raw,
        1, random.randint(10000000, 99999999), city_a, city_b,
        dep_time, 1,
        '', random.randint(0, 19), route["operatorId"],
        route["route"], random.randint(1, 64),
        dep_time, fake.date_time_this_year().strftime("%Y-%m-%dT%H:%MZ"),
        random.randint(1, 30), random.randint(0, 1), "RUS",
        fake.date_time_this_year().strftime("%Y-%m-%dT%H:%MZ"), random.randint(1, 10),
        random.randint(1, 10), random.randint(1, 5), random.randint(1, 5),
        random.randint(1, 5), fake.phone_number(), fake.email(),
        fake.user_name(), bcrypt.hashpw(bytes(fake.password(), 'utf-8'), salt),
        f'{fake.ipv4_public()} {random.choice(range(1, 9999))}',
        random.choice(["ПАО Сбербанк", "АО \"АЛЬФА-БАНК\"", "АО \"ТБанк\""]),
        random.randint(1000, 5000), fake.credit_card_number(), random.randint(1000, 5000),
        random.choice(['RUB', 'USD']), random.choice(['Эконом', 'Бизнес'])
    ]

# Функция для создания директории, если она не существует
def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)


# Главная функция для генерации CSV файлов
def generate_csv(subsystem, headers, rows, output_dir):
    create_directory(output_dir)
    file_name = generate_random_filename(subsystem)
    file_path = os.path.join(output_dir, file_name)
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(headers)  # Запись заголовков
        writer.writerows(rows)    # Запись данных
    return file_name


# Генерация случайных строк данных для выбранной подсистемы
def generate_random_rows(subsystem, num_rows):
    rows = []
    for _ in tqdm(range(num_rows)):
        if subsystem == 'auto':
            rows.append(generate_auto_data())
        elif subsystem == 'avia':
            rows.append(generate_avia_data())
        elif subsystem == 'ship':
            rows.append(generate_ship_data())
        elif subsystem == 'rail':
            rows.append(generate_rail_data())
        else:
            raise ValueError("Неверная подсистема")
    return rows


def generate_true_data(subsystem, num_rows):
    rows = []
    for _ in tqdm(range(num_rows)):
        if subsystem == 'auto':
            rows.append(generate_true_auto_data())
        elif subsystem == 'avia':
            rows.append(generate_true_avia_data())
        elif subsystem == 'ship':
            rows.append(generate_true_ship_data())
        elif subsystem == 'rail':
            rows.append(generate_true_rail_data())
        else:
            raise ValueError("Неверная подсистема")
    return rows


# Функция для генерации нескольких файлов
def generate_multiple_files(subsystem, num_files, num_rows, true_data):
    output_dir = os.path.join('out', subsystem)
    headers = headers_dict[subsystem]
    for _ in range(num_files):
        if true_data:
            rows = generate_true_data(subsystem, num_rows)
        else:
            rows = generate_random_rows(subsystem, num_rows)
        file_name = generate_csv(subsystem, headers, rows, output_dir)
        print(f'CSV файл {file_name} успешно создан в директории {output_dir}.')


# Пример использования
if __name__ == "__main__":
    true_data = True
    tags = ['auto', 'avia', 'ship', 'rail']  # 'auto', 'avia', 'ship', 'rail'
    num_files = 1  # Количество файлов для генерации
    num_rows = 10
    for subsystem in tags:
        generate_multiple_files(subsystem, num_files, num_rows, true_data)
