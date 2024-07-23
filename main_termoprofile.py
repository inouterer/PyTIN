from pyTIN_library.triangulation import Triangulation
from pyTIN_library.isocontourer import IsoConturer
from pyTIN_library.triangulation_classes import Point, HeightLevel, HeightLeveler

from pyTIN_library.visualisation import plot_triangulation
from pyTIN_library.visualisation import visualize_contours, visualize_profile, plotly_iso

import pandas as pd

points = Point.import_nxyz_csv('input_data\\profile.csv', 0)

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
maplevels = HeightLeveler(HeightLeveler.read_cmp_file('input_data\\entro.cmp'))
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
surface.smooth_contour_lines(10, 0.5)

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
#visualize_profile(graf.points, surface.points, graf.isolines, graf.bounds, graf.isocontours)
plotly_iso(graf.isocontours, surface.points)
