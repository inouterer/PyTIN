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


def CatmullRomChain(P, nPoints, alpha):
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

import matplotlib.pyplot as plt

# Создание объектов Point из класса для набора точек
points = [
    Point(-0.72, -0.3, 0),
    Point(0, 0, 0),
    Point(1., 0.8, 0),
    Point(1.1, 0.5, 0),
    Point(2.7, 1.2, 0),
    Point(3.4, 0.27, 0),
    Point(-0.72, -0.3, 0)
]

# Запуск алгоритма Catmull-Rom с указанием параметра alpha
nPoints = 10
alpha = 0.5
curve_points = CatmullRomChain(points, nPoints, alpha)

# Извлечение координат x и y из точек
x_curve = [p.x for p in curve_points]
y_curve = [p.y for p in curve_points]

print(curve_points)
x_points = [p.x for p in points]
y_points = [p.y for p in points]

# Визуализация
plt.figure(figsize=(9, 6))
plt.plot(x_curve, y_curve, 'r-', label='Catmull-Rom Curve')
plt.plot(x_points, y_points, 'bo', label='Interpolatory Points')
plt.legend()
plt.title('Catmull-Rom Curve with Interpolatory Points')
plt.xlabel('X')
plt.ylabel('Y')
plt.grid(True)
plt.show()
