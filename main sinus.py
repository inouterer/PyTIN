from triangulation import Triangulation
from isocontourer import IsoConturer
from triangulation_classes import Point

from visualisation import plot_triangulation
from visualisation import visualize_profile

from sample_data import point_in, trn_in, real, real_levels, user_bounds, real_bounds

import math

points = []


import random
num_points = 30
i=0
j=0
while i < num_points:
    i+=1
    while j < num_points:
        j+=1
        points.append(Point(i*10, j*10, 10+10*math.sin(i*j)))
    j=0


#Создаём поверхность
surface = Triangulation()
#Добавляем в поверхность списком точки класса Points и создаём триангулляцию.
surface.triangulate(points)

surface.get_bounds()

#Добавим пользовательские внешние границы
# surface.custom_bounds = custom_bounds_points

#Добавим пользовательские внешние границы в набор точек
# surface.insert_custom_bounds()

#Снова триангулируем
surface.triangulate(points)
#surface.remove_outer_triangles()
surface.get_bounds()

#Генерируем уровни
step = 1
surface.define_contours_levels(0, step)

#Строим изолинии
surface.build_contour_lines()

#Прорежаем изолинии
surface.cull_contour_lines(1)
#Сглаживаем спрайном Катмулла - Рома (точек на ребро и параметр натяжения 0-1)
surface.smooth_contour_lines(10, 0.5)

#Визуализация в matplotlib
#plot_triangulation(surface)

#Создаём граф для изоконтуров
graf = IsoConturer(surface.levels, points)
#Добавляем туда границы сетки
graf.add_bounds(surface.bounds)
#Добавляем изолинии
graf.add_isolines(surface.sm_contour_lines)
#Строим изоконтура
graf.build_isocontours(step)
#Показываем
visualize_profile(graf.points, surface.points, graf.isolines, graf.bounds, graf.isocontours)