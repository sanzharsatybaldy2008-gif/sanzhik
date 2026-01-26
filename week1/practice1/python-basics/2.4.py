#  Обмен значениями переменных без временной переменной
x = "tea"
y = "coffee"
x, y = y, x
print(x, y)  # coffee tea