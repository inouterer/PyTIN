import matplotlib.pyplot as plt

class Point:
    def __init__(self, x, y, z = 0):
        self.x = x
        self.y = y
        self.z = z
    def __ne__(self, other):
        # Перегрузка оператора неравенства (!=)
        return (self.x != other.x) or (self.y != other.y)
    def __eq__(self, other):
        # Перегрузка оператора неравенства (!=)
        return (self.x == other.x) and (self.y == other.y)

def catmull_rom_spline(p0, p1, p2, p3, num_points = 10, tau=0.5):
    """Генерирует точки Catmull-Rom сплайна для одного сегмента.
    
    (Нужна полилиния из 4 точек)"""
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
            
        points.append(Point(x, y))
    
    return points

def centripetal_catmull_rom_spline(p0, p1, p2, p3, num_points=10):
    """Generate points for a centripetal Catmull-Rom spline segment."""
    points = []
    for i in range(num_points):
        t = i / float(num_points - 1)
        t2 = t * t
        t3 = t2 * t

        # Centripetal Catmull-Rom equation
        x = 0.5 * ((2 * p1.x) +
                   (-p0.x + p2.x) * t +
                   (2 * p0.x - 5 * p1.x + 4 * p2.x - p3.x) * t2 +
                   (-p0.x + 3 * p1.x - 3 * p2.x + p3.x) * t3)
        y = 0.5 * ((2 * p1.y) +
                   (-p0.y + p2.y) * t +
                   (2 * p0.y - 5 * p1.y + 4 * p2.y - p3.y) * t2 +
                   (-p0.y + 3 * p1.y - 3 * p2.y + p3.y) * t3)
        points.append(Point(x, y))
    return points

def centripetal_catmull_rom_spline(p0, p1, p2, p3, num_points=10, tension=0.5):
    """Generate points for a Cubic Hermite spline segment."""
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

        x = h00 * p1.x + h10 * ((p2.x - p0.x) * tension) + h01 * p2.x + h11 * ((p3.x - p1.x) * tension)
        y = h00 * p1.y + h10 * ((p2.y - p0.y) * tension) + h01 * p2.y + h11 * ((p3.y - p1.y) * tension)

        points.append(Point(x, y))
    return points


control_points = [Point(-100, 0), Point(2, 2), Point(3, 1.9), Point(54, 3), Point(100, 0), Point(-100, 0)]

num_points = 10
tau = 0.25


# Создание сплайна

spline_points = []
if control_points[0] == control_points[-1]:
    del control_points[-1]
    control_points = [control_points[-2]] + [control_points[-1]] + control_points + [control_points[0]]
    for i in range (0, len(control_points)-3):
        spline_points.extend(centripetal_catmull_rom_spline(control_points[i], control_points[i+1], control_points[i+2], control_points[i+3], num_points, tau))
else:
    control_points = [control_points[0]] + control_points + [control_points[-1]]
    for i in range (0, len(control_points)-3):
        spline_points.extend(centripetal_catmull_rom_spline(control_points[i], control_points[i+1], control_points[i+2], control_points[i+3], num_points, tau))

# Визуализация
plt.figure(figsize=(10, 5))
plt.plot([p.x for p in control_points ], [p.y for p in control_points ], 'ro-', label='Control Points')
plt.plot([p.x for p in spline_points], [p.y for p in spline_points], 'b-', label='Catmull-Rom Spline')
plt.title('Catmull-Rom Spline Visualization')
plt.xlabel('X coordinate')
plt.ylabel('Y coordinate')
plt.legend()
plt.grid(True)
plt.show()
