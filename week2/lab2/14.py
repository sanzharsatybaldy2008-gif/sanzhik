a=int(input())
list=list(map(int, input().split()))
maxcnt=0
max=list[0]

for i in range(a):
    cnt=0
    for j in range(a):  
                       
        if list[i]==list[j]:
            cnt+=1 
                   
    if cnt>maxcnt or (cnt==maxcnt and list[i]<max):
        
        maxcnt=cnt 
        max=list[i] 
print(max)
