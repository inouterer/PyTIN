from triangulation import Triangulation
from isocontourer import IsoConturer
from triangulation_classes import Point

from visualisation import plot_triangulation
from visualisation import visualize_contours, visualize_profile

import pandas as pd

# Чтение CSV файла с указанием разделителя ';'
df = pd.read_csv('profil_test.csv', header=None, delimiter=';')

# Получение значений глубин из первой строки и преобразование их в список
depths = df.iloc[0].tolist()

# Создание пустого списка для хранения объектов Point
points = []

# Начальное значение для координаты x
x_value = 0

# Проход по каждой строке значений температуры, начиная со второй строки
for index, row in df.iloc[1:].iterrows():
    temp_values = row.tolist()
    for depth, temp in zip(depths, temp_values):
        point = Point(x_value, depth*-1, float(temp))
        points.append(point)
    x_value += 100  # Увеличение координаты x на 100 для следующей строки

# Вывод результатов
for point in points:
    print(point)

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
step = 1
surface.define_contours_levels(-10,step)

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