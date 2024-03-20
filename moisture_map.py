import noise
import numpy as np
from PIL import Image

def generate_moisture_map(width, height, scale, octaves, persistence, lacunarity, seed):
    # Generating moisture map
    moisture_map = np.zeros((width, height))
    for y in range(height):
        for x in range(width):
            value = noise.pnoise2(x/scale,
                                  y/scale,
                                  octaves=octaves,
                                  persistence=persistence,
                                  lacunarity=lacunarity,
                                  repeatx=1024,
                                  repeaty=1024,
                                  base=seed)
            moisture_map[x, y] = (value + 1) * 50

    return moisture_map

# Setting parameters of the map
width = 330
height = 600
scale = 60
octaves = 4
persistence = 0.5
lacunarity = 2.0
seed = 1

# Generating map
moisture_map = generate_moisture_map(width, height, scale, octaves, persistence, lacunarity, seed)

# Generating an image from the map
image = Image.fromarray(moisture_map.astype('uint8'))

# Saving image as bmp
image.save("moisture_map.bmp")

# Showing generated map
image.show()

# Show the map as an image
moisture_image = Image.fromarray(moisture_map.astype('uint8'))
moisture_image.show()
