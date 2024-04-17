from typing import List
from triangulation_classes import Triangle
from triangulation_classes import Edge
from triangulation_classes import Point
from triangulation_classes import IsoLine
from geometrytools import GeometryTools
import copy

class Triangulation: 
    """ Это главный класс поверхности на основе триангуляции Делоне"""
    EPS = 1e-7 #величина для округления
    def __init__(self):
        self.triangles = []
        self.bounds = []
        self.custom_bounds = []
        self.contour_lines = []
        self.sm_contour_lines = []
        self.isocontours = []
        self.points = []
        self.levels = []

    def add_triangle(self, triangle):
        self.triangles.append(triangle)

    def remove_triangle(self, triangle):
        self.triangles.remove(triangle)

    def clear_triangles(self):
        self.triangles = []

    ###########################################
    #   Методы для построения триангуляции    #        
    ###########################################    
    
    
    def triangulate(self, points):
        """Функция, находящая триангуляцию"""
        self.points = points
        n = len(points)
        if n < 3:
            return []  # Треугольников нет

        #Работаем с копией массива точек, сортируем по X
        points_copy = sorted(points, key=lambda p: p.x)
        
        #Ищем большой треугольник
        big = self.make_big_triangle(points)
        
        #Добавим точки супертреугольника в список точек
        points_copy+= big
        
        #Делаем текущим супертреугольник и добавим в массив
        # Создаем ребра из этих точек
        edges = [Edge(points_copy[n], points_copy[n+1]), Edge(points_copy[n], points_copy[n+2]),\
                Edge(points_copy[n+1], points_copy[n+2])]
        # Создаем треугольник из этих ребер и в список
        cur_triangles = [Triangle(*edges)]

        badEdges = [] #Ребра улалённых треугольников 
        edges = []
        #Перебираем все точки с конца кроме точек супертреугольника
        for i in range(n-1, -1, -1):
            #Перебираем все треугольники
            j = len(cur_triangles) - 1
            while j >= 0:
                # Если точка лежит в окружности этого треугольника, то добавляе его в плохие треугольники
                dx = points_copy[i].x - cur_triangles[j].circumcenter()[0]
                dy = points_copy[i].y - cur_triangles[j].circumcenter()[1]
                r2 = cur_triangles[j].circumradius()

                #Если точка справа от окружности, то треугольник проверять больше не нужно 
                #точки отсортированы и поэтому тоже будут справа?
                if (dx > 0) and (dx*dx > r2):
                    j-=1
                    continue
                #если точка вне окружности, то треугольник изменять не нужно
                inout = (dx*dx + dy*dy - r2)
                if inout > self.EPS:
                    j-=1
                    continue
                
                if inout < self.EPS:
                    curTriangle = cur_triangles.pop(j)
                    #добавляем его стороны в список ребер
                    badEdges.extend(curTriangle.edges)
                    j-=1
            
            #Идём с конца, поэтому проблем с индексами быть не должно
            # удаляем кратные ребра
            unique_edges = self.delete_multiples_edges(badEdges)
            
            # создаем новые треугольники последовательно по списку ребер
            k = len( unique_edges) - 1
            while k >= 0:
            # ваш код здесь
                new_edges = [unique_edges[k] ,\
                        Edge(unique_edges[k].start, points_copy[i]),\
                        Edge(unique_edges[k].end, points_copy[i])]
                #cur_triangles+=Triangle(*edges)
                cur_triangles.append(Triangle(*new_edges))
                k-=1 
            badEdges = []
            #plot_triangulation(cur_triangles, points_copy)
            
        #Теперь удалим треугольники от точек супертреугольника
        t = len(cur_triangles) - 1
        while t >= 0:
            for edge in cur_triangles[t].edges:
                if edge.start in big or edge.end in big:
                    cur_triangles.remove(cur_triangles[t])
                    break
                break
            t -= 1
        self.triangles = cur_triangles
        self.get_bounds() #Сразу вставим границы текущей триангуляции
    
    def get_bounds(self):
        """Граница треугольников помещается в атрибут bounds"""
        edges = []
        for triangle in self.triangles:
            for edge in triangle.edges:
                edges.append(edge)
        #Удаляем кратные ребра
        contour_edges = self.delete_multiples_edges(edges)
        #Преобразуем список непарных ребер в список пар точек
        point_pairs = [[edge.start, edge.end] for edge in contour_edges]
        #Обратимся к менеджеру полигонов, дав ему пока пустое значение
        pmanager = GeometryTools()
        #Собираем контур границы из кусочков, при этом точки собранной линии или полигона
        #попадают в атрибут .polygon
        pmanager.assemble_polygon_from_noodles(point_pairs)
        pmanager.ensure_clockwise() #Сортируем по часовой стрелке
        self.bounds = pmanager.polygon #Получаем точки границы триангуляции

    
    #Функция, удаляющая кратные ребра
    def delete_multiples_edges (self, edges):
        """Удаляем кратные ребра."""
        contour_edges = []
        for edge in edges:
            count = 0
            for other_edge in edges:
                if edge == other_edge:
                    count += 1
            if count == 1:
                contour_edges.append(edge)
            count = 0
        return contour_edges

    def make_big_triangle(self, points):
        """Создаём большой треугольник, включающий все точки набора  """
        minx = min(p.x for p in points)
        maxx = max(p.x for p in points)
        miny = min(p.y for p in points)
        maxy = max(p.y for p in points)
        dx = maxx - minx
        dy = maxy - miny
        dxy = max(dx, dy)
        midx = dx * 0.5 + minx
        midy = dy * 0.5 + miny
        return [
            Point(midx - 10 * dxy, midy - 10 * dxy, 0),
            Point(midx, midy + 10 * dxy, 0),
            Point(midx + 10 * dxy, midy - 10 * dxy, 0)
        ]

    
    def filter_triangles(self, max_lenght, min_angle):
        """Удалить из триангуляции треугольники не соответствующие критериям
        
        по минимальному углу и длине ребра"""

        if self.triangles == []:
            return []
        filtered_triangles = []
        for triangle in self.triangles:
            if (triangle.max_edge() < max_lenght) and (triangle.min_angle() > min_angle):
                filtered_triangles.append(triangle)
        self.triangles = filtered_triangles


    ###########################################
    #      Методы для построения изолиний     #        
    ###########################################

    def find_intersection(self, edge, h):
        """
        Находит точку пересечения ребра с плоскостью заданной высоты.
        :param edge: объект Edge
        :param h: высота плоскости
        :return: кортеж (x, y) координат точки пересечения или None, если ребро полностью лежит в плоскости
        """
        x1, y1, z1 = edge.start.x, edge.start.y, edge.start.z
        x2, y2, z2 = edge.end.x, edge.end.y, edge.end.z
        dz = z2 - z1
        # Если разность высот равна 0, значит высота точки равна z1 или z2
        if dz == 0:
            return None
            #return [(x1 + x2) / 2, (y1 + y2) / 2, z1]
        z_max = max (z1,z2)
        z_min = min (z1,z2)
        if not z_min < h < z_max:
            return None
        # Пропорциональное соотношение для нахождения расстояния от начальной точки до искомой точки
        t = (h - z1) / dz
        # Находим координаты искомой точки
        x = x1 + t * (x2 - x1)
        y = y1 + t * (y2 - y1)
        return Point(x, y, h)

    
    def define_contours_levels(self, start=0, step=1):
        """Определяет список отметок по заданному шагу."""
        if not self.points:
            return []

        min_height = min(point.z for point in self.points)
        max_height = max(point.z for point in self.points)

        # Вычисляем первый уровень внутри диапазона, начиная от start
        # Настройка начального уровня на ближайший возможный в пределах высот
        start = min(min_height, start)
        if start > max_height:
            return []  # Если начальное значение выше максимума, возвращаем пустой список

        # Генерация уровней высоты
        height_values = []
        current_height = start
        eps = 0.01  # Малая величина для коррекции высоты изолиний
        if not self.levels:
            while current_height <= max_height:
                corrected_height = current_height
                # Проверяем и корректируем высоту, чтобы избежать точного совпадения с высотами точек
                while any(abs(point.z - corrected_height) < eps for point in self.points):
                    corrected_height -= eps
                height_values.append(corrected_height)
                current_height += step
        else:
            for current_height in self.levels:
                corrected_height = current_height
                # Проверяем и корректируем высоту, чтобы избежать точного совпадения с высотами точек
                while any(abs(point.z - corrected_height) < eps for point in self.points):
                    corrected_height -= eps
                height_values.append(corrected_height)
        self.levels = height_values
        
        return


    def build_contour_lines (self):
        """Построение изолиний"""
        
        def trace_contour_line(height: float):
            """Трассируем изолинии. Просто итерируются все треугольники и по ним строятся отдельные ребра изолиний"""
            contour_edges = []
            for triangle in self.triangles:
                #Находим точки изолинии в треугольнике
                edge_points = []
                for edge in triangle.edges:
                    contour_point = self.find_intersection(edge, height)
                    if contour_point:
                        edge_points.append(contour_point)
                if edge_points:
                    contour_edges.append(edge_points)
            return contour_edges        
        
        heights = self.levels

        print (self.levels)

        contour_lines = []

        gutils = GeometryTools()

        for height in heights:
            contour_edges = trace_contour_line(height)
            if contour_edges:
                while contour_edges:
                    contour_line = IsoLine(height=round(height,1))
                    #Собрать изолинию из лапши
                    assembled_edges, contour_edges = gutils.assemble_polygon_from_noodles(contour_edges)
                    contour_line.points = assembled_edges 
                    contour_lines.append(contour_line)

        self.contour_lines = contour_lines

        return

    def cull_contour_lines (self, threshold=0.1):
        """Прореживает полилинии.
        
        Помогает уменьшить каракули возле отметок, когда их высота близка к уровню изолинии """
        cull_contour_lines = []
        gutils = GeometryTools()
        for contour_line in self.contour_lines:
            contour_line.points = gutils.remove_close_points(contour_line.points, threshold)
            cull_contour_lines.append(contour_line)
        self.contour_lines = cull_contour_lines
        return
    
    def smooth_contour_lines (self, nPoints, alpha):
        """Сгладить полилинию"""
        smooth_contour_lines = []
        gutils = GeometryTools()
        for contour_line in self.contour_lines:
            points = copy.copy(contour_line.points)
            smooth_contour_line = IsoLine(height=contour_line.height)         
            smooth_contour_line.points = gutils.cubic_hermite_spline(points, nPoints, alpha)
            smooth_contour_lines.append(smooth_contour_line)
        self.sm_contour_lines = smooth_contour_lines

    def insert_custom_bounds (self):
        """Добавить свой внешний полигон.
        Вершинам присвоятся значения соседних отметок, после чего они войдут в исходный набор """
        def distance_between_points(p1, p2):
            """Calculate the distance between two points."""
            dx = p2.x - p1.x
            dy = p2.y - p1.y
            return (dx ** 2 + dy ** 2) ** 0.5
        
        for point in self.custom_bounds:
            distances = [distance_between_points(p, point) for p in self.points]
            min_distance = min(distances)
            closest_point_index = distances.index(min_distance)
            point.z = self.points[closest_point_index].z
        self.points.extend(self.custom_bounds)
       
        return