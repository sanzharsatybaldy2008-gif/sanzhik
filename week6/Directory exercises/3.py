import os

path = "."
extension = ".txt"

print(f"Файлы с расширением {extension} в {path}:")
for name in os.listdir(path):
    if name.endswith(extension) and os.path.isfile(os.path.join(path, name)):
        print(name)
