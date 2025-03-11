import numpy as np
from PIL import Image
import math

def barycentric_coordinates(x0, y0, x1, y1, x2, y2, x, y):
    lambda0 = ((x - x2) * (y1 - y2) - (x1 - x2) * (y - y2)) / ((x0 - x2) * (y1 - y2) - (x1 - x2) * (y0 - y2))
    lambda1 = ((x0 - x2) * (y - y2) - (x - x2) * (y0 - y2)) / ((x0 - x2) * (y1 - y2) - (x1 - x2) * (y0 - y2))
    lambda2 = 1.0 - lambda0 - lambda1
    return lambda0, lambda1, lambda2

def max_x_y(x0, y0, x1, y1, x2, y2):
    xmax = int(max(x0, x1, x2)) + 1
    if (xmax > 1000) : xmax = 1000
    ymax = int(max(y0, y1, y2)) + 1
    if (ymax > 1000) : ymax = 1000
    return xmax, ymax

def min_x_y(x0, y0, x1, y1, x2, y2):
    xmin = int(min(x0, x1, x2))
    if (xmin < 0) : xmin = 0
    ymin = int(min(y0, y1, y2))
    if (ymin < 0) : ymin = 0
    return xmin, ymin

def draw_pixel(x0, y0, z0, x1, y1, z1, x2, y2, z2, res, n):
    color = (0, -215 * n[2], -12 * n[2])
    px0, py0, px1, py1, px2, py2 = zoom(x0, y0, z0, x1, y1, z1, x2, y2, z2)
    min_cor = min_x_y(px0, py0, px1, py1, px2, py2)
    max_cor = max_x_y(px0, py0, px1, py1, px2, py2)
    for i in range(min_cor[0], max_cor[0]):
        for j in range(min_cor[1], max_cor[1]):
            mass = barycentric_coordinates(px0, py0, px1, py1, px2, py2, i, j)
            if mass[0] >= 0 and mass[1] >= 0 and mass[2] >= 0:
                z = z0 * mass[0] + z1 * mass[1] + z2 * mass[2]
                if z > z_buf[j][i]:
                    continue
                z_buf[j][i] = z
                res[j][i] = color
    return res

def open_v(filename):
    arr = []
    with open(filename, "r") as file:
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
    with open(filename, "r") as file:
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

def rotate(arr):
    a = math.radians(30)
    b = math.radians(230)
    c = math.radians(180)
    rotation_matrix_x = np.array([[1, 0, 0],
                                  [0, np.cos(a), np.sin(a)],
                                  [0, -np.sin(a), np.cos(a)]])
    rotation_matrix_y = np.array([[np.cos(b), 0, np.sin(b)],
                                  [0, 1, 0],
                                  [-np.sin(b), 0, np.cos(b)]])
    rotation_matrix_z = np.array([[np.cos(c), np.sin(c), 0],
                                  [-np.sin(c), np.cos(c), 0],
                                  [0, 0, 1]])
    arr = np.dot(np.array(arr), rotation_matrix_z)
    arr = np.dot(np.array(arr), rotation_matrix_y)
    arr = np.dot(np.array(arr), rotation_matrix_x)
    arr[...] = arr + np.array([0.02, 0.05, 0.3])
    return arr

def zoom(x0, y0, z0, x1, y1, z1, x2, y2, z2):
    n = 3500
    px0, py0 = n*x0/z0 + 500, n*y0/z0 + 500
    px1, py1 = n*x1/z1 + 500, n*y1/z1 + 500
    px2, py2 = n*x2/z2 + 500, n*y2/z2 + 500
    return px0, py0, px1, py1, px2, py2

arr_v = rotate(open_v("model_1.obj"))
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
    pixels = draw_pixel(x0, y0, z0, x1, y1, z1, x2, y2, z2, res, normal)

img = Image.fromarray(pixels, mode='RGB')
img.save("rot12.png")