# 8) Остановиться при первом отрицательном
values = [5, 2, 1, -1, 10]
i = 0
while i < len(values):
    if values[i] < 0:
        print("Stop at negative:", values[i])
        break
    i += 1