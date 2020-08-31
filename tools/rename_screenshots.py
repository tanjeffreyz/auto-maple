import os

path = 'C:/Users/tanje/Desktop/'
images = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

i = 1
# print(images)
for img in images:
    if 'jpg' in img:
        os.rename(f'{path}{img}', f'{path}{i}.jpg')
        i += 1