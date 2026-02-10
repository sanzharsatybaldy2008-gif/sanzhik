n = int(input())
freq = {}

for i in range(n):
    num = input()
    if num in freq:
        freq[num] += 1
    else:
        freq[num] = 1

count = 0
for v in freq.values():
    if v == 3:
        count += 1

print(count)
