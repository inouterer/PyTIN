import math
import pandas as pd
from pyTIN_library.geometrytools import GeometryTools

class Point:
    """
    Точки с отметкой высоты
    """
    
    def __init__(self, x=0, y=0, z=0, name=''):
        self.name = name
        self.x = x
        self.y = y
        self.z = z
        self.marked = False
    def __ne__(self, other):
        # Перегрузка оператора неравенства (!=)
        tolerance = 0.001
        return  (abs(self.x - other.x) > tolerance and
                 abs(self.y - other.y) > tolerance)
    def __eq__(self, other):
        # Перегрузка оператора равенства (==)
        tolerance = 0.001
        return  (abs(self.x - other.x) <= tolerance and
                 abs(self.y - other.y) <= tolerance)
    def __hash__(self):
        # Для хеширования используем кортеж из координат x и y
        return hash((self.x, self.y))
    
    def is_inside_polygon(self, polygon):
        """
        Проверяет, находится ли точка внутри полигона.

        :param polygon: Список вершин полигона, представленных в виде объектов Point.
        :return: True, если точка внутри полигона, и False в противном случае.
        """
        n = len(polygon)
        intersections = 0

        for i in range(n):
            p1 = polygon[i]
            p2 = polygon[(i + 1) % n]
            if ((p1.y <= self.y and p2.y > self.y) or
                (p1.y > self.y and p2.y <= self.y)) and \
                    self.x < (p2.x - p1.x) * (self.y - p1.y) / (p2.y - p1.y) + p1.x:
                intersections += 1

        return intersections % 2 == 1
    
    @staticmethod
    def import_nxyz_csv(path, offset=0):
        """
        Получат точки из CSV.

        """
        df = pd.read_csv(path, header=None, delimiter=';')# Чтение CSV файла с указанием разделителя ';'
        points = [] # Создание пустого списка для хранения объектов Point
        # Проход по каждой строке значений z
        for index, row in df.iloc[0:].iterrows():
            points.append(Point(row[offset+1], row[offset+2], row[offset+3], row[offset+0]))
        return points
   


class Edge:
    """Ребро триангуляции. Состоит из двух точек"""
    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.length = self.calculate_length()

    def __eq__(self, other):
        return (self.start == other.start and self.end == other.end) or \
               (self.start == other.end and self.end == other.start)

    def calculate_length(self):
        return ((self.end.x - self.start.x) ** 2 + (self.end.y - self.start.y) ** 2) ** 0.5
    def __hash__(self):
        # Для хеширования используем кортеж из координат начала и конца ребра
        return hash((self.start, self.end))


class IsoLine:
    """
    Изолинии с высотой. Точки хранятс списком.
    
    У замкнутых первая и последняя точка одинаковая
    """
    def __init__(self, height):
        # Инициализация изолинии с указанием высоты
        self.height = height
        self.points = []  # Список точек изолинии

    def add_point_front(self, point):
        # Добавление точки в начало изолинии
        self.points=[point]+self.points

    def add_point_back(self, point):
        # Добавление точки в конец изолинии
        self.points.append(point)

    def __eq__(self, other):
        # Перегрузка оператора равенства (==)
        return self.x == other.x and self.y == other.y
    def __ne__(self, other):
        # Перегрузка оператора равенства (==)
        return self.x != other.x and self.y != other.y


class Triangle:
    """
    Треугольники. Состоят из ребер.

    Встроены методы поиска окружности, длины короткого ребра и наименьшего угла.
    """
    EPS = 1e-7 #величина для округления

    def __init__(self, edge1, edge2, edge3):
        self.edges = [edge1, edge2, edge3]
        self.neighbors = []
        self.marked = False  # Установка атрибута marked по умолчанию в False

    def __repr__(self):
        return f'Triangle({self.edges[0]}, {self.edges[1]}, {self.edges[2]})'

    # Перегрузка оператора равенства (!=)
    def __eq__(self, other):
        return self.edges == other.edges

    # Выдаёт точки треугольника обрабатывая ребра
    def extract_points(self):
        points = []
        for edge in self.edges:
            if edge.start not in points:
                points.append(edge.start)
            if edge.end not in points:
                points.append(edge.end)
        return points

 
    def triangle_centroid(self):
        """
        Вычисляет центр треугольника по его вершинам.

        :param p1: Первая вершина треугольника, объект Point.
        :param p2: Вторая вершина треугольника, объект Point.
        :param p3: Третья вершина треугольника, объект Point.
        :return: Координаты центра треугольника в виде списка [x, y]."""

        p1 = self.edges[0].start
        p2 = self.edges[0].end
        p3 = None
        for edge in self.edges[1:]:
            if edge.start in [p1, p2]:
                p3 = edge.end
                break
            elif edge.end in [p1, p2]:
                p3 = edge.start
                break
        if p3 is None:
            raise ValueError("Unable to find third point of triangle")
        
        x = (p1.x + p2.x + p3.x) / 3
        y = (p1.y + p2.y + p3.y) / 3
        return Point(x, y, 0)



   # Вычисляет центр окружности через точки треугольника
    def circumcenter(self):
        p1 = self.edges[0].start
        p2 = self.edges[0].end
        p3 = None

        for edge in self.edges[1:]:
            if edge.start in [p1, p2]:
                p3 = edge.end
                break
            elif edge.end in [p1, p2]:
                p3 = edge.start
                break
        if p3 is None:
            raise ValueError("Unable to find third point of triangle")

        x1, y1 = p1.x, p1.y
        x2, y2 = p2.x, p2.y
        x3, y3 = p3.x, p3.y

        dy12 = abs(y1 - y2)
        dy23 = abs(y2 - y3)
        if dy12 < self.EPS:
            m2 = -((x3 - x2) / (y3 - y2))
            mx2 = (x2 + x3) / 2
            my2 = (y2 + y3) / 2
            xc = (x1 + x2) / 2
            yc = m2 * (xc - mx2) + my2
        elif dy23 < self.EPS:
            m1 = -((x2 - x1) / (y2 - y1))
            mx1 = (x1 + x2) / 2
            my1 = (y1 + y2) / 2
            xc = (x2 + x3) / 2
            yc = m1 * (xc - mx1) + my1
        else:
            m1 = -((x2 - x1) / (y2 - y1))
            m2 = -((x3 - x2) / (y3 - y2))
            mx1 = (x1 + x2) / 2
            my1 = (y1 + y2) / 2
            mx2 = (x2 + x3) / 2
            my2 = (y2 + y3) / 2
            xc = (m1 * mx1 - m2 * mx2 + my2 - my1) / (m1 - m2)
            if dy12 > dy23:
                yc = m1 * (xc - mx1) + my1
            else:
                yc = m2 * (xc - mx2) + my2
        return xc, yc

    def circumradius(self):
        xc, yc = self.circumcenter()
        dx = self.edges[0].start.x - xc  # Исправлено на self.edges[0]
        dy = self.edges[0].start.y - yc  # Исправлено на self.edges[0]
        r2 = dx * dx + dy * dy
        return r2

    # находит минимальный угол в треугольнике
    def min_angle(self):
        angles = []
        points = self.extract_points()  # Получаем точки треугольника
        for i in range(3):
            p1 = points[i]
            p2 = points[(i + 1) % 3]
            p3 = points[(i + 2) % 3]

            dx1 = p1.x - p2.x
            dy1 = p1.y - p2.y
            dx2 = p3.x - p2.x
            dy2 = p3.y - p2.y

            dot_product = dx1 * dx2 + dy1 * dy2
            magnitude_v1 = math.sqrt(dx1 ** 2 + dy1 ** 2)
            magnitude_v2 = math.sqrt(dx2 ** 2 + dy2 ** 2)

            if magnitude_v1 == 0 or magnitude_v2 == 0:
                # Предотвращаем деление на ноль
                continue

            angle = dot_product / (magnitude_v1 * magnitude_v2)
            angle = max(min(angle, 1), -1)  # Ограничиваем значения аргумента для арккосинуса
            angle_rad = math.acos(angle)  # Вычисляем арккосинус
            angles.append(angle_rad)

        if not angles:
            # Если список углов пустой, вернем нулевой угол
            return 0

        min_angle_rad = min(angles)
        min_angle_degrees = min_angle_rad * 180 / math.pi  # Преобразуем радианы в градусы
        return min_angle_degrees

    # Самое длинное ребро
    def max_edge(self):
        lenghts = []
        for edge in self.edges:
            edge.calculate_length()
            lenghts.append(edge.calculate_length())
        return max (lenghts)
    
    # Выдаёт точки треугольника обрабатывая ребра
    def extract_points(self):
        points = []
        for edge in self.edges:
            if edge.start not in points:
                points.append(edge.start)
            if edge.end not in points:
                points.append(edge.end)
        return points
    
    def get_point_by_line(self, p1, p2):
        """
        Возвращает точку в центре отрезка, образованного точками пересечения с ребрами треугольника.

        :param p1: Начальная точка отрезка, объект Point.
        :param p2: Конечная точка отрезка, объект Point.
        :return: Точка xyz - центр отрезка с отметкой, объект Point.
        """
        intersections = []  # Список для хранения точек пересечения с ребрами треугольника

        # Проверяем пересечение линии с каждым ребром треугольника
        for edge in self.edges:
            intersection_point = GeometryTools.calculate_intersection(p1, p2, edge.start, edge.end)
            if intersection_point:
                intersections.append(intersection_point)

        if len(intersections) < 2:
            #raise ValueError("Line does not intersect triangle or intersects less than 2 edges")
            return None

        # Находим высоту точек пересечения на ребрах и создаем новые точки с этой высотой
        z1 = intersections[0].z
        z2 = intersections[1].z
        x = (intersections[0].x + intersections[1].x) / 2
        y = (intersections[0].y + intersections[1].y) / 2
        z = (z1 + z2) / 2

        return Point(x, y, z)

    def calculate_triangle_area(self):
        """
        Вычисляет площадь треугольника по формуле Герона.

        :return: Площадь треугольника.
        """
        a = self.edges[0].calculate_length()
        b = self.edges[1].calculate_length()
        c = self.edges[2].calculate_length()

        s = (a + b + c) / 2
        area = (s * (s - a) * (s - b) * (s - c)) ** 0.5

        return area
    
    def is_inside_triangle(self, point, tolerance=0.001):
        """
        Проверяет, находится ли точка внутри треугольника с заданным допуском.

        :param point: Точка, которую нужно проверить, объект Point.
        :param tolerance: Допуск для проверки.
        :return: True, если точка находится внутри треугольника, иначе False.
        """
        total_area = self.calculate_triangle_area()
        point_area = sum(0.5 * abs((edge.start.x - point.x) * (edge.end.y - edge.start.y) - (edge.start.x - edge.end.x) * (point.y - edge.start.y)) for edge in self.edges)

        return abs(total_area - point_area) < tolerance
    
    def interpolate_z(self, point, tolerance=0.001):
        """
        Интерполирует значение z для точки внутри треугольника с заданным допуском.

        :param point: Точка, для которой нужно интерполировать значение z, объект Point.
        :param tolerance: Допуск для определения, находится ли точка внутри треугольника.
        :return: Интерполированное значение z для точки, если она находится внутри треугольника, иначе None.
        """
        if not self.is_inside_triangle(point, tolerance):
            return None

        total_area = self.calculate_triangle_area()
        weights = []

        for edge in self.edges:
            p1 = edge.start
            p2 = edge.end
            p3 = point

            area = 0.5 * abs((p1.x - p3.x) * (p2.y - p1.y) - (p1.x - p2.x) * (p3.y - p1.y))
            weight = area / total_area
            weights.append(weight)

        interpolated_z = sum(weight * point.z for weight, point in zip(weights, self.extract_points()))
        return interpolated_z


  
class HeightLevel:
    """
    Класс Level представляет уровень с высотой "от" и "до" и цветом RGB.

    Атрибуты:
    - height_from: высота начала диапазона
    - height_to: высота конца диапазона
    - color_rgb: кортеж с тремя значениями RGB в 16-ричной форме
    """

    def __init__(self, level_index, height_from, height_to, color_rgb=None):
        """
        Инициализирует объект Level с заданными высотами и цветом RGB.
        """
        self.level_index = level_index
        self.height_from = height_from
        self.height_to = height_to
        self.color_rgb = self.color_rgb = color_rgb[:] if color_rgb is not None else []

    def __str__(self):
        """
        Возвращает строковое представление объекта Level.
        """
        return f"Level:{self.level_index} H from: {self.height_from}, H to: {self.height_to}, Color RGB: {self.color_rgb}"

class HeightLeveler:
    """
    Класс для управления уровнями и их упорядочивания.

    Атрибуты:
    levels (list): Список уровней, отсортированных по возрастанию
    corrected_levels: Список скорректированных для построения изолиний уровней
    intervals (list): Список список интервалов.

    Методы:

    read_cmp_file
    get_level_index_by_heigh_from
    get_level_index_by_heigh_to
    get_level_index(value): Возвращает индекс указанного уровня.

    """

    def __init__(self, levels=None):
        """
        Инициализирует объект Levels с заданным списком уровней.

        Аргументы:
        levels (list): Список уровней.
        """
        self.levels = levels[:] if levels is not None else [] #Этот тернарный оператор сделает копию списка levels или если не указано создаст пустой список
    
    def __str__(self):
        """
        Возвращает строковое представление объекта Level.
        """
        return '\n'.join([str(level) for level in self.levels])
    
    @staticmethod
    def read_cmp_file(file_path):
        """
        Статический метод для чтения файла *.cmp и создания объектов Level на основе данных из файла.

        Аргументы:
        - file_path: путь к файлу *.cmp

        Возвращает:
        - Список объектов Level, созданных на основе данных из файла
        """
        levels = []
        with open(file_path, 'r') as file:
            for index, line in enumerate(file):
                data = line.strip().split(', ')
                height_from = float(data[0])
                height_to = float(data[1])
                #color_rgb = tuple(int(x, 16) for x in data[2:])
                color_rgb = [int(x, 16) for x in data[2:]]
                level = HeightLevel(index, height_from, height_to, color_rgb)
                levels.append(level)
        return levels
    
    
    @staticmethod
    def get_level_index_by_heigh_from(value, levels):
        """
        Возвращает индекс указанного уровня по высоте height_from.

        Аргументы:
        value (float): Значение уровня.

        Возвращает:
        int: Индекс уровня или None, если уровень не найден.
        """
        # Ищем индекс уровня с заданной нижней отметкой
        # index = next((index for index, level in enumerate(levels) if level.height_from == round(value, 1)), None)
        index = next((index for index, level in enumerate(levels) if level.height_from == value), None)
        if index is not None:
            return index
        else:
            return None
        
    @staticmethod
    def get_level_index_by_heigh_to(value, levels):
        """
        Возвращает индекс указанного уровня по высоте height_from.

        Аргументы:
        value (float): Значение уровня.

        Возвращает:
        int: Индекс уровня или None, если уровень не найден.
        """
        # Ищем индекс уровня с заданной нижней отметкой
        # index = next((index for index, level in enumerate(levels) if level.height_to == round(value, 1)), None)
        index = next((index for index, level in enumerate(levels) if level.height_to == value), None)
        if index is not None:
            return index
        else:
            return None


    @staticmethod
    def define_contours_levels(points, step=1, low=None):
        """Определяет список отметок по заданному шагу."""
        #Вычислим предельные высоты и округлим до десятых
        min_height = math.floor(min(point.z for point in points))
        max_height = math.ceil(max(point.z for point in points))

        # Создать список интервалов, начиная с 0 или low
        height_values = []
        if not low:
            low = round (min_height)
        current_height = low
        while current_height <= max_height:
            height_values.append(current_height)
            current_height += step
        
        # Отфильтровать интервалы в пределах от min_height до max_height
        height_values = [height for height in height_values if min_height <= height <= max_height]
        
        # Если минимальная высота не входит в интервалы, добавляем её в начало
        if height_values[0] > min_height:
            height_values.insert(0, min_height)
        
        # Если максимальная высота не входит в интервалы, добавляем её в конец
        if height_values[-1] < max_height:
            height_values.append(max_height)
        
        corrected_levels = []
        eps = 0.01  # Малая величина для коррекции высоты изолиний, сотая доля шага
        for cur_level in height_values:
            # Проверяем и корректируем высоту, чтобы избежать точного совпадения с высотами точек
            while any(point.z == cur_level for point in points):
                if cur_level <= 0:
                    cur_level += eps
                else:
                    cur_level -= eps
            corrected_levels.append(cur_level)
        
        levels = []
        n = len(corrected_levels)-1
        for ind in range(n):
            h1 = corrected_levels[ind]
            h2 = corrected_levels[ind+1]  
            levels.append(HeightLevel(ind,h1,h2,))
        return levels
    
    def get_correct_isolines_levels(self, points):
        """
        Список высот для построения изолиний с корректировкой.

        Аргументы:
        points: список точек триангуляции

        Возвращает:
        List: .
        """
        eps = 0.01  # Малая величина для коррекции высоты изолиний, сотая доля шага
        corrected_levels = []
        
        levels = [level.height_from for level in self.levels] #Извлечь нижние высоты из уровней
        levels.append(self.levels[-1].height_to) #Добавить верхнюю высоту верхнего уровня

        for cur_level in levels:
            # Проверяем и корректируем высоту, чтобы избежать точного совпадения с высотами точек
            while any(point.z == cur_level for point in points):
                if cur_level <= 0:
                    cur_level += eps
                else:
                    cur_level -= eps
            corrected_levels.append(cur_level)
        
        #Скорректируем отметки и в Height_Level, иначе будут проблемы с определением высот изоконтуров
        for index, lvl in enumerate(self.levels):
            lvl.height_from = corrected_levels[index]
            lvl.height_to = corrected_levels[index+1]

        
        return corrected_levels
    

    
    def interpolate_color(self):
        """Интерполяция градиента для изоконтуров"""
        from_height = self.levels[0].height_from
        to_height = self.levels[-1].height_from
        for level in self.levels:
            # Нормализуем высоты к интервалу [0, 1]
            norm_from_height = (level.height_from - from_height)  / (to_height - from_height)
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
            level.color_rgb = [red, green, blue]
        return
    
    @staticmethod
    def extract_levels_as_list (levels):
        """Просто список уровней

        Args:
            levels (_type_): _description_
        """
        levels_list = []
        for level in levels:
            levels_list.append(level.height_from)
        levels_list.append(levels[-1].height_to)
        print (f'extract_levels_as_list {levels_list}')
        return levels_list
