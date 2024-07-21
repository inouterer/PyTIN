import time

from triangulation import Triangulation
from isocontourer import IsoConturer
from triangulation_classes import Point, HeightLevel, HeightLeveler

from visualisation import plot_triangulation
from visualisation import visualize_contours, visualize_profile

import pandas as pd

#Точки из CSV
points = Point.import_xyz_csv('input_data\\kgs1.csv', 1)

maplevels = HeightLeveler(HeightLeveler.read_cmp_file('input_data\\entro.cmp'))
#print(maplevels)
#print(maplevels.get_level_index_by_heigh_from(-5.99))

#Добавляем в поверхность списком точки класса Points и создаём триангулляцию.
print("Триангулируем...")
surface = Triangulation()
surface.triangulate(points)

print("Получаем границы...")
surface.get_bounds()
plot_triangulation(surface)
surface.custom_bounds = Point.import_xyz_csv('input_data\\kgs1_bounds.csv', 1)
surface.insert_custom_bound_points()

surface.triangulate(points)
surface.remove_outer_triangles()

surface.get_bounds()


#Генерируем уровни
maplevels = HeightLeveler(HeightLeveler.read_cmp_file('input_data\\entro.cmp'))
surface.levels = maplevels.get_correct_isolines_levels(surface.points) #Извлекаем уровни для изолиний

#Строим изолинии
print("Строим изолинии")
surface.build_contour_lines()

#Прорежаем изолинии
print("Прорежаем изолинии")
#surface.cull_contour_lines(1)
#Сглаживаем спрайном Катмулла - Рома (точек на ребро и параметр натяжения 0-1)
surface.smooth_contour_lines(10, 0.25)
plot_triangulation(surface)

#Создаём граф для изоконтуров
print("Собираем изоконтуры...")
graf = IsoConturer(maplevels.levels, points)
#Добавляем туда границы сетки
graf.add_bounds(surface.bounds)
#Добавляем изолинии
#graf.add_isolines(surface.contour_lines.copy())
graf.add_isolines(surface.sm_contour_lines.copy())
#Строим изоконтура
graf.build_isocontours()


#Показываем

print("Визуализация...")

visualize_profile(graf.points, surface.points, graf.isolines, graf.bounds, graf.isocontours)
