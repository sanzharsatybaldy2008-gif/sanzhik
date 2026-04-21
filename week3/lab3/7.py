import math
a, b = map(int, input().split())
d, c = map(int, input().split())
q, w = map(int, input().split())

print(f"({a}, {b})")
print(f"({d}, {c})")
d = math.sqrt((d - q) ** 2 + (w - c) ** 2)
print(f"{d:.2f}")