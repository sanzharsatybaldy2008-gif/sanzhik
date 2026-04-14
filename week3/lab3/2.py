a=int(input(" "))
sum=0
for i in range(1,10):
    if a%i==0:
        sum+=1
if sum<3:    
    print("Yes")
else:
    print("No")
        