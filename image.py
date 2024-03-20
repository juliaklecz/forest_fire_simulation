import pygame
from pygame.locals import *
import sys
from PIL import Image

#Function checking Moore's neighbourhood and changing pixel's color
def change_color(x, y, pixels, width, height):
    neighbors = [
        pixels[(y - 1) * width + x - 1] if y > 0 and x > 0 else 0,
        pixels[(y - 1) * width + x] if y > 0 else 0,
        pixels[(y - 1) * width + x + 1] if y > 0 and x < width - 1 else 0,
        pixels[y * width + x - 1] if x > 0 else 0,
        pixels[y * width + x + 1] if x < width - 1 else 0,
        pixels[(y + 1) * width + x - 1] if y < height - 1 and x > 0 else 0,
        pixels[(y + 1) * width + x] if y < height - 1 else 0,
        pixels[(y + 1) * width + x + 1] if y < height - 1 and x < width - 1 else 0
    ]

    if neighbors.count(216) >= 4:
        return (0, 0, 255)  # Change to blue
    elif neighbors.count(255) >= 1:
        return (192, 192, 192)  # Change grey
    else:
        return (0, 255, 0)  # Change to green

# Loading image using PIL
img = Image.open("Mapa_MD_no_terrain_low_res_Gray.bmp")
img = img.convert("L")  # Converting to grayscale

# Pixels data in a list
pixels = list(img.getdata())

# Getting images shape
width, height = img.size

# New list for new pixel's data
new_pixels = []

# Going through pixels to check neighbours
for y in range(height):
    for x in range(width):
        new_pixels.append(change_color(x, y, pixels, width, 2))

# Making new image with new pixel's data
new_img = Image.new("RGB", (width, height))
new_img.putdata(new_pixels)

new_img.save("image.png")


# Initialize pygame
pygame.init()

# Setting screen shape
screen = pygame.display.set_mode((width, height))

# Converting pil to pygame
pygame_img = pygame.image.fromstring(new_img.tobytes(), new_img.size, new_img.mode)

# Set window title
pygame.display.set_caption("Changing image's color")

# Main loop
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    # Show image on screen
    screen.blit(pygame_img, (0, 0))
    pygame.display.flip()
