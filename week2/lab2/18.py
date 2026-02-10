n = int(input())
pos = {}

for i in range(1, n + 1):
    s = input()
    if s not in pos:
        pos[s] = i

for key in sorted(pos):
    print(key, pos[key])
