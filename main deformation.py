from triangulation import Triangulation
from isocontourer import IsoConturer
from triangulation_classes import Point

from visualisation import plot_triangulation
from visualisation import visualize_contours

from sample_data import point_in, trn_in, real, real_levels, user_bounds, real_bounds

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

points = input_data(real)

#points = input_data(point_in) #Создали список объектов класса Points по рабочему набору
custom_bounds_points =  input_data(user_bounds) #Создали список объектов класса Points по пользовательскому контуру
real_bounds_points =  input_data(real_bounds)

#Создаём поверхность
surface = Triangulation()
#Добавляем в поверхность списком точки класса Points и создаём триангулляцию.
surface.triangulate(points)
#Фильтруем треугольники по максимальной длине и минимальному углу
#surface.filter_triangles(20, 1)
#Определяем границы триангуляции по внешним рёбрам треугольников
surface.get_bounds()

#Добавим пользовательские внешние границы
surface.custom_bounds = real_bounds_points

#Добавим пользовательские внешние границы в набор точек
surface.insert_custom_bounds()

#Снова триангулируем
surface.triangulate(points)
surface.remove_outer_triangles()

surface.get_bounds()
#surface.levels = [-32]

#Генерируем уровни
step = 10
surface.define_contours_levels(0, step )

#Строим изолинии
surface.build_contour_lines()

#Прорежаем изолинии
surface.cull_contour_lines(1)
#Сглаживаем спрайном Катмулла - Рома (точек на ребро и параметр натяжения 0-1)
surface.smooth_contour_lines(10, 0.5)

#Визуализация в matplotlib
plot_triangulation(surface)

#Создаём граф для изоконтуров
graf = IsoConturer(surface.levels)
#Добавляем туда границы сетки
graf.add_bounds(surface.bounds)
#Добавляем изолинии
graf.add_isolines(surface.sm_contour_lines)
#Строим изоконтура
graf.build_isocontours(step)
#Показываем
visualize_contours(graf.points, surface.points, graf.isolines, graf.bounds, graf.isocontours)