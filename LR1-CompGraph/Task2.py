import numpy as np
from PIL import Image
import math
#вариант 1
def draw_line(image, x0,  y0, x1, y1, count, color):
    step = 1.0 / count
    for t in np.arange(0, 1, step):
        x = round((1.0- t) * x0 + t * x1)
        y = round((1.0- t) * y0 + t * y1)
        image[y, x] = color
#вариант 2
def dotted_line(image, x0, y0, x1, y1, color):
    count = math.sqrt((x0 -x1)**2 + (y0 -y1)**2)
    step = 1.0/count
    for t in np.arange(0, 1, step):
        x = round ((1.0-t)*x0 + t*x1)
        y = round ((1.0-t)*y0 + t*y1)
        image[y, x] = color
#вариант 3
def x_loop_line(image, x0, y0, x1, y1, color):
    x0 = int(x0)
    x1 = int(x1)
    for x in range (x0, x1):
        t = (x-x0)/(x1 -x0)
        y = round ((1.0-t)*y0 + t*y1)
        image[y, x] = color
#вариант 4
def x_loop_line_1(image, x0, y0, x1, y1, color):
    if (x0 > x1):
        x0, x1 = x1, x0
        y0, y1 = y1, y0
    x0 = int(x0)
    x1 = int(x1)
    for x in range (x0, x1):
        t = (x-x0)/(x1 -x0)
        y = round ((1.0-t)*y0 + t*y1)
        image[y, x] = color
#вариант 5
def x_loop_line_2(image, x0, y0, x1, y1, color):
    xchange = False
    if (abs(x0 - x1) < abs(y0 - y1)):
        x0, y0 = y0, x0
        x1, y1 = y1, x1
        xchange = True

    x0 = int(x0)
    x1 = int(x1)

    for x in range (x0, x1):
        t = (x-x0)/(x1 -x0)
        y = round ((1.0-t)*y0 + t*y1)
        if (xchange):
            image[x, y] = color
        else:
            image[y, x] = color
#вариант 6
def x_loop_line_12(image, x0, y0, x1, y1, color):
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

    for x in range (x0, x1):
        t = (x-x0)/(x1 -x0)
        y = round ((1.0-t)*y0 + t*y1)
        if (xchange):
            image[x, y] = color
        else:
            image[y, x] = color
#вариант 7
def x_loop_line_no_y(image, x0, y0, x1, y1, color):
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
    dy = abs(y1-y0)/(x1 -x0)
    derror = 0.0
    y_update = 1 if y1 > y0 else -1
    for x in range(x0, x1):
        if (xchange):
            image[x, y] = color
        else:
            image[y, x] = color
        derror += dy
        if (derror > 0.5):
            derror -= 1.0
            y += y_update
#вариант 8
def x_loop_line_no_y_wtf(image, x0, y0, x1, y1, color):
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
    dy = 2.0*(x1 - x0)*abs(y1 -y0)/(x1 -x0)
    derror = 0.0
    y_update = 1 if y1 > y0 else -1
    for x in range (x0, x1):
        if (xchange):
            image[x, y] = color
        else:
            image[y, x] = color
        derror += dy
        if (derror > 2.0 * (x1 - x0) * 0.5):
            derror -= 2.0 * (x1 - x0) * 1.0
            y += y_update
#вариант 9
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

img = np.zeros((200, 200, 3), dtype = np.uint8)
count = 100
color = 255
for i in range (0, 13):
    x0, y0 = 100, 100
    x1, y1 = np.cos((i*2*np.pi)/13)*100 + 100, np.sin((i*2*np.pi)/13)*100 + 100
    bresenham(img, x0, y0, x1, y1, color)
img = Image.fromarray(img, mode = 'RGB')
img.save('star9.png')
