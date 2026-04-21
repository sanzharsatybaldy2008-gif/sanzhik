a = int(input())

if a <= 0:
    print("No")
else:
    for i in (2, 3, 5):
        while a % i == 0:
            a //= i

    if a == 1:
        print("Yes")
    else:
        print("No")