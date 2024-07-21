import math
import pandas as pd
from geometrytools import GeometryTools

class Point:
    """
    Точки с отметкой высоты
    """
    
    def __init__(self, x=0, y=0, z=0):
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
    def import_xyz_csv(path, offset=0):
        """
        Получат точки из CSV.

        """
        df = pd.read_csv(path, header=None, delimiter=';')# Чтение CSV файла с указанием разделителя ';'
        points = [] # Создание пустого списка для хранения объектов Point
        # Проход по каждой строке значений z
        for index, row in df.iloc[0:].iterrows():
            points.append(Point(row[offset+0], row[offset+1], row[offset+2]))
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
        def is_point_inside_polygon(x, y):
            """
            Проверяет, находится ли точка (x, y) внутри многоугольника.
            Алгоритм: метод лучевого преобразования (Ray Casting method).
            """
            n = len(self.points)
            inside = False

            px, py = x, y
            for i in range(n):
                x1, y1 = self.points[i].x, self.points[i].y
                x2, y2 = self.points[(i + 1) % n].x, self.points[(i + 1) % n].y
                if ((y1 > py) != (y2 > py)) and (px < (x2 - x1) * (py - y1) / (y2 - y1) + x1):
                    inside = not inside
            return inside

        for point in allpoints:
            if is_point_inside_polygon(point.x, point.y):
                return point.z

        return self.points[0].z
    
class HeightLevel:
    """
    Класс Level представляет уровень с высотой "от" и "до" и цветом RGB.

    Атрибуты:
    - height_from: высота начала диапазона
    - height_to: высота конца диапазона
    - color_rgb: кортеж с тремя значениями RGB в 16-ричной форме
    """

    def __init__(self, level_index, height_from, height_to, color_rgb):
        """
        Инициализирует объект Level с заданными высотами и цветом RGB.
        """
        self.level_index = level_index
        self.height_from = height_from
        self.height_to = height_to
        self.color_rgb = color_rgb

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

    def __init__(self, levels=[]):
        """
        Инициализирует объект Levels с заданным списком уровней.

        Аргументы:
        levels (list): Список уровней.
        """
        self.levels = levels[:] if levels is not None else [] #Этот тернарный оператор сделает копию списка levels или если не указано создаст пустой список
        self.corrected_levels = []
        self.intervals = []
    
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
        index = next((index for index, level in enumerate(levels) if level.height_from == round(value, 1)), None)
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
        index = next((index for index, level in enumerate(levels) if level.height_to == round(value, 1)), None)
        if index is not None:
            return index
        else:
            return None

    
    def define_contours_levels(self, bottom, top, step=1):
        """Определяет список отметок по заданному шагу."""
        # Создать список интервалов, начиная с bottom
        height_values = []
        current_height = bottom
        
        while current_height <= top:
            height_values.append(current_height)
            current_height += step
        print(height_values)       
        
        # Отфильтровать интервалы в пределах от bottom до top
        height_values = [height for height in height_values if bottom <= height <= top]
        print(height_values)
        # Если минимальная высота не входит в интервалы, добавляем её в начало
        if height_values[0] > bottom:
            height_values.insert(0, bottom)
        
        # Если максимальная высота не входит в интервалы, добавляем её в конец
        if height_values[-1] < top:
            height_values.append(top)
        self.levels = height_values
        return
    
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
        return corrected_levels
    
    def make_intervals(self):
        """Создает список интервалов между уровнями."""
        self.intervals = []
        for i in range(len(self.levels) - 1):
            interval = (self.levels[i], self.levels[i + 1], self.interpolate_color(self.levels[i]))
            self.intervals.append(interval)
        print (self.intervals)

    
    def interpolate_color(self, from_height):
        """Интерполяция градиента для изоконтуров"""
        # Нормализуем высоты к интервалу [0, 1]
        norm_from_height = (from_height - self.levels[0]) / (self.levels[-1] - self.levels[0])
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