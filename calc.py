def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    
if __name__ == "__main__":
    print(add(5, 3))
    print(subtract(10, 4))
    print(multiply(6, 7))
    print(divide(20, 5))