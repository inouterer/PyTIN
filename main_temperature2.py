import time

from triangulation import Triangulation
from isocontourer import IsoConturer
from triangulation_classes import Point

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
start_time = time.time()
#Создаём поверхность
print("Поверхность")
surface = Triangulation()
#Добавляем в поверхность списком точки класса Points и создаём триангулляцию.
print("Триангулируем")
surface.triangulate(points)
print("Границы")
#Определяем границы триангуляции по внешним рёбрам треугольников
surface.get_bounds()

#Генерируем уровни
step = 1.25
surface.define_contours_levels(-10,step)
#surface.levels = [-10, -7, -5, -3, -1.5, -0.5, 0, 0.5, 1.5, 3, 5, 7]

surface.correct_levels()
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

end_time = time.time()    # Время окончания выполнения
execution_time = end_time - start_time
print(f"Время выполнения: {execution_time} секунд")

#Показываем
visualize_profile(graf.points, surface.points, graf.isolines, graf.bounds, graf.isocontours)
