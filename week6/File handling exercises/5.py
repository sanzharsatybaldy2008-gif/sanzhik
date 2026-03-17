import os

filename = "example_to_delete.txt"

# Создадим файл для примера
with open(filename, "w", encoding="utf-8") as f:
    f.write("Этот файл будет удален\n")

# Проверяем, существует ли файл, прежде чем удалять
if os.path.exists(filename):
    os.remove(filename)
    print(f"Файл {filename} удалён")
else:
    print(f"Файл {filename} не найден")