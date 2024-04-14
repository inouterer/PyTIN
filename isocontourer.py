from geometrytools import GeometryTools
from triangulation_classes import IsoLine, Isocontour, Point


import matplotlib.pyplot as plt


import random
from typing import List


class IsoConturer:
    """
    Структура и методы для построения изоконтуров
    """
    def __init__(self) -> None:
        self.points = []
        self.isolines = []
        self.sections = []
        self.bounds = []
        self.isocontours = []

    def add_bounds (self, bounds: List[Point]):
        """Получит границы триангуляции"""
        self.bounds = bounds

    def add_isolines (self, isolines: List[IsoLine]):
        """Добавит изолинии из класса IsoLine как список списков точек"""
        lines = [line.points for line in isolines]
        self.isolines.extend(lines)

    def is_point_on_edge(self, point, a, b, epsilon=1e-3):
        """Расчет коллинеарности точки point с отрезком a-b"""
        if abs((point.y - a.y) * (b.x - a.x) - (b.y - a.y) * (point.x - a.x)) > epsilon:
            return False
        # Проверка, находится ли точка между вершинами a и b по обоим координатам с учетом допуска
        if min(a.x, b.x) - epsilon <= point.x <= max(a.x, b.x) + epsilon and min(a.y, b.y) - epsilon <= point.y <= max(a.y, b.y) + epsilon:
            return True
        return False

    def sort_points_on_edge(self, points, a, b):
        """Сортировка точек на ребре по их проекции на вектор ребра"""
        points.sort(key=lambda p: ((p.x - a.x) * (b.x - a.x) + (p.y - a.y) * (b.y - a.y)))
        for point in points:
            point.marked = True
        return points

    def find_and_sort_points_on_polygon(self, points):
        """
        Находим и сортируем точки на графе так,
        что бы включить в него все точки границы и входы и
        выходы полилиний по порядку по часовой стрелке
        """
        ordered_points = []
        n = len(self.bounds)
        for i in range(n):
            a = self.bounds[i]
            b = self.bounds[(i + 1) % n]
            points_on_edge = [p for p in points if self.is_point_on_edge(p, a, b)]
            if points_on_edge:
                sorted_points = self.sort_points_on_edge(points_on_edge, a, b)
                ordered_points.append(a)
                ordered_points.extend(sorted_points)
            else:
                ordered_points.append(a)
        return ordered_points[:-1] #Не добавляем последнюю точку, чтобы не задваивалась

    def find_isoline_for_point  (self, point):
        """Ищем изолинию, в которой точка"""
        for isoline in self.isolines:
            if (isoline[0] == point) or (isoline[-1] == point):
                return isoline


    def build_isocontours (self):
        """Непосредственно строим изоконтуры"""

        def find_point_index(point):
            """Поиск номера точки на контуре графа"""
            for i, p in enumerate(self.points):
                if point == p:
                    return i
            return -1

        #Здесь мы создаём точки графа, проходя по контуру объекта на его узлах и
        #на входах и выходах изолиний в порядке по часовой
        edge_points = []
        for isoline in self.isolines:
            for point in isoline:
                edge_points.append(point)
        self.points = self.find_and_sort_points_on_polygon(edge_points)



        #Добавляем замкнутые изолинии - они уже готовые изоконтуры
        for isoline in self.isolines:
            if isoline[0] == isoline[-1]:
                low_level = isoline[-1].z #Нижнее значение изоконтура
                iso = Isocontour(low_level, 0)  # Создаем новый объект Isocontour
                iso.add_points(isoline)  # Добавляем точки в объект Isocontour
                self.isocontours.append(iso)

        #Сделаем ребра графа. 
        if len(self.points) < 2:
            return
                # Создание отрезков между последовательными точками
        self.sections = [[self.points[i], self.points[i + 1]] for i in range(len(self.points) - 1)]
        # Добавление отрезка между последней и первой точкой, чтобы закрыть контур
        self.sections.append([self.points[-1], self.points[0]])


        def find_section_index (point):
            """Поиск номера сегмента на контуре графа"""
            for i, section in enumerate(self.sections):
                if point == section[0]:
                    return i



        def trace_isocontour():
            visited_sections = []
            manager = GeometryTools()
            s = 0
            while len(visited_sections) < len(self.sections):
                #Проходим по рёбрам или секциям графа и строим выходящие контуры
                contour_noodle = []
                isocontour = []
                if s > len (self.sections)-1:
                        s = 0
                section = self.sections[s]
                if section in visited_sections:
                    s+=1
                    continue

                while len(visited_sections) < len(self.sections):
                    if section not in visited_sections:
                        visited_sections.append(section)
                        contour_noodle.append(section)
                        s+=1

                    if section[-1].marked:
                        finded_isoline = self.find_isoline_for_point (section[-1])
                        contour_noodle.append(finded_isoline)


                    isocontour, last_noodles = manager.assemble_polygon_from_noodles(contour_noodle)

                    if section[-1].marked:
                        s = find_section_index (isocontour [-1])

                    contour_noodle= []
                    contour_noodle.append(isocontour)

                    if isocontour[0] == isocontour[-1]:
                        iso = Isocontour(0, 0)  # Создаем новый объект Isocontour
                        iso.add_points(isocontour)  # Добавляем точки в объект Isocontour
                        self.isocontours.append(iso)  # Добавляем объект Isocontour в список isocotours
                        break
                    section = self.sections[s]

        #self.visualize()
        trace_isocontour()


        #Находим диапазоны изолиний
        for isocontour in self.isocontours:
            levels = []
            for point in isocontour.points:
                for graf_point in self.points:
                    if point == graf_point:
                        levels.append(graf_point.z)
                if levels:
                    min_height = min(levels)
                    max_height = max(levels)
                    isocontour.from_height = round(min_height,1)
                    isocontour.to_height = round(max_height,1)

        #Сортируем по возрастанию нижней высоты
        self.isocontours = sorted(self.isocontours, key=lambda x: x.from_height, reverse=False)
