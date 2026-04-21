import os

path = "."

items = os.listdir(path)

print(f"Содержимое директории {path}:")
for name in items:
    print(name)
