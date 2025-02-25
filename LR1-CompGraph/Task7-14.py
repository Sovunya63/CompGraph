import numpy as np
from PIL import Image, ImageOps
from random import randrange

def barycentric_coordinates(x0, y0, x1, y1, x2, y2, x, y):
    lambda0 = ((x - x2) * (y1 - y2) - (x1 - x2) * (y - y2)) / ((x0 - x2) * (y1 - y2) - (x1 - x2) * (y0 - y2))
    lambda1 = ((x0 - x2) * (y - y2) - (x - x2) * (y0 - y2)) / ((x0 - x2) * (y1 - y2) - (x1 - x2) * (y0 - y2))
    lambda2 = 1.0 - lambda0 - lambda1
    return lambda0, lambda1, lambda2

#mass = (-100, 100, 100, 0, 100, 100)
#mass = (-100, -100, 100, 100, -100, 100)
#x0, y0, x1, y1, x2, y2 = mass[0], mass[1], mass[2], mass[3], mass[4], mass[5]
#print(mass)

def max_x_y(x0, y0, x1, y1, x2, y2):
    return int(max(x0, x1, x2)), int(max(y0, y1, y2))

def min_x_y(x0, y0, x1, y1, x2, y2):
    xmin = int(min(x0, x1, x2))
    if (xmin < 0) : xmin = 0
    ymin = int(min(y0, y1, y2))
    if (ymin < 0) : ymin = 0
    return xmin, ymin

#mass = max_x_y(5.5, -1.2, 2.4, 10.3, 10.6, 6.7)
#mass1 = min_x_y(5.5, -1.2, 2.4, 10.3, 10.6, 6.7)

#print(mass)
#print(mass1)

def draw_pixel(x0, y0, z0, x1, y1, z1, x2, y2, z2, min_cor, max_cor, res, n):
    #color = (randrange(0, 255), randrange(0, 255), randrange(0, 255))
    color = (0, -215 * n[2], -12 * n[2])
    for i in range(min_cor[0], max_cor[0]+1):
        for j in range(min_cor[1], max_cor[1] + 1):
            mass = barycentric_coordinates(x0, y0, x1, y1, x2, y2, i, j)
            if mass[0] >= 0 and mass[1] >= 0 and mass[2] >= 0:
                z = z0 * mass[0] + z1 * mass[1] + z2 * mass[2]
                if z > z_buf[i][j]:
                    continue
                z_buf[i][j] = z
                res[i][j] = color
    return res

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

def calculate_triangle_normal(v0, v1, v2):
  v0 = np.array(v0)
  v1 = np.array(v1)
  v2 = np.array(v2)

  v1_v0 = v1 - v0
  v2_v0 = v2 - v0

  n = np.cross(v1_v0, v2_v0)
  n /= np.linalg.norm(n)
  return n

arr_v = open_v("model_1.obj")
arr_f = open_f("model_1.obj")
res = np.zeros((1000, 1000, 3), dtype=np.uint8)
res[...] = 255
z_buf = np.full((1000, 1000), 10000, dtype=np.float32)

for i in arr_f:

    x0, y0, z0 = arr_v[i[0]-1][0], arr_v[i[0]-1][1], arr_v[i[0]-1][2]
    v0 = (x0, y0, z0)
    x1, y1, z1 = arr_v[i[1]-1][0], arr_v[i[1]-1][1], arr_v[i[1]-1][2]
    v1 = (x1, y1, z1)
    x2, y2, z2 = arr_v[i[2] - 1][0], arr_v[i[2] - 1][1], arr_v[i[2]-1][2]
    v2 = (x2, y2, z2)
    normal = calculate_triangle_normal(v0, v1, v2)
    if normal[2] > 0:
        continue
    x0, y0, z0 = 5000 * arr_v[i[0] - 1][0] + 500, 5000 * arr_v[i[0] - 1][1] + 250, 5000 * arr_v[i[0] - 1][2] + 500
    x1, y1, z1 = 5000 * arr_v[i[1] - 1][0] + 500, 5000 * arr_v[i[1] - 1][1] + 250, 5000 * arr_v[i[1] - 1][2] + 500
    x2, y2, z2 = 5000 * arr_v[i[2] - 1][0] + 500, 5000 * arr_v[i[2] - 1][1] + 250, 5000 * arr_v[i[2] - 1][2] + 500
    min_cor = min_x_y(x0, y0, x1, y1, x2, y2)
    max_cor = max_x_y(x0, y0, x1, y1, x2, y2)
    pixels = draw_pixel(x0, y0, z0, x1, y1, z1, x2, y2, z2, min_cor, max_cor, res, normal)

img = Image.fromarray(pixels, mode='RGB')
img = img.rotate(90)
img.save("polyg10.png")