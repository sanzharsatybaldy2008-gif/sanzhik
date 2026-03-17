from functools import reduce

numbers = [1, 2, 3, 4, 5]

# Найдём произведение всех чисел
product = reduce(lambda x, y: x * y, numbers)

print("Список:", numbers)
print("Произведение всех элементов:", product)
