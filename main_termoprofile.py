import time

from triangulation import Triangulation
from isocontourer import IsoConturer
from triangulation_classes import Point, HeightLevel, HeightLeveler

from visualisation import plot_triangulation
from visualisation import visualize_contours, visualize_profile

import pandas as pd

# Чтение CSV файла с указанием разделителя ';'
df = pd.read_csv('profile.csv', header=None, delimiter=';')

# Создание пустого списка для хранения объектов Point
points = []

# Проход по каждой строке значений температуры, начиная со второй строки
for index, row in df.iloc[0:].iterrows():
    point = Point(row[0], row[1], row[2])
    points.append(point)

maplevels = HeightLeveler(HeightLeveler.read_cmp_file('input_data\\entro.cmp'))
#print(maplevels)
#print(maplevels.get_level_index_by_heigh_from(-5.99))

#Добавляем в поверхность списком точки класса Points и создаём триангулляцию.
print("Триангулируем...")
surface = Triangulation()
surface.triangulate(points)

print("Получаем границы...")
surface.get_bounds()

#Генерируем уровни
maplevels = HeightLeveler(HeightLeveler.read_cmp_file('input_data\entro.cmp'))
#print(maplevels)
#print(maplevels.get_level_index_by_heigh_from(-5.99))
surface.levels = maplevels.get_correct_isolines_levels(surface.points) #Извлекаем уровни для изолиний
# print("Генерируем уровни")
# step = 1
#surface.define_contours_levels(-10,step)
#surface.levels = [-10, -6, -5, -4, -3, -2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2, 10]

#Строим изолинии
print("Строим изолинии")
surface.build_contour_lines()

#Прорежаем изолинии
print("Прорежаем изолинии")
surface.cull_contour_lines(1)
#Сглаживаем спрайном Катмулла - Рома (точек на ребро и параметр натяжения 0-1)
surface.smooth_contour_lines(10, 0.25)

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
