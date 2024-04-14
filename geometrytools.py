from triangulation_classes import Point

class GeometryTools:
    """Класс для реализации преобразований линейной геометриии.

    Оборот полигона по часовой, сборка линий из нарезки и т.д.

    """
    def __init__(self):
        self.polygon = []

    
    def remove_close_points(self, polyline, threshold=1):
        """Убирает очень короткие ребра полилинии, всегда осталяя первую и последнюю точки"""
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
        # Проверяем предпоследнюю и удаляем, если она слишком близко
        if ((polyline[-1].x - new_polyline[-2].x) ** 2 + (polyline[-1].y - new_polyline[-2].y) ** 2) ** 0.5 <= threshold:
            del new_polyline[-2]
        return new_polyline
    
    # Порядок вершин всегда по часовой
    def ensure_clockwise (self):
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
        !!! Оставшуюся лапшу возвращает !!!
        """
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

    

    def CatmullRomChain(self, P, nPoints, alpha):
        """Barry and Goldman's pyramidal formulation  Centripetal Catmull–Rom spline

        Args:
            P (list): List of Point objects representing control points.
            nPoints (int): Number of points to generate on the curve.
            alpha (float): Tension parameter.

        Returns:
            list: List of Point objects representing points on the Catmull-Rom spline.
        """

        def pyramidalFormulation(P0, P1, P2, P3, nPoints, alpha):
            def knotParameters(ti, Pi, Pj):
                xi, yi, zi = Pi.x, Pi.y, Pi.z
                xj, yj, zj = Pj.x, Pj.y, Pj.z
                return ((xj - xi) ** 2 + (yj - yi) ** 2 + (zj - zi) ** 2) ** (alpha / 2) + ti

            t0 = 0
            t1 = knotParameters(t0, P0, P1)
            t2 = knotParameters(t1, P1, P2)
            t3 = knotParameters(t2, P2, P3)

            t = [t1 + (t2 - t1) * i / nPoints for i in range(nPoints)]

            A1_x = [(t1 - t_val) / (t1 - t0) * P0.x + (t_val - t0) / (t1 - t0) * P1.x for t_val in t]
            A1_y = [(t1 - t_val) / (t1 - t0) * P0.y + (t_val - t0) / (t1 - t0) * P1.y for t_val in t]

            A2_x = [(t2 - t_val) / (t2 - t1) * P1.x + (t_val - t1) / (t2 - t1) * P2.x for t_val in t]
            A2_y = [(t2 - t_val) / (t2 - t1) * P1.y + (t_val - t1) / (t2 - t1) * P2.y for t_val in t]

            A3_x = [(t3 - t_val) / (t3 - t2) * P2.x + (t_val - t2) / (t3 - t2) * P3.x for t_val in t]
            A3_y = [(t3 - t_val) / (t3 - t2) * P2.y + (t_val - t2) / (t3 - t2) * P3.y for t_val in t]

            B1_x = [(t2 - t_val) / (t2 - t0) * A1_x[i] + (t_val - t0) / (t2 - t0) * A2_x[i] for i, t_val in enumerate(t)]
            B1_y = [(t2 - t_val) / (t2 - t0) * A1_y[i] + (t_val - t0) / (t2 - t0) * A2_y[i] for i, t_val in enumerate(t)]

            B2_x = [(t3 - t_val) / (t3 - t1) * A2_x[i] + (t_val - t1) / (t3 - t1) * A3_x[i] for i, t_val in enumerate(t)]
            B2_y = [(t3 - t_val) / (t3 - t1) * A2_y[i] + (t_val - t1) / (t3 - t1) * A3_y[i] for i, t_val in enumerate(t)]

            C_x = [(t2 - t_val) / (t2 - t1) * B1_x[i] + (t_val - t1) / (t2 - t1) * B2_x[i] for i, t_val in enumerate(t)]
            C_y = [(t2 - t_val) / (t2 - t1) * B1_y[i] + (t_val - t1) / (t2 - t1) * B2_y[i] for i, t_val in enumerate(t)]

            return [Point(C_x[i], C_y[i], 0) for i in range(len(t))]

        length = len(P)
        Curve = []
        length = len(P)
        Curve = []
        if len(P) < 4:
            return P
        
        
        if P[0] == P[-1]:  # If the curve is closed
            c = pyramidalFormulation(P[0], P[1], P[2], P[3], nPoints, alpha)
            for i in range(length - 3):
                c = pyramidalFormulation(P[i], P[i + 1], P[i + 2], P[i + 3], nPoints, alpha)
                Curve.extend(c)
            last = pyramidalFormulation(P[-3], P[-2], P[-1], P[1], nPoints, alpha)
            first = pyramidalFormulation(P[-2], P[0], P[1], P[2], nPoints, alpha)
            Curve = Curve + [P[-2]] + last[1:] + [P[0]] + first [1:] + [P[1]] # Здесь пришлось собирать
        else:  # If the curve is not closed
            for i in range(length - 3):
                c = pyramidalFormulation(P[i], P[i + 1], P[i + 2], P[i + 3], nPoints, alpha)
                Curve.extend(c)
            Curve = [P[0]] + Curve + [P[-1]] # Добавим первый и последний отрезок кривой

        return Curve


        
    def catmull_rom_spline(self, control_points, num_points = 10, tau=0.5):
        """Генерирует точки Catmull-Rom сплайна для замкнутои незамкнутой полилинии.
        
        У замкнутой последняя точка должна равняться первой"""

        def catmull_rom_matrix(height, p0, p1, p2, p3, num_points = 10, tau=0.5):
            """Генерирует точки Catmull-Rom сплайна для одного сегмента (нужна полилиния из 4 точек)."""
            # Матрица коэффициентов Catmull-Rom
            m = [
                [-tau, 2-tau, tau-2, tau],
                [2*tau, tau-3, 3-2*tau, -tau],
                [-tau, 0, tau, 0],
                [0, 1, 0, 0]
            ]
            
            points = []
            for i in range(num_points):
                t = i / float(num_points - 1)
                t2 = t * t
                t3 = t2 * t
                
                # Вектор времени
                t_vector = [t3, t2, t, 1]
                
                # Вычисление координат x и y с помощью матричного умножения
                x = (t_vector[0]*m[0][0] + t_vector[1]*m[1][0] + t_vector[2]*m[2][0] + t_vector[3]*m[3][0]) * p0.x \
                    + (t_vector[0]*m[0][1] + t_vector[1]*m[1][1] + t_vector[2]*m[2][1] + t_vector[3]*m[3][1]) * p1.x \
                    + (t_vector[0]*m[0][2] + t_vector[1]*m[1][2] + t_vector[2]*m[2][2] + t_vector[3]*m[3][2]) * p2.x \
                    + (t_vector[0]*m[0][3] + t_vector[1]*m[1][3] + t_vector[2]*m[2][3] + t_vector[3]*m[3][3]) * p3.x
                    
                y = (t_vector[0]*m[0][0] + t_vector[1]*m[1][0] + t_vector[2]*m[2][0] + t_vector[3]*m[3][0]) * p0.y \
                    + (t_vector[0]*m[0][1] + t_vector[1]*m[1][1] + t_vector[2]*m[2][1] + t_vector[3]*m[3][1]) * p1.y \
                    + (t_vector[0]*m[0][2] + t_vector[1]*m[1][2] + t_vector[2]*m[2][2] + t_vector[3]*m[3][2]) * p2.y \
                    + (t_vector[0]*m[0][3] + t_vector[1]*m[1][3] + t_vector[2]*m[2][3] + t_vector[3]*m[3][3]) * p3.y
                    
                points.append(Point(x, y, height))
            
            return points
  
        # Создание сплайна
        height = control_points[0].z
        spline_points = []
        if control_points[0] == control_points[-1]:
            del control_points[-1]
            control_points = [control_points[-2]] + [control_points[-1]] + control_points + [control_points[0]]
            for i in range (0, len(control_points)-3):
                spline_points.extend(catmull_rom_matrix(height, control_points[i], control_points[i+1], control_points[i+2], control_points[i+3], num_points, tau))
            spline_points = spline_points + [spline_points[0]]
        else:
            control_points = [control_points[0]] + control_points + [control_points[-1]]
            for i in range (0, len(control_points)-3):
                spline_points.extend(catmull_rom_matrix(height, control_points[i], control_points[i+1], control_points[i+2], control_points[i+3], num_points, tau))

        return spline_points

