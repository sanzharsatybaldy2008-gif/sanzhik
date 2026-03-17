filename = "example.txt"

# Добавляем строки в конец файла
with open(filename, "a", encoding="utf-8") as f:
    f.write("Добавленная строка 1\n")
    f.write("Добавленная строка 2\n")

# Читаем файл, чтобы проверить
with open(filename, "r", encoding="utf-8") as f:
    content = f.read()

print("Обновленное содержимое файла:")
print(content)