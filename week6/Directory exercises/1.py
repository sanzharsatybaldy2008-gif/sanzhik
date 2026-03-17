import os

nested_path = os.path.join("test_dir", "subdir1", "subdir2")

# exist_ok=True не бросает ошибку, если папки уже есть
os.makedirs(nested_path, exist_ok=True)

print(f"Созданы папки: {nested_path}")
