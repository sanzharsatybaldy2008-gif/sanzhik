numbers = [1, 2, 3, 4, 5, 6]

# Увеличим каждое число на 10 с помощью map
plus_ten = list(map(lambda x: x + 10, numbers))

# Отфильтруем только чётные числа с помощью filter
even_numbers = list(filter(lambda x: x % 2 == 0, numbers))

print("Исходный список:", numbers)
print("Плюс 10:", plus_ten)
print("Чётные числа:", even_numbers)
