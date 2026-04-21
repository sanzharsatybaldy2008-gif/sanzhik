import shutil

source = "example.txt"
backup = "example_backup.txt"

# Копируем файл
shutil.copy(source, backup)

print(f"Файл {source} скопирован в {backup}")