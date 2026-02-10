a=int(input(" "))
b=list(map(int,input().split()))
c=min(b)
for i in b:
    if b[i]==c:
        print(i)