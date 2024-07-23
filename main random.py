from pyTIN_library.triangulation import Triangulation
from pyTIN_library.isocontourer import IsoConturer
from pyTIN_library.triangulation_classes import Point
from pyTIN_library.triangulation_classes import Point, HeightLevel, HeightLeveler
from pyTIN_library.visualisation import plot_triangulation
from pyTIN_library.visualisation import visualize_profile, plotly_iso

from input_data.sample_data import point_in, trn_in, real, real_levels, user_bounds, real_bounds

# Сгенерируем точки по исходному набору в формате [x,y,z,...]
def input_data (point_in):
    points = []
    for i in range(0,len(point_in)-1, 3):
        point = Point(point_in[i], point_in[i+1], point_in[i+2])
        points.append(point)
    return points

import random
num_points = 100
min_coord, max_coord = 0, 1000
rnd_points = [Point(random.uniform(min_coord, max_coord), random.uniform(min_coord, max_coord),random.uniform(min_coord, max_coord)/100+10) for _ in range(num_points)]

points = rnd_points

#Создаём поверхность
surface = Triangulation()
#Добавляем в поверхность списком точки класса Points и создаём триангулляцию.
surface.triangulate(points)

#Добавим границы
surface.custom_bounds = Point.import_nxyz_csv('input_data\\random_bounds.csv', 0)
surface.insert_custom_bound_points()


#Генерируем уровни
step = 1
map_levels = HeightLeveler(HeightLeveler.define_contours_levels(surface.points, step))
map_levels.interpolate_color()
surface.levels = map_levels.get_correct_isolines_levels(surface.points) #Извлекаем уровни для изолиний
print(surface.levels)

#Строим изолинии
surface.build_contour_lines()


#Прорежаем изолинии
surface.cull_contour_lines(1)
#Сглаживаем спрайном Катмулла - Рома (точек на ребро и параметр натяжения 0-1)
surface.smooth_contour_lines(10, 0.5)

#Визуализация в matplotlib
#plot_triangulation(surface)

#Создаём граф для изоконтуров
graf = IsoConturer(map_levels.levels, points)
#Добавляем туда границы сетки
graf.add_bounds(surface.bounds)
#Добавляем изолинии
graf.add_isolines(surface.sm_contour_lines.copy())
#Строим изоконтура
graf.build_isocontours()
#Показываем
#visualize_profile(graf.points, surface.points, graf.isolines, graf.bounds, graf.isocontours)
plotly_iso(graf.isocontours, surface.points)