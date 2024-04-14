import math


class Point:
    """
    Точки с отметкой высоты
    """
    
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.marked = False
    def __ne__(self, other):
        # Перегрузка оператора неравенства (!=)
        return (self.x != other.x) or (self.y != other.y)
    def __eq__(self, other):
        # Перегрузка оператора неравенства (!=)
        return (self.x == other.x) and (self.y == other.y)


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


class Isocontour:
    """Изоконтуры"""
    def __init__(self, from_height, to_height):
        self.from_height = from_height
        self.to_height = to_height
        self.points = []
    def add_points(self, points):
        self.points.extend(points)

    def get_contour_points (self):
        return self.points

    def clear_contour_points(self):
        self.points = []