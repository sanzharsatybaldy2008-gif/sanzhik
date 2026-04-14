import os



# exist_ok=True не бросает ошибку, если папки уже есть
os.makedirs("ddd\ssss\ggg", exist_ok=True)

print(f"Созданы папки: {nested_path}")
