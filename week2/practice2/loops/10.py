# 10) break с условием
n = 1
while n < 100:
    if n * n > 50:
        print("First square > 50:", n, n*n)
        break
    n += 1