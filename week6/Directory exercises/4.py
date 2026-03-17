import os
import shutil

# Создаем папки, если их нет
os.makedirs("folder1", exist_ok=True)
os.makedirs("folder2", exist_ok=True)

# Создаем файл в папке folder1
with open("folder1/file.txt", "w", encoding="utf-8") as f:
    f.write("Этот файл мы будем копировать и перемещать\n")

# Копируем файл из folder1 в folder2
shutil.copy("folder1/file.txt", "folder2/file.txt")
print("Файл скопирован из folder1 в folder2")

# Перемещаем файл из folder1 в folder2 с новым именем
shutil.move("folder1/file.txt", "folder2/moved_file.txt")
print("Файл перемещён из folder1 в folder2 с новым именем")
