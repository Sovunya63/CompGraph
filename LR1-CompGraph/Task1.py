import numpy as np
from PIL import Image

#img [200:400, 200:400] = 128 # серое окошко
#img [0:800, 0:600, 1] = 255 # зеленый

# полностью черное
def black():
  img = np.zeros((H, W), dtype= np.uint8)
  img[...] = 0
  image = Image.fromarray(img, mode='L')
  image.save("color1.png")

# полностью белое
def white():
  img = np.zeros((H, W), dtype= np.uint8)
  img[...] = 255
  image = Image.fromarray(img, mode='L')
  image.save("color2.png")

# полностью красное
def red():
  img = np.zeros((H, W, 3), dtype= np.uint8)
  img[...] = (255, 0, 0)
  image = Image.fromarray(img, mode='RGB')
  image.save("color3.png")

# градиент
def gradient():
  img = np.zeros((H, W, 3), dtype=np.uint8)
  for y in range(H):
      for x in range(W):
          color = (x + y) % 256
          img[y, x] = [color, color, color]
  image = Image.fromarray(img, mode='RGB')
  image.save("color4.png")

H, W = 600, 600
black()
white()
red()
gradient()