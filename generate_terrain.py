import numpy as np
from noise import pnoise2
from triangulation_classes import Point
import random

def generate_terrain(width, height, scale=0.1, octaves=6, persistence=0.5, lacunarity=2.0):
    terrain = []
    for y in range(height):
        for x in range(width):
            # Вычисляем высоту z с помощью шума Perlin
            z = pnoise2(x * scale, 
                        y * scale, 
                        octaves=octaves, 
                        persistence=persistence, 
                        lacunarity=lacunarity)
            # Скейлим высоту для лучшей визуализации или использования
            z_scaled = z * 100  # Масштабируем высоту
            terrain.append(Point(x, y, z_scaled))
    return terrain

# # Параметры карты
# width = 100  # ширина карты
# height = 100  # высота карты

# # Генерация территории
# terrain_points = generate_terrain(width, height)

# Пример вывода координат одной точки
# print(f"X: {terrain_points[0].x}, Y: {terrain_points[0].y}, Z: {terrain_points[0].z}")




def generate_random_points(num_points):
    points = []
    for _ in range(num_points):
        x = random.uniform(0, 100)  # случайное значение X в диапазоне от -100 до 100
        y = random.uniform(0, 100)  # случайное значение Y в том же диапазоне
        z = random.uniform(0, 10)    # случайное значение Z, предположим, в меньшем диапазоне
        points.append(Point(x, y, z))
    return points
