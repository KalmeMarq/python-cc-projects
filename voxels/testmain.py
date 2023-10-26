import matplotlib.pyplot as plt
from perlin_noise import PerlinNoise

noise = PerlinNoise(octaves=4, seed=1)
for x in range(16):
    for z in range(16):
        print(noise.noise([x / 16, z / 16]) * 16)
# xpix, ypix = 16, 16
# pic = [[noise([i/xpix, j/ypix]) for j in range(xpix)] for i in range(ypix)]

# plt.imshow(pic, cmap='gray')
# plt.show()