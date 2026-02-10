a, b, c=map(int, input().split())
b-=1
c-=1
list=list(map(int, input().split()))
list[b:c+1]=list[b:c+1][::-1]

print(*list)
