def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b, c):
    return a * b * c

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    
def pow(x, n):
    return x ** n 
 
if __name__ == "__main__":
    print(add(5, 3))
    print(subtract(10, 4))
    print(multiply(6, 7, 8))
    print(divide(20, 5))
    print(pow(5, 3))