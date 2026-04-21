n = abs(int(input()))
if n == 0:
    print("Valid")
else:
    valid = True
    while n > 0:
        digit = n % 10
        if digit % 2 != 0:
            valid = False
            break
        n //= 10

    print("Valid" if valid else "Not valid")