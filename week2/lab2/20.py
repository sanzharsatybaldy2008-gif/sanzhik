import sys
input = sys.stdin.readline 

n = int(input())
doc = {}

for _ in range(n):
    command = input().split()
    if command[0] == "set":
        doc[command[1]] = command[2]
    else:  
        key = command[1]
        if key in doc:
            print(doc[key])
        else:
            print(f"KE: no key {key} found in the document")