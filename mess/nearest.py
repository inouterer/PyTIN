def find_nearest(point, data_points):
    # Находит ближайшую точку и возвращает значение высоты этой точки
    min_distance = float('inf')
    nearest_value = None
    for (x, y, value) in data_points:
        distance = (x - point[0])**2 + (y - point[1])**2
        if distance < min_distance:
            min_distance = distance
            nearest_value = value
    return nearest_value

def interpolate_nearest_neighbor(data_points, x_range, y_range, resolution):
    # Создание регулярной сетки
    x_min, x_max = x_range
    y_min, y_max = y_range
    grid_x = [x_min + i * (x_max - x_min) / resolution for i in range(resolution + 1)]
    grid_y = [y_min + i * (y_max - y_min) / resolution for i in range(resolution + 1)]

    # Интерполяция данных
    interpolated_grid = []
    for x in grid_x:
        row = []
        for y in grid_y:
            nearest_value = find_nearest((x, y), data_points)
            row.append(nearest_value)
        interpolated_grid.append(row)
    
    return interpolated_grid

# Пример исходных данных (x, y, value)
data_points = [
    (1, 1, 100), (2, 2, 200), (3, 3, 300), (1.5, 1.5, 150),
    (2.5, 0.5, 250), (3.5, 2, 350), (0.5, 3.5, 50)
]

# Параметры сетки
x_range = (0, 4)
y_range = (0, 4)
resolution = 10

# Интерполяция
grid = interpolate_nearest_neighbor(data_points, x_range, y_range, resolution)

# Визуализация в текстовом формате
print("Интерполированная сетка:")
for row in grid:
    print(" ".join("{:4}".format(int(v)) for v in row))
