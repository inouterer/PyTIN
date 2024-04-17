import numpy as np
import matplotlib.pyplot as plt

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
        tolerance = 0.001
        return  (abs(self.x - other.x) > tolerance and
                 abs(self.y - other.y) > tolerance)
    
    def __eq__(self, other):
        # Перегрузка оператора равенства (==)
        tolerance = 0.001
        return  (abs(self.x - other.x) <= tolerance and
                 abs(self.y - other.y) <= tolerance)

def cubic_hermite_spline(x, y, m):
    """
    Кубический сплайн Эрмита.

    Параметры:
        x: массив координат точек.
        y: массив значений в точках.
        m: массив производных в точках.

    Возвращает:
        S: список кубических сплайнов Эрмита.
    """
    n = len(x)
    S = []

    for i in range(n - 1):
        # Вычисляем коэффициенты кубического сплайна для каждого сегмента
        h = x[i + 1] - x[i]
        a = y[i]
        b = m[i]
        c = (3*(y[i + 1] - y[i]) / h**2) - (2*m[i] / h) - (m[i + 1] / h)
        d = (-2*(y[i + 1] - y[i]) / h**3) + ((m[i] + m[i + 1]) / h**2)

        S.append((a, b, c, d))

    return S

def evaluate_cubic_hermite_spline(x, S):
    """
    Оценка значений кубического сплайна Эрмита в заданных точках.

    Параметры:
        x: массив координат точек.
        S: список кубических сплайнов Эрмита.

    Возвращает:
        y: массив значений кубического сплайна Эрмита в заданных точках.
    """
    y = []
    for xi in x:
        for i, spline in enumerate(S):
            if xi <= x[i + 1]:
                a, b, c, d = spline
                h = xi - x[i]
                y.append(a + b*h + c*h**2 + d*h**3)
                break

    return y


def smooth_polyline(points):
    """
    Сглаживание полилинии кубическими сплайнами Эрмита.

    Параметры:
        points: список объектов Point.

    Возвращает:
        smooth_points: сглаженные координаты полилинии.
    """
    x = [point.x for point in points]
    y = [point.y for point in points]
    z = [point.z for point in points]

    # Производные в точках можно задать различными способами, например, конечными разностями
    dx = np.gradient(x)
    dy = np.gradient(y)
    dz = np.gradient(z)

    # Создание кубических сплайнов Эрмита для каждой координаты
    Sx = cubic_hermite_spline(x, x, dx)
    Sy = cubic_hermite_spline(x, y, dy)
    Sz = cubic_hermite_spline(x, z, dz)

    print("Length of Sx:", len(Sx))
    print("Length of Sy:", len(Sy))
    print("Length of Sz:", len(Sz))

    # Оценка значений сплайнов в новых точках
    num_points = 100  # Количество точек на сглаженной кривой
    new_x = np.linspace(min(x), max(x), num_points)
    new_y = evaluate_cubic_hermite_spline(new_x, Sy)
    new_z = evaluate_cubic_hermite_spline(new_x, Sz)

    print("Length of new_x:", len(new_x))
    print("Length of new_y:", len(new_y))
    print("Length of new_z:", len(new_z))

    # Формирование списка сглаженных точек
    smooth_points = [Point(new_x[i], new_y[i], new_z[i]) for i in range(len(new_x))]

    return smooth_points


# Создание исходной полилинии
points = [
    Point(0, 0, 0),
    Point(1, 1, 1),
    Point(2, 0, 2),
    Point(3, -1, 3),
    Point(4, 0, 4)
]

# Сглаживание полилинии
smoothed_points = smooth_polyline(points)

# Визуализация исходной и сглаженной полилинии
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Исходная полилиния
x_orig = [point.x for point in points]
y_orig = [point.y for point in points]
z_orig = [point.z for point in points]
ax.plot(x_orig, y_orig, z_orig, 'ro-', label='Исходная полилиния')

# Сглаженная полилиния
x_smooth = [point.x for point in smoothed_points]
y_smooth = [point.y for point in smoothed_points]
z_smooth = [point.z for point in smoothed_points]
ax.plot(x_smooth, y_smooth, z_smooth, 'g-', label='Сглаженная полилиния')

# Настройка графика
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('Сглаживание полилинии кубическими сплайнами Эрмита')
ax.legend()

plt.show()
