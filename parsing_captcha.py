#!/usr/bin/env python
# -*- coding: utf-8 -*-


__author__ = 'ipetrash'


"""Скрипт разбирает капчи. Пример капч в папке test_captcha.

Алгоритм разбора не умеет разбирать буквы, которые по вертикали не имеет просветов.
Решением может быть улучшение алгоритма поиска просветов в функции border_letters или
добавлением масок "слипшихся" букв.
"""


from PIL import Image
import hashlib
import os
import random


BLACK_PXL = 0
WHITE_PXL = 255


def clear_captcha(im):
    """Функция очищает капчу от ненужного, оставляя только текст"""
    # Т.к. исходные капчи имеет всегда одинаковый цвет текста -- черный,
    # то очищение капчи будет таким простым

    w, h = im.size


    for x in range(w):
        for y in range(h):
            pxl = im.getpixel((x, y))

            # Все пиксели, отличающиеся от черного, закрашивают белым
            if pxl != BLACK_PXL:
                im.putpixel((x, y), WHITE_PXL)


def get_margins(im):
    """Функция для определения границ слова капчи"""

    w, h = im.size
    left, right, top, bottom = w, -1, h, -1

    for y in range(h):
        for x in range(w):
            pxl = im.getpixel((x, y))

            if pxl == BLACK_PXL:
                if left > x:
                    left = x

                if right < x:
                    right = x

                if top > y:
                    top = y

                if bottom < y:
                    bottom = y

    return left, right, top, bottom


def crop_captcha_text(im):
    """Функция вырезает из изображения текст капчи и возвращает его копию"""

    left, right, top, bottom = get_margins(im)
    return im.crop((left, top, right+1, bottom+1))


def border_letters(im):
    """Функция ищет просветы между буквами и возвращает координаты границ.
    Между двумя буквами вернется один и первый попавшийся просвет"""

    # Разделить на части
    w, h = im.size

    # Бывает, просвет между буквами больше одного пикселя
    # и чтобы у нас не набрались несколько координат просветов
    # между двумя буквами, а нам нужно только одну координату,
    # мы заводим флаг, который при нахождении просвета будет
    # возведен, а при встрече первого черного пикселя (дошли
    # до буквы) опущен
    multi_line = False

    lines = []

    # Ищем просветы между буквами
    for x in range(w):
        line = True

        for y in range(h):
            pxl = im.getpixel((x, y))

            # Если наткнулись на черный пиксель, значит
            # тут не просвета, выходим из цикла
            if pxl == BLACK_PXL:
                line = False
                multi_line = False
                break

        if line and not multi_line:
            multi_line = True
            lines.append(x)

    return lines


def get_letters_from_captcha(im):
    """Функция находит просветы между буквами капчи и вырезает буквы,
    предварительно обрезав вокруг каждой буквы фон, после функция
    вернет список изображений букв"""

    lines = border_letters(im)

    w, h = im.size

    # left -- просвет слева, для первой буквы будет равен 0
    left = 0
    top = 0
    bottom = h

    # Границей последней буквы будет ширина капчи
    lines.append(w)

    # Список для хранения букв капчи
    letters = []

    for line in lines:
        # right - просвет справа
        right = line

        # Вырезаем букву
        letter_im = im.crop((left, top, right, bottom))

        # Убираем белый фон вокруг буквы
        letter_im = crop_captcha_text(letter_im)

        letters.append(letter_im)

        # Для следующей буквы сдвигаем просвет слева
        # до просвета справа текущей буквы
        left = right

    return letters


def get_hash_mask_letter(letter_im):
    """Функция возвращает хеш маски изображения буквы."""

    str_bitarr = []
    w, h = letter_im.size

    for y in range(h):
        for x in range(w):
            pxl = letter_im.getpixel((x, y))

            # Если пиксель черный добавим в список '1', иначе '0'
            str_bitarr.append('1' if pxl == BLACK_PXL else '0')

    # Получим маску
    mask = ''.join(str_bitarr)

    # Подсчитаем хеш маски и будем по хешу определять буквы капчи
    hash = hashlib.new('md5')
    hash.update(mask.encode())
    hash_mask = hash.hexdigest()

    return hash_mask


# Словарь, содержащий маски хешей изображений букв и сами буквы
# Найден опытным путем: прогонялись две сотни капч, из которых
# вытаскивались хеши масок и по маскам определялись буквы
HASH_MASK_LETTER_DICT = {
    "7ba728b17d0dd314c1eecc66284daf37": "A",
    "6283d9c23c6b515433815b6cb6829e34": "B",
    "1b70a9bff56e75b3e9f4d2e7180a0441": "C",
    "3a4ef53d006b67d38a28fbe8f5794358": "D",
    "3d2ac5829a84647df1abcd9c8fe19d8b": "E",
    "3e5ecb02e62a8201a0c2db6134f1e139": "F",
    "aac27e01ba133489d81582dc9d30abb7": "G",
    "6fc200aedf3a9e043cea5893f19cceca": "H",
    "51bea0b4ab303e156dc72111e037770b": "I",
    "6ce2a6f9ba3c39bc38332ddceb57d4eb": "J",
    "a29c1c3da66a63d6c0a9c19650f9792b": "K",
    "0cc7f120e0e00ba9f3820082b818773f": "L",
    "6f68a3614889143147aabe7ab40596d6": "M",
    "5c3a50e8032f71a7c1853ac64375a0d5": "N",
    "ab14f3a642ad93a1addca8dfbbc0bf1d": "O",
    "b6c2c178141188af4325e513b61f3186": "P",
    "caf1e72e0de321b87b995be56b5428fa": "Q",
    "22081721c151c7220dc3c519851644f9": "R",
    "4a4d9f994df5f73fa36ec7ca9845d953": "S",
    "9ca22a4731f80b825dd8307e82e880e0": "T",
    "fd9c862d8e93d643d5e62c56fdedafc2": "U",
    "3ae4ba4eaee39a683b465a947ba25984": "V",
    "9153be325aed7b8ea5d012a567671241": "W",
    "6cad4a539ff55a5d8d77ebcb5de89ba4": "X",
    "2866615d49116e804db8efec0e101e35": "Y",
    "17c3f4930f0ad27afc1396bb13406a2a": "Z"
}


if __name__ == '__main__':
    DIR = 'test_captcha'

    # Случайный файл капчи из папки test_captcha
    random_captcha = random.choice(os.listdir(DIR))

    file_name = DIR + '/' + random_captcha

    # Открытие изображения
    im = Image.open(file_name)
    # im.show()

    # Конвертирование в монохромный режим
    im = im.convert('L')

    # Очищение капчи
    clear_captcha(im)

    # Обрезание текста капчи
    im = crop_captcha_text(im)

    # Список букв капчи
    letters_captcha = get_letters_from_captcha(im)

    # Итоговый текст капчи
    captcha_text = ''

    # Перебор изображений букв капч
    for letter in letters_captcha:
        # Получаем маску буквы капчи
        hash_mask = get_hash_mask_letter(letter)

        # Если маска есть в словаре
        if hash_mask in HASH_MASK_LETTER_DICT:
            captcha_text += HASH_MASK_LETTER_DICT[hash_mask]
        else:
            captcha_text += "-"

    print('{}: "{}"'.format(file_name, captcha_text))