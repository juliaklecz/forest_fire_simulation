import numpy as np
import pygame
from pygame.locals import *
import sys
from PIL import Image
import random

clock = pygame.time.Clock()
FPS = 80

# Loading moisture map
moisture_image = Image.open("moisture_map.bmp")

# Convert image to np array
moisture_array = np.array(moisture_image)

# Normalizing value to 0 - 100
min_value = moisture_array.min()
max_value = moisture_array.max()
normalized_moisture = 1 + (moisture_array - min_value) * (99 / (max_value - min_value))

# Initializing wind direction
def initialize_wind_direction():
    directions = ["north", "south", "east", "west"]
    return np.random.choice(directions)

wind_direction = initialize_wind_direction()

def change_state(x, y, current_pixel, pixels, width, height, wind_direction, moisture, extinguish_radius, extinguish_center=None):
    if current_pixel == 255:  # River (blue)
        return current_pixel
    elif 16711680 <= current_pixel <= 16711685:  # Burning tree (red)
        # Check if area is where rain or extinguishing is happening
        if raining:
            if random.random() > 0.9:
                return 2827826
            else:
                return current_pixel
        if extinguish_center and (
                (x - extinguish_center[0]) ** 2 + (y - extinguish_center[1]) ** 2
        ) <= extinguish_radius ** 2:
            return 2827826  # Change state to burnt tree
        # Checking if tree has been burning for long enough
        generations_burning = current_pixel - 16711680
        if generations_burning < 4:
            return current_pixel + 1  # Increase by 1 to show how long the tree has been burning for
        else:
            return 2827826  # Change state to burnt tree

    elif current_pixel == 2827826:  # Burnt tree (brown)
        return current_pixel
    elif current_pixel == 12632256:  # Road (gray)
        return current_pixel
    elif current_pixel == 65280:  # Tree (green)
        if raining: return 65280

        # Checking Moore's neighbourhood
        burning_trees = 0
        dx_left = 4 if wind_direction == "west" else 3
        dx_right = 4 if wind_direction == "east" else 3
        dy_up = 4 if wind_direction == "north" else 3
        dy_down = 4 if wind_direction == "south" else 3

        if firefighting_direction == (0, 1):
            dy_down = 1
        elif firefighting_direction == (0, -1):
            dy_up = 1
        elif firefighting_direction == (1, 0):
            dx_right = 1
        elif firefighting_direction == (-1, 0):
            dx_left = 1



        for dx in range(-dx_left, dx_right+1):
            for dy in range(-dy_up, dy_down+1):
                if dx == 0 and dy == 0:
                    continue

                new_x, new_y = x + dx, y + dy
                # Checking if new coordinates are within image
                if 0 <= new_x < width and 0 <= new_y < height:
                    if 16711680 <= pixels[new_x, new_y] <= 16711684:  # Checking if there is a burning tree nearby
                        burning_trees += 1
        if(burning_trees > 1):
            for dx in range(-dx_left, dx_right+1):
                for dy in range(-dy_up, dy_down+1):
                    if dx == 0 and dy == 0:
                        continue

                    new_x, new_y = x + dx, y + dy

                    if 0 <= new_x < width and 0 <= new_y < height:

                        if wind_direction == "north" and new_y < y:
                            if pixels[new_x, new_y] in (16711680, 16711681, 16711682, 16711683, 16711684):
                                burning_trees += 1
                        elif wind_direction == "south" and new_y > y:
                            if pixels[new_x, new_y] in (16711680, 16711681, 16711682, 16711683, 16711684):
                                burning_trees += 1
                        elif wind_direction == "east" and new_x > x:
                            if pixels[new_x, new_y] in (16711680, 16711681, 16711682, 16711683, 16711684):
                                burning_trees += 1
                        elif wind_direction == "west" and new_x < x:
                            if pixels[new_x, new_y] in (16711680, 16711681, 16711682, 16711683, 16711684):
                                burning_trees += 1

        # Checking if there are at leas 3 burning trees nearby
        if burning_trees >= 3:
            # Calculating probability
            probability = calculate_probability(moisture, burning_trees, wind_direction)

            # Checking if tree catches fire
            if random.random() < probability:
                return 16711680  # Change state to burning tree

        # Less than 3 burning trees nearby -> not changing state of the tree
        return current_pixel

    else:
        return current_pixel

def calculate_probability(moisture, burning_trees, wind_direction):

    moisture_factor = 0.3
    burning_trees_factor = 0.2

    normalized_moisture = 1 - moisture / 100

    probability = (
        normalized_moisture * moisture_factor +
        burning_trees / 8 * burning_trees_factor
    )


    probability = max(0, min(1, probability))

    return probability

def create_next_generation(current_generation, width, height, wind_direction, normalized_moisture, extinguish_radius, extinguish_center):
    # Creating new generation based on previous generations
    next_generation = pygame.Surface((width, height))

    pixels_current = pygame.PixelArray(current_generation)
    pixels_next = pygame.PixelArray(next_generation)

    for y in range(height):
        for x in range(width):
            pixels_next[x, y] = change_state(x, y, pixels_current[x, y], pixels_current, width, height, wind_direction, normalized_moisture[x%329, y], extinguish_radius, extinguish_center)

    del pixels_current
    del pixels_next

    return next_generation

# Loading image, getting shape and using it for the pygame screen
img = Image.open("image.png")
img = img.convert("RGB")

width, height = img.size

pygame.init()

screen = pygame.display.set_mode((width, height))

# Converting PIL to pygame surface
pygame_img = pygame.image.fromstring(img.tobytes(), img.size, img.mode)

# Setting red pixels to start the fire in the upper left corner
pygame_img.set_at((28, 27), (255, 0, 0))
pygame_img.set_at((28, 28), (255, 0, 0))
pygame_img.set_at((28, 29), (255, 0, 0))
pygame_img.set_at((27, 29), (255, 0, 0))
pygame_img.set_at((27, 27), (255, 0, 0))
pygame_img.set_at((27, 28), (255, 0, 0))
pygame_img.set_at((29, 28), (255, 0, 0))
pygame_img.set_at((29, 27), (255, 0, 0))
pygame_img.set_at((29, 29), (255, 0, 0))

# Screen title
pygame.display.set_caption("Simulation of a forest fire")

# Opening generation
current_generation = pygame_img

extinguish_radius = 0
extinguish_center = 0
firefighting_direction = (0, 0)
raining = False
dancing_people = [(width - 1, i) for i in range(height - 1, height - 11, -1)]



# Main loop
while True:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == MOUSEBUTTONDOWN and event.button == 1:
            # Left mouse key
            mouse_x, mouse_y = event.pos
            extinguish_radius = 9
            extinguish_center = (mouse_x, mouse_y)
        elif event.type == KEYDOWN:
            # Arrow keys
            if event.key == K_UP:
                firefighting_direction = (0, -1)
            elif event.key == K_DOWN:
                firefighting_direction = (0, 1)
            elif event.key == K_LEFT:
                firefighting_direction = (-1, 0)
            elif event.key == K_RIGHT:
                firefighting_direction = (1, 0)
            elif event.key == K_r:
                if random.random() > 0.6:
                    raining = not raining



    # Create new generation
    current_generation = create_next_generation(current_generation, width, height, wind_direction, normalized_moisture, extinguish_radius, extinguish_center)

    # Show image
    screen.blit(current_generation, (0, 0))

    pygame.display.flip()
