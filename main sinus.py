from pyTIN_library.triangulation import Triangulation
from pyTIN_library.isocontourer import IsoConturer
from pyTIN_library.triangulation_classes import Point

from pyTIN_library.visualisation import plot_triangulation
from pyTIN_library.visualisation import visualize_profile, plotly_iso
from pyTIN_library.triangulation_classes import HeightLeveler

from input_data.sample_data import point_in, trn_in, real, real_levels, user_bounds, real_bounds

import math

points = []


import random
# num_rows = 30
# i=0
# j=0
# while i < num_rows:
#     i+=1
#     while j < num_rows:
#         j+=1
#         points.append(Point(i*10, j*10, 10+10*math.sin(i*j)))
#     j=0
 
import numpy as np
# Создание сетки точек
n = 20  # Количество точек по каждой оси
x = np.linspace(-5, 5, n)
y = np.linspace(-5, 5, n)
X, Y = np.meshgrid(x, y)

# Генерация случайных значений высоты Z
Z_random = np.random.rand(n, n)

# Вычисление значения синусной функции
Z_sin = np.sin(X) * np.cos(Y)

# Комбинирование случайных значений с синусной функцией
Z = (Z_random*2 + Z_sin)*3

# Преобразование сетки точек в список точек
points = []
for i in range(n):
    for j in range(n):
        print (X[i, j], Y[i, j], Z[i, j], f'{i}-{j}')
        points.append(Point(X[i, j], Y[i, j], Z[i, j], ''))

#Создаём поверхность
surface = Triangulation()
#Добавляем в поверхность списком точки класса Points и создаём триангулляцию.
surface.triangulate(points)

surface.get_bounds()


#Генерируем уровни
step = 1
map_levels = HeightLeveler(HeightLeveler.define_contours_levels(surface.points, step))
map_levels.interpolate_color()
surface.levels = map_levels.get_correct_isolines_levels(surface.points) #Извлекаем уровни для изолиний
print(surface.levels)

#Строим изолинии
surface.build_contour_lines()

#Прорежаем изолинии
#surface.cull_contour_lines(0.1)
#Сглаживаем спрайном Катмулла - Рома (точек на ребро и параметр натяжения 0-1)
surface.smooth_contour_lines(10, 0.5)

#Визуализация в matplotlib
#plot_triangulation(surface)
print(2222222222222)
#Создаём граф для изоконтуров
graf = IsoConturer(map_levels.levels, points)
#Добавляем туда границы сетки
print(333333333333)
graf.add_bounds(surface.bounds)
#Добавляем изолинии
graf.add_isolines(surface.sm_contour_lines)
#Строим изоконтура
print(44444444444444)
graf.build_isocontours()
#Показываем
#visualize_profile(graf.points, surface.points, graf.isolines, graf.bounds, graf.isocontours)
print(555555555)
plotly_iso(graf.isocontours, surface.points)