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



#Создаём поверхность
total_start_time = time.time()
start_time = time.time()

#Добавляем в поверхность списком точки класса Points и создаём триангулляцию.
start_time = time.time()
print("Триангулируем...")
surface = Triangulation()
surface.triangulate(points)
end_time = time.time()    # Время окончания выполнения
print(f"...Время выполнения: {end_time - start_time} секунд")

start_time = time.time()
print("Строим границы...")
surface.get_bounds()
end_time = time.time() # Время окончания выполнения
print(f"...Время выполнения: {end_time - start_time} секунд")

#Генерируем уровни
print("Обработка изолиний...")
print("Генерируем уровни")
start_time = time.time()
step = 1
#surface.define_contours_levels(-10,step)
surface.levels = [-20, -10,  -6, -5, -4, -3, -2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2]
print("Коррекция уровней")
surface.correct_levels()

#Строим изолинии
start_time = time.time()
print("Строим изолинии")
surface.build_contour_lines()

#Прорежаем изолинии
print("Прорежаем изолинии")
surface.cull_contour_lines(1)
#Сглаживаем спрайном Катмулла - Рома (точек на ребро и параметр натяжения 0-1)
#surface.smooth_contour_lines(10, 0.5)
end_time = time.time()    # Время окончания выполнения
print(f"...Время выполнения: {end_time - start_time} секунд")

#Создаём граф для изоконтуров
start_time = time.time()
print("Собираем изоконтуры...")
graf = IsoConturer(surface.levels, points)
#Добавляем туда границы сетки
graf.add_bounds(surface.bounds)
#Добавляем изолинии
graf.add_isolines(surface.contour_lines.copy())
#graf.add_isolines(surface.sm_contour_lines.copy())
#Строим изоконтура
graf.build_isocontours(step)
end_time = time.time()    # Время окончания выполнения
print(f"...Время построения изоконтуров: {end_time - start_time} секунд")

#Показываем
start_time = time.time()
print("Визуализация...")
visualize_profile(graf.points, surface.points, graf.isolines, graf.bounds, graf.isocontours)
end_time = time.time()    # Время окончания выполнения
print(f"...Время выполнения: {end_time - start_time} секунд")
print(f"Общее время выполнения: {end_time - total_start_time} секунд")