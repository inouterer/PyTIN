from pyTIN_library.geometrytools import GeometryTools
from pyTIN_library.triangulation_classes import IsoLine, Point, HeightLeveler

from typing import List

class Isocontour:
    """Изоконтуры это замкнутые фигуры между изолиниями"""
    def __init__(self, points=None):
        self.level_index = 0
        self.from_height = 0
        self.to_height = 0
        self.points = points if points is not None else []  # Инициализация как пустой список, если points не передан
        self.rgb_color = ()

    def add_points(self, points):
        self.points.extend(points)

    def get_contour_points(self):
        return self.points

    def clear_contour_points(self):
        self.points = []  # Очистка как список

    def calculate_area(self):
        if len(self.points) < 3:  # Площадь не может быть вычислена, если менее 3 точек
            return 0

        area = 0
        n = len(self.points)
        for i in range(n):
            x1, y1 = self.points[i].x, self.points[i].y
            x2, y2 = self.points[(i + 1) % n].x, self.points[(i + 1) % n].y
            area += x1 * y2 - x2 * y1
        return abs(area) / 2
    
    def find_point_inside(self, allpoints):
        """
        Находит любую точку из набора allpoints, которая находится внутри изоконтура.
        Возвращает z-координату первой найденной точки, находящейся внутри контура, или None.
        """
       
        def is_point_inside_polygon(x, y, epsilon=0.01):
            """
            Проверяет, находится ли точка (x, y) внутри многоугольника с учетом допустимого расстояния от границы epsilon.
            Алгоритм: метод лучевого преобразования (Ray Casting method).
            """
            n = len(self.points)
            inside = False

            px, py = x, y
            for i in range(n):
                x1, y1 = self.points[i].x, self.points[i].y
                x2, y2 = self.points[(i + 1) % n].x, self.points[(i + 1) % n].y
                if ((y1 > py) != (y2 > py)) and (px < (x2 - x1) * (py - y1) / (y2 - y1) + x1):
                    if abs((x2 - x1) * (py - y1) - (y2 - y1) * (px - x1)) / ((x2 - x1)**2 + (y2 - y1)**2)**0.5 < epsilon:
                        return True
                    inside = not inside
            return inside

        for point in allpoints:
            if is_point_inside_polygon(point.x, point.y):
                return point.z

        return self.points[0].z
    

class IsoConturer:
    """
    Структура графа и методы для построения изоконтуров. 
    """
    def __init__(self, levels=None, allpoints=None) -> None:
        self.points = [] #Точки гарфа - контура триангуляции с точками входа и выхода изолиний
        self.isolines = []
        self.sections = []
        self.bounds = []
        self.isocontours = []
        self.levels = levels
        self.allpoints = allpoints[:] if allpoints is not None else []

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
    

    def build_isocontours (self):
        """Непосредственно строим изоконтуры"""
        
        def find_section_index (point):
            """Поиск номера сегмента на контуре графа"""
            for i, section in enumerate(self.sections):
                if point == section[0]:
                    return i
            return False
        
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
                        s = find_section_index (contour_noodle[-1][-1])#Вычисляем индекс секции на другом конце изолинии
                    #Если лапша замкнулась
                    if contour_noodle[0][0] == contour_noodle[-1][-1]:
                        iso = Isocontour()  # Создаем новый объект Isocontour
                        iso.points, last_noodles = gtools.assemble_polygon_from_noodles(contour_noodle)
                        self.isocontours.append(iso)  # Добавляем объект Isocontour в список isocotours
                        break
                    section = self.sections[s]
            return
        
        
        def define_loop_isocontour_levels(self, isocontour):
            """Определить интервал высот или значений замкнутого изоконтура

            Args:
                isocontour (bool): _description_
            """
            # Определим высоту изоконтура по отметке первой вершины и по отметке точки из набора данных внутри него:
            # Найдём высоту первой точки, если она маркирована, тоесть относится к изолинии
            fpoint_z = None
            for isocontour_point in isocontour.points: #Переберем точки изоконтура
                if isocontour_point.marked == True: #Пока не найдём маркированную - это выход изолини на граф
                    fpoint_z = isocontour_point.z
            if not fpoint_z: #Если высоты нет, значит это замкнутая изолиния
                fpoint_z = isocontour.points[0].z
            # Если точка выше первого узла изолинии то нижняя высота будет равна высоте точки, а верхння + шаг
            if fpoint_z < isocontour.find_point_inside(self.allpoints):
                isocontour.level_index = HeightLeveler.get_level_index_by_heigh_from(fpoint_z, self.levels)
                isocontour.from_height = self.levels[isocontour.level_index].height_from
                isocontour.to_height = self.levels[isocontour.level_index].height_to
            else:
                # Иначе, это верхняя высота, а нижняя минус шаг
                isocontour.level_index = HeightLeveler.get_level_index_by_heigh_to(fpoint_z, self.levels)
                isocontour.from_height = self.levels[isocontour.level_index].height_from
                isocontour.to_height = self.levels[isocontour.level_index].height_to
        
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
        #        
        levels_list = HeightLeveler.extract_levels_as_list(self.levels)#Извлечем списком уровни
        for isocontour in self.isocontours:#переберем изоконтуры
            levels = []
            for point in isocontour.points:
                levels.append(point.z) #соберем все высоты точек в контуре
            if min(levels) == max(levels):#Если все высоты одинаковы, то это замкнутый контур
                define_loop_isocontour_levels(self, isocontour)#Отправляем искать внутреннюю точку и определять интервал
            elif min(levels) in levels_list:
                isocontour.level_index = HeightLeveler.get_level_index_by_heigh_from(min(levels), self.levels)#Ищем Уровень, с таким НИЖНИМ значением
            elif max(levels) in levels_list:
                isocontour.level_index = HeightLeveler.get_level_index_by_heigh_to(max(levels), self.levels)#Ищем Уровень, с таким ВЕРХНИМ значением
            else:
                print (f'Нет уровня!!! {min(levels)} - {max(levels)}')
            isocontour.rgb_color = self.levels[isocontour.level_index].color_rgb # Присваиваем цвет

        
        # Сортировка списка по площади для корректного отображения изоконтуров на карте
        self.isocontours.sort(key=lambda contour: contour.calculate_area(), reverse=True)


    def interpolate_color(self, min_level, max_height, from_height, to_height):
        """
        Интерполяция градиента для изоконтуров
        
        """
        
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