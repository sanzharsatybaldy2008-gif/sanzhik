# 7) Поиск числа в списке
nums = [4, 7, 9, 12]
target = 9
i = 0
while i < len(nums):
    if nums[i] == target:
        print("Found!")
        break
    i += 1