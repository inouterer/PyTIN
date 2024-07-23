from pyTIN_library.triangulation_classes import Triangle
from pyTIN_library.triangulation_classes import Edge
from pyTIN_library.triangulation_classes import Point
from pyTIN_library.triangulation_classes import IsoLine
from pyTIN_library.geometrytools import GeometryTools
import copy

class Triangulation: 
    """
    Это главный класс поверхности на основе триангуляции Делоне
    
    Attributes:
        triangles (list): список треугольников, образующих триангуляцию
        bounds (list): границы поверхности
        custom_bounds (list): пользовательские границы
        contour_lines (list): линии контуров
        sm_contour_lines (list): малые линии контуров
        isocontours (list): изолинии
        points (list): точки, используемые для триангуляции
        levels (list): уровни поверхности
    """
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
    
    ###########################################
    #   Методы для построения триангуляции    #        
    ###########################################
    
    def triangulate(self, points):
        """
        Функция, находящая триангуляцию Делоне для заданного набора точек методом Бовьера-Ваттсона.
        
        Args:
            points (list): Список точек для триангуляции.
        
        Returns:
            list: Список треугольников, формирующих триангуляцию.
        """
        self.points = points
        n = len(points)
        if n < 3:
            return []  # Треугольников нет

        #Работаем с копией массива точек, сортируем по X, что является оптимизацией
        points_copy = sorted(points, key=lambda p: p.x)
        
        #Ищем большой треугольник
        big = self.make_big_triangle(points)
        
        #Добавим точки супертреугольника в список точек
        points_copy+= big
        
        #Делаем текущим супертреугольник и добавим в массив
        #Создаем ребра из этих точек
        edges = [Edge(points_copy[n], points_copy[n+1]), Edge(points_copy[n], points_copy[n+2]),\
                Edge(points_copy[n+1], points_copy[n+2])]
        # Создаем треугольник из этих ребер и в список
        cur_triangles = [Triangle(*edges)]

        badEdges = [] #Ребра удалённых треугольников 
        edges = [] #Обнуляем массив ребер
        
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
            
        #Теперь удалим треугольники от точек супертреугольника
        t = len(cur_triangles) - 1
        while t >= 0:
            for edge in cur_triangles[t].edges:
                if edge.start in big or edge.end in big:
                    cur_triangles.remove(cur_triangles[t])
                    break
                break
            t -= 1
        self.triangles = cur_triangles #Сразу вставим границы текущей триангуляции
        #self.get_bounds() #А можно и вычислить границы
        print(f'Num of triangles in triangulation: {len(cur_triangles)}')
        
    
    def is_triangle_boundary(self, triangle):
        """
        Проверяет, является ли треугольник граничным в триангуляции.

        :param triangle: Треугольник, объект класса Triangle.
        :return: True, если треугольник граничный, False в противном случае.
        
        """
        edges_count = 0
        for other_triangle in self.triangles:
            if other_triangle != triangle:
                common_edges = set(triangle.edges) & set(other_triangle.edges)
                edges_count += len(common_edges)

        # Треугольник считается граничным, если у него меньше трех общих ребер с другими треугольниками
        return edges_count < 3
    
    def get_bounds(self):
        
        """
        Определяет границы триангуляции и сохраняет их в атрибут bounds. Это потребуется при обработке изоконтуров
        
        """
        edges = []
        for triangle in self.triangles:
            for edge in triangle.edges:
                edges.append(edge)
        copy_edges = edges.copy()#Работаем с копией
        print(f'Num of edges to get bounds of triangulation: {len(copy_edges)}')
        #Удаляем кратные ребра
        contour_edges = self.delete_multiples_edges(copy_edges)
        #Преобразуем список непарных ребер в список пар точек
        point_pairs = [[edge.start, edge.end] for edge in contour_edges]
        #Обратимся к менеджеру полигонов, дав ему пока пустое значение
        pmanager = GeometryTools()
        #Собираем контур границы из кусочков, при этом точки собранной линии или полигона
        #попадают в атрибут .polygon
        pmanager.assemble_polygon_from_noodles(point_pairs)
        pmanager.ensure_clockwise() #Сортируем по часовой стрелке
        self.bounds = pmanager.polygon #Получаем точки границы триангуляции

    
    def delete_multiples_edges (self, copy_edges):
        """
        
        Функция, удаляющая кратные ребра (оптимизированная функция).
        
        """
        e = len(copy_edges) #Создаём копию списка
        #Итерируем с конца списка
        while e>0:
            e-=1
            g = e 
            while g>0:
                g-=1
                if copy_edges[e] == copy_edges[g]:
                    del copy_edges[e]
                    del copy_edges[g]
                    e-=1 # После удаления уменьшаем индекс два раза на 1 (здесь и в начале цикла)
                    break    
        return copy_edges


    def make_big_triangle(self, points):
        """
        
        Создаём большой треугольник, включающий все точки набора
        
        """
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

    
    def filter_triangles(self, min_angle):
        """
        
        Удалить из триангуляции треугольники не соответствующие критериям
        по минимальному углу и длине ребра. НЕДОРЕАЛИЗОВАНО
        
        """
        if self.triangles == []:
            return []
        filtered_triangles = []
        for triangle in self.triangles:
            if (triangle.min_angle() < min_angle) and self.is_triangle_boundary(triangle):
                print (triangle.min_angle())
                continue
            else:
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


    def build_contour_lines (self):
        """
        
        Построение изолиний
        
        """
        
        def trace_contour_line(height: float):
            """
            Трассируем изолинии.
            Просто итерируются все треугольники и по ним строятся отдельные ребра изолиний
            
            """
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
        
        Помогает уменьшить каракули возле отметок, когда их высота близка к уровню изолинии 
        
        """
        cull_contour_lines = []
        gutils = GeometryTools()
        for contour_line in self.contour_lines:
            contour_line.points = gutils.remove_close_points(contour_line.points, threshold)
            cull_contour_lines.append(contour_line)
        self.contour_lines = cull_contour_lines
        return
    
    def smooth_contour_lines (self, nPoints=10, alpha=0.5):
        """
        
        Сгладить полилинию
        
        """
        smooth_contour_lines = []
        g_tools = GeometryTools()
        for contour_line in self.contour_lines:
            points = copy.copy(contour_line.points)
            smooth_contour_line = IsoLine(height=contour_line.height)         
            smooth_contour_line.points = g_tools.cubic_hermite_spline(points, nPoints, alpha)
            smooth_contour_lines.append(smooth_contour_line)
        self.sm_contour_lines = smooth_contour_lines

    def insert_custom_bound_points2 (self):
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
    
    def insert_custom_bound_points (self):
        """Добавить свой внешний полигон.
        Вершинам присвоятся значения соседних отметок, после чего они войдут в исходный набор """
        def distance_between_points(p1, p2):
            """Calculate the distance between two points."""
            dx = p2.x - p1.x
            dy = p2.y - p1.y
            return (dx ** 2 + dy ** 2) ** 0.5
        #Сначала присвоим всем точкам пользовательских границ отметки ближайших точек
        for point in self.custom_bounds:
            distances = [distance_between_points(p, point) for p in self.points]
            min_distance = min(distances)
            closest_point_index = distances.index(min_distance)
            point.z = self.points[closest_point_index].z
        # #Теперь проверим, не попадают ли точки на треугольники и интерполируем с них высоту - отклонено
        # for bound_point in self.custom_bounds:
        #     for triangle in self.triangles:
        #         if triangle.is_inside_triangle(bound_point):
        #             bound_point.z = triangle.interpolate_z(bound_point)
        self.points.extend(self.custom_bounds) #Добавим точки в границы
        self.triangulate(self.points)
        #В финале проверим отрезки границ, проходят ли они через треугольники.
        #Если да то добавим в центре пересечения точки с отметками
        n= len(self.custom_bounds)
        tri_points = []
        for ind in range(n):
            p1 = self.custom_bounds[ind]
            p2 = self.custom_bounds[(ind + 1) % n]  # использование операции модуля для циклического обхода списка вершин
            for triangle in self.triangles:
                addpoint = triangle.get_point_by_line(p1, p2)
                if isinstance(addpoint, Point):  # Проверка, является ли элемент точкой
                        tri_points.append(addpoint)
                        #print(f'{addpoint.x} {addpoint.y} {addpoint.z}')
        self.points.extend(tri_points)
        self.points = list(set(self.points)) #Прекрасный способ избавиться от дубликатов - преобразовать во множество и обратно в список
        self.triangulate(self.points)
        self.remove_outer_triangles()
        self.get_bounds()
        return
    
    def remove_outer_triangles(self):
        """
        Удаляет из сети треугольники за границами пользователя по центроиду
        """
        def is_inside_polygon(point, polygon):
            """
            Проверяет, находится ли точка внутри полигона.

            :param point: Точка, представленная объектом класса Point.
            :param polygon: Список вершин полигона, представленных в виде объектов Point.
            :return: True, если точка внутри полигона, и False в противном случае.
            """
            n = len(polygon)
            intersections = 0

            for i in range(n):
                p1 = polygon[i]
                p2 = polygon[(i + 1) % n]
                if ((p1.y <= point.y and p2.y > point.y) or
                    (p1.y > point.y and p2.y <= point.y)) and \
                        point.x < (p2.x - p1.x) * (point.y - p1.y) / (p2.y - p1.y) + p1.x:
                    intersections += 1

            return intersections % 2 == 1

        inner_triangles = []
        for triangle in self.triangles:
            centroid = triangle.triangle_centroid()
            if is_inside_polygon(centroid, self.custom_bounds):
                inner_triangles.append(triangle)
        self.triangles = inner_triangles



