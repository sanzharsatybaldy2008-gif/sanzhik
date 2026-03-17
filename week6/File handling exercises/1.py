# Создаем текстовый файл и записываем в него строки
filename = "example.txt"

with open(filename, "w", encoding="utf-8") as f:
    f.write("Первая строка\n")
    f.write("Вторая строка\n")
    f.write("Третья строка\n")