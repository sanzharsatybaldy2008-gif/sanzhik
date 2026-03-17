filename = "example.txt"

with open(filename, "r", encoding="utf-8") as f:
    content = f.read()

print("Содержимое файла:")
print(content)