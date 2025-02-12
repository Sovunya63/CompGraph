import numpy as np
from PIL import Image, ImageOps

def open_v(filename):
    arr = []
    with open("model_1.obj", "r") as file:
        for line in file:
            parts = line.strip().split()
            if parts and parts[0] == 'v':
                x = float(parts[1])
                y = float(parts[2])
                z = float(parts[3])
                arr.append([x, y, z])

arr_v = open_v("model_1.obj")
pixels = np.zeros((1000, 1000), dtype= np.uint8)
for v in arr_v:
    x_new = int(5000*v[0] + 500)
    y_new = int(5000*v[1] + 250)
    pixels[y_new, x_new] = 255

img = Image.fromarray(pixels, mode='L')
img = ImageOps.flip(img)
img.save("draw1.png")

