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
    if (xmax > 1000): xmax = 1000
    ymax = int(max(y0, y1, y2)) + 1
    if (ymax > 1000): ymax = 1000
    return xmax, ymax

def min_x_y(x0, y0, x1, y1, x2, y2):
    xmin = int(min(x0, x1, x2))
    if (xmin < 0): xmin = 0
    ymin = int(min(y0, y1, y2))
    if (ymin < 0): ymin = 0
    return xmin, ymin

def calculate_triangle_normal(v0, v1, v2):
    v0 = np.array(v0)
    v1 = np.array(v1)
    v2 = np.array(v2)

    v1_v0 = v1 - v0
    v2_v0 = v2 - v0

    n = np.cross(v1_v0, v2_v0)
    n /= np.linalg.norm(n)
    return n

def calculate_vertex_normals(vertices, faces):
    vertex_normals = np.zeros((len(vertices), 3))
    vertex_faces = [[] for _ in range(len(vertices))]

    for face in faces:
        v0 = face[0] - 1
        v1 = face[1] - 1
        v2 = face[2] - 1
        normal = calculate_triangle_normal(vertices[v0], vertices[v1], vertices[v2])
        vertex_faces[v0].append(normal)
        vertex_faces[v1].append(normal)
        vertex_faces[v2].append(normal)

    for i in range(len(vertices)):
        if vertex_faces[i]:
            avg_normal = np.mean(vertex_faces[i], axis=0)
            avg_normal /= np.linalg.norm(avg_normal)
            vertex_normals[i] = avg_normal

    return vertex_normals

def draw_pixel_textured(x0, y0, z0, n0, tx0, ty0, x1, y1, z1, n1, tx1, ty1, x2, y2, z2, n2, tx2, ty2, res, z_buf, texture):
    px0, py0, px1, py1, px2, py2 = zoom(x0, y0, z0, x1, y1, z1, x2, y2, z2)
    min_cor = min_x_y(px0, py0, px1, py1, px2, py2)
    max_cor = max_x_y(px0, py0, px1, py1, px2, py2)

    light_dir = np.array([0, 0, 1])
    I0 = max(0, np.dot(n0, light_dir))
    I1 = max(0, np.dot(n1, light_dir))
    I2 = max(0, np.dot(n2, light_dir))

    texture_width, texture_height = texture.shape[1], texture.shape[0]

    for i in range(min_cor[0], max_cor[0]):
        for j in range(min_cor[1], max_cor[1]):
            mass = barycentric_coordinates(px0, py0, px1, py1, px2, py2, i, j)
            if mass[0] >= 0 and mass[1] >= 0 and mass[2] >= 0:
                z = z0 * mass[0] + z1 * mass[1] + z2 * mass[2]
                if z > z_buf[j][i]:
                    continue
                z_buf[j][i] = z

                u = mass[0] * tx0 + mass[1] * tx1 + mass[2] * tx2
                v = mass[0] * ty0 + mass[1] * ty1 + mass[2] * ty2

                tex_x = min(int(u * (texture_width - 1)), texture_width - 1)
                tex_y = min(int((1 - v) * (texture_height - 1)), texture_height - 1)
                tex_color = texture[tex_y, tex_x]

                I = mass[0] * I0 + mass[1] * I1 + mass[2] * I2
                shaded_color = (tex_color * I).astype(np.uint8)
                res[j][i] = shaded_color
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

def open_f_with_texture(filename):
    arr_f = []
    with open(filename, "r") as file:
        for line in file:
            parts = line.strip().split()
            if parts and parts[0] == 'f':
                face = []
                for part in parts[1:]:
                    indices = part.split('/')
                    v_idx = int(indices[0]) if indices[0] else 0
                    vt_idx = int(indices[1]) if len(indices) > 1 and indices[1] else 0
                    face.append((v_idx, vt_idx))
                arr_f.append(face)
    return arr_f

def open_vt(filename):
    arr_vt = []
    with open(filename, "r") as file:
        for line in file:
            parts = line.strip().split()
            if parts and parts[0] == 'vt':
                u = float(parts[1])
                v = float(parts[2])
                arr_vt.append([u, v])
    return arr_vt

def rotate(arr):
    a = math.radians(30)
    b = math.radians(200)
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
    arr[...] = arr + np.array([0.01, 0.04, 0.4])
    return arr

def zoom(x0, y0, z0, x1, y1, z1, x2, y2, z2):
    n = 3500
    px0, py0 = n*x0/z0 + 500, n*y0/z0 + 500
    px1, py1 = n*x1/z1 + 500, n*y1/z1 + 500
    px2, py2 = n*x2/z2 + 500, n*y2/z2 + 500
    return px0, py0, px1, py1, px2, py2

arr_v = open_v("model_1.obj")
arr_vt = open_vt("model_1.obj")
arr_f = open_f_with_texture("model_1.obj")
texture = np.array(Image.open("bunny-atlas.jpg"))

vertex_normals = calculate_vertex_normals(arr_v, [[f[0] for f in face] for face in arr_f])
arr_v = rotate(arr_v)

res = np.zeros((1000, 1000, 3), dtype=np.uint8)
res[...] = 255
z_buf = np.full((1000, 1000), 10000, dtype=np.float32)

for face in arr_f:
    (v0, vt0), (v1, vt1), (v2, vt2) = face

    x0, y0, z0 = arr_v[v0 - 1][0], arr_v[v0 - 1][1], arr_v[v0 - 1][2]
    x1, y1, z1 = arr_v[v1 - 1][0], arr_v[v1 - 1][1], arr_v[v1 - 1][2]
    x2, y2, z2 = arr_v[v2 - 1][0], arr_v[v2 - 1][1], arr_v[v2 - 1][2]

    n0 = vertex_normals[v0 - 1]
    n1 = vertex_normals[v1 - 1]
    n2 = vertex_normals[v2 - 1]

    tx0, ty0 = arr_vt[vt0 - 1] if vt0 > 0 else (0, 0)
    tx1, ty1 = arr_vt[vt1 - 1] if vt1 > 0 else (0, 0)
    tx2, ty2 = arr_vt[vt2 - 1] if vt2 > 0 else (0, 0)

    triangle_normal = calculate_triangle_normal([x0, y0, z0], [x1, y1, z1], [x2, y2, z2])
    if np.dot(triangle_normal, [0, 0, 1]) > 0:
        continue

    pixels = draw_pixel_textured(x0, y0, z0, n0, tx0, ty0, x1, y1, z1, n1, tx1, ty1, x2, y2, z2, n2, tx2, ty2, res, z_buf, texture)

img = Image.fromarray(pixels, mode='RGB')
img.save("texture2.png")