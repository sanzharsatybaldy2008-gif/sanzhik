a=int(input(" "))
b=list(map(int,input().split()))
sum=0
for i in b:
    if i>0:
        sum+=1
print(sum)