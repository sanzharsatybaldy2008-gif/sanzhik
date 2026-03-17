names = ["Alice", "Bob", "Charlie"]
scores = [90, 75, 88]

print("С enumerate:")
for index, name in enumerate(names, start=1):
    print(f"{index}. {name}")

print("\nС zip:")
for name, score in zip(names, scores):
    print(f"{name}: {score}")
