# 1) Словарь: три буквы -> цифра
to_digit = {
    "ZERO": "0", "ONE": "1", "TWO": "2", "THR": "3", "FOR": "4",
    "FIV": "5", "SIX": "6", "SEV": "7", "EIG": "8", "NIN": "9"
}

# 2) Обратный словарь: цифра -> три буквы
to_triplet = {v: k for k, v in to_digit.items()}


# 3) Функция: строка триплетов -> обычное число
def decode(s):
    digits = ""
    for i in range(0, len(s), 3):      # идём по строке шагом 3
        tri = s[i:i+3]                 # берём кусок из 3 букв
        digits += to_digit[tri]        # превращаем в цифру и добавляем
    return int(digits)                 # делаем из строки число


# 4) Функция: обычное число -> строка триплетов
def encode(n):
    if n == 0:
        return "ZERO"                  # особый случай для 0

    if n < 0:
        return "MIN" + encode(-n)      # если вдруг есть отрицательный ответ

    result = ""
    for ch in str(n):                  # идём по цифрам числа
        result += to_triplet[ch]       # каждую цифру превращаем в триплет
    return result


# 5) Ввод: три части через пробел (пример: ONETWOSEV + TWO)
a_str, op, b_str = input().split()

# 6) Переводим в обычные числа
a = decode(a_str)
b = decode(b_str)

# 7) Считаем
if op == "+":
    ans = a + b
elif op == "-":
    ans = a - b
else:  # "*"
    ans = a * b

# 8) Печатаем ответ триплетами
print(encode(ans))
