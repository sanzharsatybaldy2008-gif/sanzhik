class Shape():
    def area(self):
        return 0

class Square(Shape):
    def __init__(self, length):
        self.length = length
    
    def area(self):
        return self.length * self.length

l = int(input())

s = Square(l)
print(s.area())