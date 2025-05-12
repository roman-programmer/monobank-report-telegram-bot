import telebot
from telebot import types
import requests
import datetime
import pytz
import threading
import schedule
import time

bot = telebot.TeleBot('...')

# Заголовки, включаючи ваш X-Token
headers = {
    "X-Token": "..."
}

# Функція для постійного перевіряння часу і виконання запланованих завдань
def schedule_checker():
    while True:
        schedule.run_pending()
        time.sleep(1)  # Перевіряє щосекунди

# Запускаємо планувальник у новому потоці
threading.Thread(target=schedule_checker).start()

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, f"Ваш chat_id: {chat_id}")
    mess = f"Привіт, <b>{message.from_user.first_name} {message.from_user.last_name}</b>"
    bot.send_message(message.chat.id, mess, parse_mode='html')

@bot.message_handler(commands=['day_zvit'])
def day_zvit(message):
    # Отримуємо поточний час для Києва
    kyiv_tz = pytz.timezone('Europe/Kyiv')
    # Поточний час
    kyiv_time = datetime.datetime.now(kyiv_tz)
    # Початок дня (00:00) у Києві
    start_of_day = datetime.datetime(kyiv_time.year, kyiv_time.month, kyiv_time.day, 0, 0, 0, tzinfo=kyiv_tz)
    # Кінець дня (23:59:59)
    end_of_day = datetime.datetime(kyiv_time.year, kyiv_time.month, kyiv_time.day, 23, 59, 59, tzinfo=kyiv_tz)
    # Переводимо в Unix-формат
    start_of_day_unix = int(start_of_day.timestamp())
    end_of_day_unix = int(end_of_day.timestamp())

    # URL для запиту (з прикладу)
    url = "https://api.monobank.ua/...".format(start_of_day_unix)

    # Виконання GET-запиту
    response = requests.get(url, headers=headers)

    bot.send_message(message.chat.id, f"Ось звіт за {kyiv_time.day}.{kyiv_time.month}.{kyiv_time.year}", parse_mode='html')

    mess = ''
    
    if response.status_code == 200:
        # Отримання списку операцій
        list = response.json()
        
        # Заголовок таблиці
        mess = "`Опис\t\t\tСума\t\tТип\t\tЧас`\n"
        mess += "`-----------------------------------------------`\n"
        
        # Формування рядків таблиці
        for i in list:    
            order_time = datetime.datetime.fromtimestamp(i['time'])
            formatted_date = order_time.strftime("%H:%M %d.%m.%Y")
            
            if i['mcc'] == 5499:
                type = 'ПРОДУКТИ'
            else:
                type = 'інше'
            
            # Форматування з використанням табуляції та шрифтів
            mess += f"`{i['description'][:15]:<15}\t{i['amount']/100:<8}\t{type:<10}\t{formatted_date}`\n"
        
        # Відправка повідомлення у форматі з моноширинним шрифтом
        bot.send_message(message.chat.id, mess, parse_mode='Markdown')
        
        # Виведення залишку
        balance_msg = f"Баланс: {list[0]['balance']/100}"
        bot.send_message(message.chat.id, balance_msg, parse_mode='html')

    else:
        bot.send_message(message.chat.id, f"Запит не вдався: {response.status_code}", parse_mode='html')

@bot.message_handler(commands=['month_zvit'])
def month_zvit(message):
    month_zvit_auto()

def month_zvit_auto():
    chat_id = 592634246
    # Отримуємо поточний час для Києва
    kyiv_tz = pytz.timezone('Europe/Kyiv')
    # Поточний час
    kyiv_time = datetime.datetime.now(kyiv_tz)
    # Перший день поточного місяця
    start_of_month = datetime.datetime(kyiv_time.year, kyiv_time.month, 1, 0, 0, 0, tzinfo=kyiv_tz)
    # Останній день поточного місяця
    # Визначаємо наступний місяць і потім беремо перший день наступного місяця
    next_month = kyiv_time.month % 12 + 1
    next_month_year = kyiv_time.year + (kyiv_time.month // 12)
    end_of_month = datetime.datetime(next_month_year, next_month, 1, 0, 0, 0, tzinfo=kyiv_tz) - datetime.timedelta(seconds=1)
    # Переводимо в Unix-формат
    start_of_month_unix = int(start_of_month.timestamp())
    end_of_month_unix = int(end_of_month.timestamp())
    # URL для запиту (з прикладу)
    url = "https://api.monobank.ua/...".format(start_of_month_unix)

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        bot.send_message(chat_id, f"Ось звіт за {kyiv_time.month}.{kyiv_time.year}", parse_mode='html')

        list = response.json()
        
        mcc_products = ['5441', '5921', '5411', '5412', '5451', '5422', '5297', '5298', '5331', '5715', '5300', '5462', '5399', '5499', '5311']
        products_title = "Продукти"
        PRODUCTS = 0

        mcc_car_azs = ['7523', '5541', '5542', '5511', '7531', '7534', '7535', '7538', '5172', '7542', '7511', '5531', '5532', '5533', '7549', '5983']
        car_azs_title = "Авто/АЗС"
        CARAZS = 0

        mcc_apteka = ['5122', '5292', '5295', '5912']
        apteka_title = "Аптека"
        APTEKA = 0

        mcc_cinema = ['7829', '7832', '7841', ]
        cinema_title = "Кіно"
        CINEMA = 0

        mcc_books = ['2741', '5111', '5192', '5942', '5994']
        books_title = "Книги"
        BOOKS = 0

        mcc_wear = ['5948', '5699', '5691', '5651', '5621', '5611', '5137']
        wear_title = 'Одяг'
        WEAR = 0

        mcc_tehnika = ['4812', '5722', '5732', '5946']
        tehnika_title = 'Техніка'
        TEHNIKA = 0

        mcc_flowers = ['5992', '0708', '5261', '5193']
        flowers_title = 'Квіти'
        FLOWERS = 0

        mcc_taxi = ['4121']
        taxi_title = 'Таксі'
        TAXI = 0

        mcc_shoes = ['5139', '5661']
        shoes_title = 'Взуття'
        SHOES = 0

        other_title = 'Інше'
        OTHER = 0

        DOHID = 0

        for i in list:
            i['amount'] /= 100
            if i['amount'] < 0:
                i['amount'] *= -1
                if str(i['mcc']) in mcc_products:
                    PRODUCTS += i['amount']

                elif str(i['mcc']) in mcc_car_azs:
                    CARAZS += i['amount']
                
                elif str(i['mcc']) in mcc_apteka:
                    APTEKA += i['amount']
                
                elif str(i['mcc']) in mcc_cinema:
                    CINEMA += i['amount']
                
                elif str(i['mcc']) in mcc_books:
                    BOOKS += i['amount']
                
                elif str(i['mcc']) in mcc_wear:
                    WEAR += i['amount']
                
                elif str(i['mcc']) in mcc_tehnika:
                    TEHNIKA += i['amount']

                elif str(i['mcc']) in mcc_flowers:
                    FLOWERS += i['amount']

                elif str(i['mcc']) in mcc_taxi:
                    TAXI += i['amount']

                elif str(i['mcc']) in mcc_shoes:
                    SHOES += i['amount']

                else:
                    OTHER += i['amount']
            else:
                DOHID += i['amount']
          
        mess = ''
        mess = mess + "\nВитрати:\n"
        if PRODUCTS > 0:
            mess = mess + f"Категорія {products_title}. Витрачено: {PRODUCTS}грн\n"
        if CARAZS > 0:
            mess = mess + f"Категорія {car_azs_title}. Витрачено: {CARAZS}грн\n"
        if APTEKA > 0:
            mess = mess + f"Категорія {apteka_title}. Витрачено: {APTEKA}грн\n"
        if CINEMA > 0:
            mess = mess + f"Категорія {cinema_title}. Витрачено: {CINEMA}грн\n"
        if BOOKS > 0:
            mess = mess + f"Категорія {books_title}. Витрачено: {BOOKS}грн\n"
        if WEAR > 0:
            mess = mess + f"Категорія {wear_title}. Витрачено: {WEAR}грн\n"
        if TEHNIKA > 0:
            mess = mess + f"Категорія {tehnika_title}. Витрачено: {TEHNIKA}грн\n"
        if FLOWERS > 0:
            mess = mess + f"Категорія {flowers_title}. Витрачено: {FLOWERS}грн\n"
        if TAXI > 0:
            mess = mess + f"Категорія {taxi_title}. Витрачено: {TAXI}грн\n"
        if SHOES > 0:
            mess = mess + f"Категорія {shoes_title}. Витрачено: {SHOES}грн\n"
        if OTHER > 0:
            mess = mess + f"Категорія {other_title}. Витрачено: {OTHER}грн\n"

        mess = mess + F"\nВсього витрачено: {int(PRODUCTS+CARAZS+APTEKA+CINEMA+BOOKS+WEAR+TEHNIKA+FLOWERS+TAXI+SHOES+OTHER)}грн за цей місяць.\n"

        if DOHID > 0:
            mess = mess + "\n\nДохід:\n"
            mess = mess + f"Отримано всього: {DOHID}грн\n"
         
        bot.send_message(chat_id, mess, parse_mode='html')
    else:
        print(f"Запит не вдався: {response.status_code} - {response.text}")

schedule.every().day.at("22:30").do(month_zvit_auto)




@bot.message_handler(commands=['help'])
def help(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    zvit = types.KeyboardButton("/day_zvit")
    start = types.KeyboardButton("Start")
    markup.add(zvit, start)
    bot.send_message(message.chat.id, "Перейдіть на сторінку", reply_markup=markup)

bot.polling(non_stop=True)
