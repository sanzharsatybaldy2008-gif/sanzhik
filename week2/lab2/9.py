n = int(input())
a = list(map(int, input().split()))

mn = min(a)
mx = max(a)

for i in range(n):
    if a[i] == mx:
        a[i] = mn

print(*a)
