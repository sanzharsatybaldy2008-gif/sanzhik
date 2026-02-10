a=int(input(" "))
if a%4==0 or a%400==0 or a%100==1:
    print("YES")
else:
    print("NO")