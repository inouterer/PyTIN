from geometrytools import GeometryTools
from triangulation_classes import IsoLine, Isocontour, Point

from typing import List


class IsoConturer:
    """
    Структура графа и методы для построения изоконтуров. 
    """
    def __init__(self, levels=[], allpoints=[]) -> None:
        self.points = [] #Точки гарфа - контура триангуляции с точками входа и выхода изолиний
        self.isolines = []
        self.sections = []
        self.bounds = []
        self.isocontours = []
        self.levels = levels
        self.allpoints = allpoints[0:len(allpoints)]

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
            #Помечаем точки выхода и входа изолиний
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

    def find_isoline_for_point2 (self, point):
        """Ищем изолинию, в которой такая точка"""
        for isoline in self.isolines:
            if (isoline[0] == point) or (isoline[-1] == point):
                iso = isoline
                #self.isolines.remove(isoline)
                #print (len(iso))
                return iso
    def find_isoline_for_point (self, point):
        """Ищем изолинию, в которой такая точка"""
        for isoline in self.isolines:
            if isoline[0] == point:
                return isoline
            if isoline[-1] == point:
                return isoline[::-1]
    
    def find_isoline_for_point2  (self, point):
        """Ищем изолинию, в которой такая точка"""
        x = 0
        while x<len(self.isolines):
            
            if (self.isolines[x][0] == point) or (self.isolines[x][-1] == point):
                #isoline = self.isolines.pop(x)
                #print (len(isoline), x)
                return isoline
            x+=1

    def build_isocontours (self, step):
        """Непосредственно строим изоконтуры"""
        
        def find_section_index (point):
            """Поиск номера сегмента на контуре графа"""
            for i, section in enumerate(self.sections):
                if point == section[0]:
                    return i
            return False


        def trace_isocontour2():
            """Построение изоконтуров из ребер графа и изолиний с замыканием по методу похожему на Скворцова"""
            visited_sections = []
            gtools = GeometryTools()
            s = 0 #Номер секции
            while len(visited_sections) < len(self.sections):
                #Проходим по часовой стрелке по рёбрам (секциям) графа и находим непосещенную.
                contour_noodle = []
                isocontour = []
                #Если вышли за индекс - начинаем снова
                if s >= len (self.sections)-1:
                        s = 0
                section = self.sections[s]
                #Если секция в посещенных - идём дальше
                if section in visited_sections:
                    s+=1
                    continue
                #Непосещенные секции последовательно собираем.
                while len(visited_sections) < len(self.sections):
                    if section not in visited_sections:
                        visited_sections.append(section) #Отмечаем посещенную
                        contour_noodle.append(section) #Добавляем секцию в лапшу
                        s+=1
                    #Если вторая точка секции принадлежит входу изолинии - сцепляем изолинию с секцией.
                    if section[-1].marked: #Маркированные точки графа относятся  к изолиниям, в отличии от точек контура!!!
                        finded_isoline = self.find_isoline_for_point (section[-1])
                        contour_noodle.append(finded_isoline)

                    #Собираем куски (и только секции и секции с изолиниями) вместе
                    isocontour, last_noodles = gtools.assemble_polygon_from_noodles(contour_noodle)
                    s = find_section_index (isocontour [-1])

                    contour_noodle= []
                    contour_noodle.append(isocontour)

                    if isocontour[0] == isocontour[-1]:
                        iso = Isocontour(0, 0)  # Создаем новый объект Isocontour
                        iso.add_points(isocontour)  # Добавляем точки в объект Isocontour
                        if iso.calculate_area()>0.1:
                            self.isocontours.append(iso)  # Добавляем объект Isocontour в список isocotours
                        break
                    section = self.sections[s]
            return
        
        def trace_isocontour():
            """Построение изоконтуров из ребер графа и изолиний с замыканием по методу похожему на Скворцова"""
            visited_sections = []
            gtools = GeometryTools()
            s = 0 #Номер секции
            while len(visited_sections) < len(self.sections):
                #Проходим по часовой стрелке по рёбрам (секциям) графа и находим непосещенную.
                contour_noodle = []
                #Если вышли за индекс - начинаем снова
                if s >= len (self.sections)-1:
                        s = 0
                section = self.sections[s]
                #Если секция в посещенных - идём дальше
                if section in visited_sections:
                    s+=1
                    continue
                #Непосещенные секции последовательно собираем.
                while len(visited_sections) < len(self.sections):
                    if section not in visited_sections:
                        visited_sections.append(section) #Отмечаем посещенную
                        contour_noodle.append(section) #Добавляем секцию в лапшу
                        s+=1
                    #Если вторая точка секции принадлежит входу изолинии - сцепляем изолинию с секцией.
                    if section[-1].marked: #Маркированные точки графа относятся  к изолиниям, в отличии от точек контура!!!
                        contour_noodle.append(self.find_isoline_for_point (section[-1]))
                        s = find_section_index (contour_noodle[-1][-1])
                    #Если лапша замкнулась
                    if contour_noodle[0][0] == contour_noodle[-1][-1]:
                        iso = Isocontour()  # Создаем новый объект Isocontour
                        iso.points, last_noodles = gtools.assemble_polygon_from_noodles(contour_noodle)
                        self.isocontours.append(iso)  # Добавляем объект Isocontour в список isocotours
                        break
                    section = self.sections[s]
            return
        
        
        def define_isocontour_levels(self, iso):
            # Определим высоту изоконтура по отметке первой вершины и по отметке точки из набора данных внутри него:
            # Наёдём высоту первой точки, если она маркирована, тоесть относится к изолинии
            fpoint_z = None
            for ipoint in iso.points:
                if point.marked == True:
                    fpoint_z = ipoint.z
            if not fpoint_z: #Или первую попавшуюся, значит это замкнутая изолиния
                fpoint_z = iso.points[0].z
                #rint(f'Яйцо {fpoint_z}')
            # Если точка выше первого узла изолинии то нижняя высота будет равна высоте точки, а верхння + шаг
            if fpoint_z < iso.find_point_inside(self.allpoints):
                iso.from_height, iso.to_height = fpoint_z, fpoint_z + step
            else:
                # Иначе, это верхняя высота, а нижняя минус шаг
                iso.from_height, iso.to_height = fpoint_z - step, fpoint_z
            if fpoint_z == iso.find_point_inside(self.allpoints):
                #print (f'define_isocontour_levels_Panic!!!!!!!!{iso.points[0].z} {iso.points[0].marked} {iso.find_point_inside(self.allpoints)}')
                return
        
        #Здесь мы создаём точки графа, проходя по контуру объекта на его узлах и
        #на входах и выходах изолиний в порядке по часовой
        edge_points = []
        for isoline in self.isolines:
            edge_points.append(isoline[0])
            edge_points.append(isoline[-1])
        self.points = self.find_and_sort_points_on_polygon(edge_points)
 
        #Добавляем замкнутые изолинии - они уже готовые изоконтуры
        for isoline in self.isolines:
            if isoline[0] == isoline[-1]:
                isoсontour = Isocontour()  # Создаем новый объект Isocontour
                isoсontour.add_points(isoline)  # Добавляем точки в объект Isocontour
                self.isocontours.append(isoсontour)

        #Сделаем ребра графа sections. 
        if len(self.points) < 2:
            return
        # Создание отрезков между последовательными точками
        self.sections = [[self.points[i], self.points[i + 1]] for i in range(len(self.points) - 1)]
        # Добавление отрезка между последней и первой точкой, чтобы закрыть контур
        self.sections.append([self.points[-1], self.points[0]])
        
        #Собираем изоконтуры, которые выходят из графа
        trace_isocontour()

        #Находим диапазоны изолиний
        min_level = min (self.levels)
        max_level = max (self.levels)
        for isocontour in self.isocontours:
            levels = []
            for point in isocontour.points:
                for graf_point in self.points:
                    if point == graf_point and point.z in self.levels:
                        levels.append(graf_point.z)
            if levels and min(levels) != max(levels):
                isocontour.from_height = min(levels) #round(min_height,1)
                isocontour.to_height = max(levels) #round(max_height,1)
            else:
                # isocontour.from_height = -20
                # isocontour.to_height = -10
                # if min(levels) == max(levels):
                define_isocontour_levels(self, isocontour)
            #Назначим цвет
            isocontour.rgb_color = self.interpolate_color(min_level, max_level, isocontour.from_height, isocontour.to_height)
        
        # Сортировка списка по площади для корректного отображения изоконтуров на карте
        self.isocontours.sort(key=lambda contour: contour.calculate_area(), reverse=True)

        # for isocontour in self.isocontours:
        #     print (isocontour.points[0].z)

    def interpolate_color(self, min_level, max_height, from_height, to_height):
        """Интерполяция градиента для изоконтуров"""
        
        # Нормализуем высоты к интервалу [0, 1]
        norm_from_height = (from_height - min_level) / (max_height - min_level)
        if norm_from_height < 0:
            norm_from_height = 0
        
        # Находим компоненты RGB цвета для синего, зеленого и красного
        blue = 1.0 - norm_from_height  # Синий уменьшается с ростом высоты
        green = 1.0 - abs(norm_from_height - 0.5) * 2  # Зеленый максимален посередине, минимален на краях
        red = norm_from_height  # Красный увеличивается с ростом высоты
        
        # Конвертируем значения компонентов в диапазон [0, 255]
        blue = int(blue * 255)
        green = int(green * 255)
        red = int(red * 255)
        
        return (red, green, blue)