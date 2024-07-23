class GeometryTools:
    """Класс для реализации преобразований линейной геометрии.

    Оборот полигона по часовой, сборка линий из нарезки и т.д.

    """
    def __init__(self):
        self.polygon = []

    
    def remove_close_points(self, polyline, threshold=1):
        """Убирает очень короткие ребра полилинии, всегда оставляя первую и последнюю точки"""

        new_polyline = [polyline[0]]  # Начнем с первой точки, так как ее мы не удаляем
        for i in range(1, len(polyline) - 1):
            # Вычисляем расстояние между текущей точкой и предыдущей
            distance = ((polyline[i].x - new_polyline[-1].x) ** 2 + (polyline[i].y - new_polyline[-1].y) ** 2) ** 0.5
            # Если расстояние больше или равно пороговому значению, добавляем текущую точку в новую полилинию
            if distance == 0:
                continue
            if distance >= threshold:
                new_polyline.append(polyline[i])
 
        # Добавляем последнюю точку
        new_polyline.append(polyline[-1])
        # Проверяем предпоследнюю и удаляем, если она слишком близко, но не если у нас всего две точки в линии
        if len(new_polyline) > 2:
            if ((polyline[-1].x - new_polyline[-2].x) ** 2 + (polyline[-1].y - new_polyline[-2].y) ** 2) ** 0.5 <= threshold:
                del new_polyline[-2]
        
        return new_polyline
    
    
    def ensure_clockwise (self):
        """Порядок вершин всегда по часовой стрелке"""

        points = self.polygon
        area = 0
        n = len(points)
        for i in range(n):
            j = (i + 1) % n  # Следующая точка, циклически возвращаемся к первой
            x1, y1 = points[i].x, points[i].y
            x2, y2 = points[j].x, points[j].y
            area += x1 * y2 - x2 * y1
        if area < 0:
            # Ориентация уже по часовой стрелке
            self.polygon = points
        else:
            # Инвертируем порядок, чтобы сделать по часовой стрелке
            self.polygon = points[::-1]
    
    #Собираем линии из кусочков
    def assemble_polygon_from_noodles(self, noodles):#noodles это список списков точек
        """Собирает лапшу (список списка точек) в одну полилинию

        Оставшуюся лапшу возвращает
        """
        # if len (noodles) == 1:
        #     polyline = noodles[0]
        #     return polyline, noodles
        k = 0 
        polyline = []  # Создаем список с точками
        polyline = noodles[0] # Добавляем первую макаронину
        noodles.remove(noodles[0])  # Удаляем из списка
        while (len(noodles) > 0) and (k < len(noodles)):
            next_noodle = noodles[k]
            if next_noodle[-1] == polyline[0]:  # КОНЕЦ куска это НАЧАЛО полилинии
                polyline = next_noodle[:-1] + polyline  # Добавляем точки кроме последней в начало полилинии
                noodles.remove(noodles[k])
                k=0
                continue
            if next_noodle[0] == polyline[0]:  # НАЧАЛО куска это НАЧАЛО полилинии
                inverted_next_noodle = next_noodle[::-1] # Оборачиваем кусок
                polyline = inverted_next_noodle [:-1] + polyline  # Добавляем точки кроме последней в начало полилинии
                noodles.remove(noodles[k])
                k=0
                continue
            if next_noodle[0] == polyline[-1]:  # НАЧАЛО куска это КОНЕЦ полилинии 
                polyline = polyline + next_noodle[1:]# Добавляем точки кроме первой в конец полилинии
                noodles.remove(noodles[k])
                k=0
                continue
            if next_noodle[-1] == polyline[-1]:  # КОНЕЦ куска это КОНЕЦ полилинии
                inverted_next_noodle = next_noodle[::-1] # Оборачиваем кусок
                polyline = polyline + inverted_next_noodle[1:]# Добавляем точки кроме первой в конец полилинии
                noodles.remove(noodles[k])
                k=0
                continue
            if polyline[-1] == polyline[0]:
                k=0
                break
            k += 1

        self.polygon =  polyline
        return polyline, noodles



    def cubic_hermite_spline(self, P, num_points = 10, tau=0.5):
        """Кубический сплайн Хермита"""
        
        def distance_between_points(p1, p2):
            """Расстояние между точками"""
            dx = p2.x - p1.x
            dy = p2.y - p1.y
            return (dx ** 2 + dy ** 2) ** 0.5
        
        
        def tau_correction(p1,p2,p3,p4, tau=0):
            """Коррекция натяжение на участках, где управляющие отрезки значительно длиннее итерируемого"""
            l1 = distance_between_points(p1,p2)
            l2 = distance_between_points(p2,p3)
            l3 = distance_between_points(p3,p4)
            if l1 == 0 and l3 ==0: # Случай, если изолиния из одного сегмента?
                tau_corr = 0
            else:
                if l1==0:
                    tau_corr = l2/l3
                elif l3 == 0:
                    tau_corr = l2/l1
                else:
                    tau_corr = min (l2/l1 , l2/l3)
                
            if tau_corr < 1:
                tau*=tau_corr
            return tau

        def cubic_hermite(height, p0, p1, p2, p3, num_points, tau):
            """Создать точки к среднему сегменту в квадруплексе"""
            from pyTIN_library.triangulation_classes import Point
            
            points = []
            
            for i in range(num_points):
                t = i / float(num_points - 1)
                t2 = t * t
                t3 = t2 * t

                # Cubic Hermite spline equation
                h00 = 2*t3 - 3*t2 + 1
                h10 = t3 - 2*t2 + t
                h01 = -2*t3 + 3*t2
                h11 = t3 - t2

                x = h00 * p1.x + h10 * ((p2.x - p0.x) * tau) + h01 * p2.x + h11 * ((p3.x - p1.x) * tau)
                y = h00 * p1.y + h10 * ((p2.y - p0.y) * tau) + h01 * p2.y + h11 * ((p3.y - p1.y) * tau)

                points.append(Point(x, y, height))

            return points
        
        # Создание сплайна
        height = P[0].z
        spline_points = []
        if len(P) < 3:
            return P
        if P[0] == P[-1]: #Для замкнутого контура
            del P[-1]
            P = [P[-2]] + [P[-1]] + P + [P[0]] #Добавим точки для оборачивания угла
            for i in range (0, len(P)-3):
                spline_points.extend(cubic_hermite(height, P[i], P[i+1], P[i+2], P[i+3], num_points, tau_correction(P[i], P[i+1], P[i+2], P[i+3], tau)))
            spline_points = spline_points + [spline_points[0]]
        else:#Для незамкнутой линии
            P = [P[0]] + P + [P[-1]] #Продублируем точки в начале и конце
            for i in range (0, len(P)-3):
                spline_points.extend(cubic_hermite(height, P[i], P[i+1], P[i+2], P[i+3], num_points, tau_correction(P[i], P[i+1], P[i+2], P[i+3], tau)))

        return spline_points

    @staticmethod
    def do_lines_intersect(p1, q1, p2, q2):
        """
        Проверяет, пересекаются ли два отрезка [p1, q1] и [p2, q2].

        :param p1: Начальная точка первого отрезка.
        :param q1: Конечная точка первого отрезка.
        :param p2: Начальная точка второго отрезка.
        :param q2: Конечная точка второго отрезка.
        :return: True, если отрезки пересекаются, иначе False.
        """
        def orientation(p, q, r):
            val = (q.y - p.y) * (r.x - q.x) - (q.x - p.x) * (r.y - q.y)
            if val == 0:
                return 0  # Коллинеарные
            return 1 if val > 0 else 2  # Clockwise или Counterclockwise

        def on_segment(p, q, r):
            # Проверяет, лежит ли точка q на отрезке pr
            return min(p.x, r.x) <= q.x <= max(p.x, r.x) and min(p.y, r.y) <= q.y <= max(p.y, r.y)

        o1 = orientation(p1, q1, p2)
        o2 = orientation(p1, q1, q2)
        o3 = orientation(p2, q2, p1)
        o4 = orientation(p2, q2, q1)



        # Специальные случаи: проверяем коллинеарность и принадлежность точки отрезку
        if o1 == 0 and on_segment(p1, p2, q1):
            return False  # Смежные, но не пересекающиеся

        if o2 == 0 and on_segment(p1, q2, q1):
            return False  # Смежные, но не пересекающиеся

        if o3 == 0 and on_segment(p2, p1, q2):
            return False  # Смежные, но не пересекающиеся

        if o4 == 0 and on_segment(p2, q1, q2):
            return False  # Смежные, но не пересекающиеся
        
        # Основной случай: если пары точек имеют разные ориентации, то они пересекаются
        if o1 != o2 and o3 != o4:
            return True

        return False  # Отрезки не пересекаются и не смежные
    
    @staticmethod
    def calculate_intersection(p1, p2, p3, p4):
        """
        Вычисляет точку пересечения двух отрезков.

        :param p1: Начальная точка первого отрезка, объект Point.
        :param p2: Конечная точка первого отрезка, объект Point.
        :param p3: Начальная точка второго отрезка, объект Point.
        :param p4: Конечная точка второго отрезка, объект Point.
        :return: Точка пересечения отрезков, объект Point, или None, если отрезки не пересекаются.
        """
        from pyTIN_library.triangulation_classes import Point

        x1, y1 = p1.x, p1.y
        x2, y2 = p2.x, p2.y
        x3, y3 = p3.x, p3.y
        x4, y4 = p4.x, p4.y

        denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)

        if denominator == 0:
            return None  # Отрезки параллельны или совпадают

        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denominator
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denominator

        if 0 <= t <= 1 and 0 <= u <= 1:
            intersection_x = x1 + t * (x2 - x1)
            intersection_y = y1 + t * (y2 - y1)
            intersection_z = p1.z + t * (p2.z - p1.z)
            return Point(intersection_x, intersection_y, intersection_z)
        else:
            return None  # Отрезки не пересекаются