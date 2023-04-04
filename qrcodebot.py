import telebot
from telebot import types
import qrcode
import os
from pyzbar import pyzbar
import cv2


bot = telebot.TeleBot('')


#Тут начинается работа бота. Здесь представлено приветсвенное сообщение и кнопки для работы с ботом
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Разобрать QR")
    btn2 = types.KeyboardButton("Создать QR")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, 'Вас приветсвует QRCodebot. Используя этого бота вы можете создавать QR и читать QR . Для начала работы с ботом вам нужно написать "Разобрать QR" или "Создать QR". Вы также можете нажать на соответсвующую кнопки. ', parse_mode='html', reply_markup=markup)
    del message.chat.id

#Тут пересылаются в необходимые функции в зависимости от набранного сообщения или нажатой кнопки
@bot.message_handler()
def get_users_text(message):
    if message.text == 'Разобрать QR':
        bot.send_message(message.chat.id, "Скидывай картинку", parse_mode='html')
        bot.register_next_step_handler(message, decode)
    elif message.text == 'Создать QR':
        bot.send_message(message.chat.id, "Скидывайте текст, что нужно поместить в qr", parse_mode='html')
        bot.register_next_step_handler(message, qr)
    else:
        bot.send_message(message.chat.id, 'Я Вас не понимаю, прошу следовать инструкциям', parse_mode='html')
    del message.chat.id

#Тут происходит создание QR-кода
def qr(message):
    data = message.text
    if data:
        if len(list(data))>=3000:
            bot.send_message(message.chat.id, 'Извините, я не способен создавать QR из сообщение, содержащие 3 тысяч символов и больше😢', parse_mode='html')
        elif len(list(data)) <3000:
            filename = message.from_user.first_name + '.png'
            img = qrcode.make(data)
            img.save(filename)
            photo = open(filename, 'rb')
            bot.send_photo(message.chat.id, photo)
            photo.close()
            os.remove(filename)
            del filename, data, photo, img
    else:
        bot.send_message(message.chat.id, 'Извините, но Вы отправили не текст, прошу следовать инструкциям', parse_mode='html')


#Тут происходит декодирование QR-кода
@bot.message_handler(content_types=['photo'])
def decode(message):
    if message.photo:
        fileID = message.photo[-1].file_id
        file_info = bot.get_file(fileID)
        photoname = message.from_user.first_name + '.png'
        downloaded_file = bot.download_file(file_info.file_path)
        with open(photoname, 'wb') as new_file:
            new_file.write(downloaded_file)
        img_qrcode = cv2.imread(photoname)
        data = pyzbar.decode(img_qrcode)
        if data:
            bot.send_message(message.chat.id, data, parse_mode='html')
        else:
            bot.send_message(message.chat.id, "Извините, на я не нашел QR-кода", parse_mode='html')
    else:
        bot.send_message(message.chat.id, "Извините, но Вы отправили не фото, прошу следовать инструкциям", parse_mode='html')
    os.remove(photoname)


bot.polling(none_stop=True)