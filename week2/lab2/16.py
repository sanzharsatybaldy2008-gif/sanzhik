a=int(input())
list=(list(map(int, input().split())))
s=set() 

for i in list:
    if i not in s:
        print("YES")
        s.add(i)
    else:
        print("NO")
