# 17) Остановиться, когда сумма > 10
total = 0
for n in [3, 4, 5, 6]:
    total += n
    if total > 10:
        print("Stop, total:", total)
        break

