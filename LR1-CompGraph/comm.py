import numpy as np
from PIL import Image, ImageOps
import math

def barycentric_coordinates(x0, y0, x1, y1, x2, y2, x, y):
    '''
    Вычисляет барицентрические координаты точки (x, y) относительно треугольника, заданного вершинами (x0, y0), (x1, y1) и (x2, y2).
    Эти координаты используются для определения того, находится ли точка внутри треугольника
    Возвращаемое значение: Кортеж, содержащий барицентрические координаты
    '''
    lambda0 = ((x - x2) * (y1 - y2) - (x1 - x2) * (y - y2)) / ((x0 - x2) * (y1 - y2) - (x1 - x2) * (y0 - y2))
    lambda1 = ((x0 - x2) * (y - y2) - (x - x2) * (y0 - y2)) / ((x0 - x2) * (y1 - y2) - (x1 - x2) * (y0 - y2))
    lambda2 = 1.0 - lambda0 - lambda1
    return lambda0, lambda1, lambda2

'''
Назначение: Эти функции определяют максимальные и минимальные координаты x и y среди заданных вершин.
Это используется для определения ограничивающего прямоугольника вокруг треугольника для эффективной обработки пикселей
Возвращаемое значение: Кортеж, содержащий координаты x и y.
Ограничивающий прямоугольник используется для оптимизации процесса рендеринга.
Вместо перебора всех пикселей на экране, код перебирает только пиксели, 
находящиеся внутри ограничивающего прямоугольника, что значительно сокращает время рендеринга.
'''

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
    '''
    Вычисляет нормаль к треугольнику, заданному тремя вершинами.
    Нормаль используется для расчета освещения поверхности.
    Возвращаемое значение: Нормализованный вектор нормали.
    '''
    v0 = np.array(v0)
    v1 = np.array(v1)
    v2 = np.array(v2)

    # вычисляет два вектора, образованных сторонами треугольника
    v1_v0 = v1 - v0
    v2_v0 = v2 - v0

    # вычисляет векторное произведение этих векторов, чтобы получить нормаль
    n = np.cross(v1_v0, v2_v0)

    # нормаль нормализуется, чтобы получить единичный вектор
    n /= np.linalg.norm(n)
    return n

def calculate_vertex_normals(arr_v, arr_f):
    '''
    Вычисляет нормали к вершинам 3D-модели, усредняя нормали прилегающих граней.
    '''
    # массив содержит нормали каждой вершины
    vertex_normals = np.zeros((len(arr_v), 3))

    # массив сбора нормалей всех граней, которые окружают каждую вершину.
    vertex_faces = [[] for _ in range(len(arr_v))]

    for i in arr_f:
        #  грань i представляет собой набор индексов вершин, образующих треугольник.

        # извлекаем индекс первой вершины из текущей грани i и сохраняем его в v0
        # вычитается 1, потому что OBJ-формат использует индексацию с 1, а Python использует индексацию с 0.
        v0 = i[0] - 1
        v1 = i[1] - 1
        v2 = i[2] - 1

        # вычисление нормали к текущей грани
        normal = calculate_triangle_normal(arr_v[v0], arr_v[v1], arr_v[v2])

        # добавляем вычисленные нормали грани в список нормалей, связанных с вершинами
        vertex_faces[v0].append(normal)
        vertex_faces[v1].append(normal)
        vertex_faces[v2].append(normal)

    for i in range(len(arr_v)):
        # Проверяет, содержит ли список vertex_faces[i] какие-либо нормали.
        # Это условие проверяет, что вершина i используется хотя бы в одной грани.
        if vertex_faces[i]:
            # вычисляем среднее значение всех нормалей, хранящихся в vertex_faces[i]
            # np.mean вычисляет среднее значение вдоль указанной оси.
            # axis=0 означает, что усреднение происходит по столбцам (т.е. усредняются компоненты x, y и z всех нормалей).
            avg_normal = np.mean(vertex_faces[i], axis=0)

            # нормализуем усредненную нормаль, чтобы получить единичный вектор.
            avg_normal /= np.linalg.norm(avg_normal)

            # сохраняем нормализованную усредненную нормаль
            vertex_normals[i] = avg_normal

    return vertex_normals

def draw_pixel(x0, y0, z0, n0, tx0, ty0, x1, y1, z1, n1, tx1, ty1, x2, y2, z2, n2, tx2, ty2, res, z_buf, texture):
    '''
    Функция реализует конвейер рендеринга для треугольника. Рисует треугольник на изображении
    с текстурированием и затенением, используя z-буфер для удаления невидимых поверхностей.

    x0, y0, z0, x1, y1, z1, x2, y2, z2: Координаты вершин треугольника в 3D-пространстве.
                            n0, n1, n2: Нормали к вершинам треугольника.
          tx0, ty0, tx1, ty1, tx2, ty2: Текстурные координаты вершин треугольника.
                                   res: Буфер изображения (NumPy array), в котором будет рисоваться треугольник.
                                 z_buf: Z-буфер (NumPy array), используемый для удаления невидимых поверхностей.
                               texture: Текстура (NumPy array), которая будет отображаться на треугольнике.
    '''

    # функция zoom для проецирования 3D-координат в 2D-координаты экрана.
    px0, py0, px1, py1, px2, py2 = zoom(x0, y0, z0, x1, y1, z1, x2, y2, z2)

    # чтобы определить прямоугольник, содержащий треугольник. Это уменьшает количество пикселей, которые необходимо проверить.
    min_cor = min_x_y(px0, py0, px1, py1, px2, py2)
    max_cor = max_x_y(px0, py0, px1, py1, px2, py2)

    # Определяет направление света как вектор, указывающий в положительном направлении оси z.
    light_dir = np.array([0, 0, 1])

    # Вычисляет освещенность вершины (I0, I1, I2) с использованием скалярного произведения
    # нормали к вершине (n0, n1, n2) и направления света (light_dir).
    # max(0, ...) гарантирует, что освещенность не будет отрицательной (отрицательное значение означает, что вершина отвернута от света).
    I0 = max(0, np.dot(n0, light_dir))
    I1 = max(0, np.dot(n1, light_dir))
    I2 = max(0, np.dot(n2, light_dir))

    # Получает ширину и высоту текстуры из атрибута shape массива texture.
    texture_width, texture_height = texture.shape[1], texture.shape[0]

    # для каждого пикселя внутри ограничивающего прямоугольника вычисляются барицентрические координаты.
    for i in range(min_cor[0], max_cor[0]):
        for j in range(min_cor[1], max_cor[1]):
            mass = barycentric_coordinates(px0, py0, px1, py1, px2, py2, i, j)
            if (mass[0] >= 0 and mass[1] >= 0 and mass[
                2] >= 0):  # если все барицентрические координаты неотрицательными, то пиксель находится внутри треугольника.
                # z-координата интерполируется с использованием барицентрических координат
                z = z0 * mass[0] + z1 * mass[1] + z2 * mass[2]

                # z-буфер – это матрица из вещественных значений по размеру совпадающая с
                # изображением. Все элементы z-буфера изначально инициализируются некоторым достаточно большим значением.
                # z_buf используется для определения того, находится ли текущий треугольник перед какими-либо ранее нарисованными
                # треугольниками. Если это так, пиксель рисуется, и z-буфер обновляется.
                if z > z_buf[j][i]:
                    continue

                # Если пиксель проходит проверку z-буфера (т.е. он виден), z-буфер обновляется z-координатой текущего пикселя.
                z_buf[j][i] = z

                # Вычисляет текстурную координату u пикселя путем интерполяции текстурных координат вершин треугольника с использованием барицентрических координат.
                u = mass[0] * tx0 + mass[1] * tx1 + mass[2] * tx2

                # вычисляет текстурную координату v пикселя.
                v = mass[0] * ty0 + mass[1] * ty1 + mass[2] * ty2

                # Преобразует текстурную координату u, v в координату x, y в текстуре.
                # u * (texture_width - 1) масштабирует координату u к диапазону ширины текстуры.
                # min гарантирует, что координата не выходит за пределы текстуры.
                tex_x = min(int(u * (texture_width - 1)), texture_width - 1)
                tex_y = min(int((1 - v) * (texture_height - 1)), texture_height - 1)

                # Извлекает цвет пикселя из текстуры с использованием вычисленных текстурных координат tex_x и tex_y.
                tex_color = texture[tex_y, tex_x]

                # Вычисляет освещенность пикселя путем интерполяции освещенности вершин треугольника с использованием барицентрических координат.
                I = mass[0] * I0 + mass[1] * I1 + mass[2] * I2

                # Применяет освещение к цвету текстуры, умножая цвет текстуры на значение освещенности.
                # .astype(np.uint8) преобразует цвет в формат 8-битного целого числа без знака (значения от 0 до 255).
                shaded_color = (tex_color * I).astype(np.uint8)

                # Устанавливает цвет пикселя
                res[j][i] = shaded_color
    return res

def open_v(filename):
    '''
    Считывает данные вершин из файла
    Файлы OBJ хранят данные 3D-модели, включая положения вершин. Каждая строка, начинающаяся с 'v', определяет вершину.
    Возвращаемое значение: Список списков, где каждый внутренний список представляет собой вершину с ее координатами x, y и z.
    '''
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

def open_f1(filename):
    '''
    Считывает данные граней (треугольников) из файла
    Каждая строка, начинающаяся с 'f', определяет грань, которая в данном случае является треугольником. Числа, следующие за 'f',
    являются индексами в списке вершин, определяющими, какие вершины составляют грань.
    Возвращаемое значение: Список списков, где каждый внутренний список представляет собой грань и содержит индексы вершин, составляющих грань.
    '''
    arr_f = []
    with open(filename, "r") as file:
        for line in file:
            parts = line.strip().split()
            if parts and parts[0] == 'f':
                num = [int(part.split('/')[0]) for part in parts[1:]]
                arr_f.append(num)
    return arr_f

def open_f(filename):
    arr_f = []
    with open(filename, "r") as file:
        for line in file:
            parts = line.strip().split()
            if parts and parts[0] == 'f':  # если список не пуст и первый элемент списка равен 'f'
                # Этот список будет использоваться для хранения информации о текущей грани.
                face = []
                for part in parts[1:]:
                    # строка содержит подстроки ( координат и, возможно, нормалей, разделенных косой чертой '/')
                    indices = part.split('/')  # список подстрок из индексов вершин

                    # Извлекает индекс вершины из списка indices, преобразуя строку в int
                    v_idx = int(indices[0]) # интовый индекс

                    # Извлекает индекс текстурной координаты из списка indices
                    # len(indices) > 1 проверяет, содержит ли список indices как минимум два элемента (т.е. индекс текстурной координаты существует)
                    vt_idx = int(indices[1]) if len(indices) > 1 else 0

                    # Этот кортеж содержит индекс вершины и индекс текстурной координаты для текущей вершины грани.
                    face.append((v_idx, vt_idx))
                # список arr_f содержит информацию о текущей грани
                arr_f.append(face)
    return arr_f

def open_vt(filename):
    '''
    Определяет функцию с именем open_vt, которая принимает один аргумент
    Возвращает список arr_vt, содержащий все текстурные координаты, прочитанные из файла.
    '''
    # список будет использоваться для хранения текстурных координат (u, v)
    arr_vt = []

    with open(filename, "r") as file:
        for line in file:
            parts = line.strip().split()
            if parts and parts[0] == 'vt':
                # условие гарантирует, что обрабатываются только строки, определяющие текстурные координаты
                # (строки, начинающиеся с 'vt' в файле OBJ).
                u = float(parts[1])
                v = float(parts[2])
                arr_vt.append([u, v])
    return arr_vt

def rotate(arr):
    '''
    Вращает вершины 3D-модели вокруг осей x, y и z с использованием матриц вращения. Он также перемещает модель.
    Возвращаемое значение: Массив повернутых и перемещенных вершин.
    '''
    a = math.radians(30)
    b = math.radians(200)
    c = math.radians(180)

    # Матрицы вращения: Определяет матрицы вращения для каждой оси (x, y, z).
    rotation_matrix_x = np.array([[1, 0, 0],
                                  [0, np.cos(a), np.sin(a)],
                                  [0, -np.sin(a), np.cos(a)]])
    rotation_matrix_y = np.array([[np.cos(b), 0, np.sin(b)],
                                  [0, 1, 0],
                                  [-np.sin(b), 0, np.cos(b)]])
    rotation_matrix_z = np.array([[np.cos(c), np.sin(c), 0],
                                  [-np.sin(c), np.cos(c), 0],
                                  [0, 0, 1]])
    # numpy.dot() для вычисления скалярного произведения двух массивов (выполняет матричное умножение матриц)
    # Умножение матриц: Применяет вращения, умножая координаты вершин на матрицы вращения в порядке Z, Y, X.
    arr = np.dot(np.array(arr), rotation_matrix_z)
    arr = np.dot(np.array(arr), rotation_matrix_y)
    arr = np.dot(np.array(arr), rotation_matrix_x)

    # Перемещение: Перемещает модель, добавляя постоянный вектор к каждой вершине.
    arr[...] = arr + np.array([0.01, 0.04, 0.4])
    return arr

def zoom(x0, y0, z0, x1, y1, z1, x2, y2, z2):
    '''
    Выполняет перспективную проекцию 3D-координат в 2D-координаты экрана.
    Перспективная проекция: Имитирует эффект глубины, заставляя объекты казаться меньше по мере их удаления.
    Возвращаемое значение: Проецированные 2D-координаты (px0, py0, px1, py1, px2, py2).
    '''
    n = 3500
    px0, py0 = n * x0 / z0 + 500, n * y0 / z0 + 500
    px1, py1 = n * x1 / z1 + 500, n * y1 / z1 + 500
    px2, py2 = n * x2 / z2 + 500, n * y2 / z2 + 500
    return px0, py0, px1, py1, px2, py2

arr_v = open_v("model_1.obj")
arr_f = open_f("model_1.obj")
arr_vt = open_vt("model_1.obj")
texture = np.array(Image.open("bunny_atlas.jpg"))

vertex_normals = calculate_vertex_normals(arr_v, [[f[0] for f in i] for i in arr_f])  # (список координат вершин, список индексов вершин для каждой грани.)
arr_v = rotate(arr_v)

res = np.zeros((1000, 1000, 3), dtype=np.uint8)
res[...] = 255
z_buf = np.full((1000, 1000), 10000, dtype=np.float32)

for i in arr_f:
    (v0, vt0), (v1, vt1), (v2, vt2) = i

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
    pixels = draw_pixel(x0, y0, z0, n0, tx0, ty0, x1, y1, z1, n1, tx1, ty1, x2, y2, z2, n2, tx2, ty2, res, z_buf,
                        texture)

img = Image.fromarray(pixels, mode='RGB')
img.save("texture5.png")
img.show()