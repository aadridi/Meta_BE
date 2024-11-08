num_list = [33, 42, 5, 66, 77, 22, 16, 79,
            36, 62, 78, 43, 88, 39, 53, 67, 89, 11]

""" for index, value in enumerate(num_list):
    if value > 45:
        print(str(index) + ")" + " Over 45 : " + str(value))
    else:
        print(str(index) + ")"+" Under 45 : " + str(value)) """

count = 0

for index, value in enumerate(num_list):
    if value == 36:
        count += 1
        print(f"Number found at position: {index}")
        break
    else:
        count += 1

print(f"Count: {count}")
