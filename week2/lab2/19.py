n = int(input())
d = {}

for _ in range(n):
    s, k = input().split()
    d[s] = d.get(s, 0) + int(k)

for s in sorted(d):
    print(s, d[s])
