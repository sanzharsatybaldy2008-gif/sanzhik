class StringHandler:
    
    def getString(self):
        self.text = input()
    
    def printString(self):
        print(self.text.upper())


# использование
obj = StringHandler()
obj.getString()
obj.printString()
