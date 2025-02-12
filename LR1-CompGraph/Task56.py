import numpy as np
from PIL import Image, ImageOps

def bresenham(image, x0, y0, x1, y1, color):
    xchange = False
    if (abs(x0 - x1) < abs(y0 - y1)):
        x0, y0 = y0, x0
        x1, y1 = y1, x1
        xchange = True

    if (x0 > x1):
        x0, x1 = x1, x0
        y0, y1 = y1, y0

    x0 = int(x0)
    x1 = int(x1)
    y = int(y0)
    dy = 2*abs(y1 - y0)
    derror = 0.0
    y_update = 1 if y1 > y0 else -1
    for x in range (x0, x1):
        if (xchange):
            image[x, y] = color
        else:
            image[y, x] = color
        derror += dy
        if (derror > (x1 - x0)):
            derror -= 2 * (x1 - x0)
            y += y_update

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
    return arr

def open_f(filename):
    arr_f = []
    with open("model_1.obj", "r") as file:
        for line in file:
            parts = line.strip().split()
            if parts and parts[0] == 'f':
                num = [int(part.split('/')[0]) for part in parts[1:]]
                arr_f.append(num)
    return arr_f

lines = np.zeros((1000, 1000), dtype= np.uint8)
color = 255
arr_v = open_v("model_1.obj")
arr_f = open_f("model_1.obj")

# a = 0
# for v in arr_f:
#     a += 1
#     print(v[0], v[1], v[2])
#     if a == 10 : break

for i in arr_f:
    x0, y0 = 5000*arr_v[i[0]-1][0] + 500, 5000*arr_v[i[0]-1][1] + 500
    x1, y1 = 5000*arr_v[i[1]-1][0] + 500, 5000*arr_v[i[1]-1][1] + 500
    x2, y2 = 5000 * arr_v[i[2] - 1][0] + 500, 5000 * arr_v[i[2] - 1][1] + 500
    bresenham(lines, x0, y0, x1, y1, color)
    bresenham(lines, x0, y0, x2, y2, color)
    bresenham(lines, x2, y2, x1, y1, color)

img = Image.fromarray(lines, mode='L')
img = ImageOps.flip(img)
img.save("draw2.png")

