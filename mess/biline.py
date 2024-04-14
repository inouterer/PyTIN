import numpy as np
import matplotlib.pyplot as plt

def bilinear_interpolate(x, y, x_vals, y_vals, z_vals):
    # Индексы ближайших точек вниз и вверх по x и y
    x1_idx = np.searchsorted(x_vals, x) - 1
    x2_idx = x1_idx + 1
    y1_idx = np.searchsorted(y_vals, y) - 1
    y2_idx = y1_idx + 1

    # Значения в четырех углах
    x1, x2 = x_vals[x1_idx], x_vals[x2_idx]
    y1, y2 = y_vals[y1_idx], y_vals[y2_idx]
    q11 = z_vals[y1_idx, x1_idx]
    q12 = z_vals[y2_idx, x1_idx]
    q21 = z_vals[y1_idx, x2_idx]
    q22 = z_vals[y2_idx, x2_idx]

    if (x2 - x1) == 0 or (y2 - y1) == 0:  # Проверка на нулевой знаменатель
        return np.min([q11, q12, q21, q22])  # Простое решение для вырожденных случаев

    # Вычисление интерполированного значения
    return (q11 * (x2 - x) * (y2 - y) +
            q21 * (x - x1) * (y2 - y) +
            q12 * (x2 - x) * (y - y1) +
            q22 * (x - x1) * (y - y1)) / ((x2 - x1) * (y2 - y1))

# Параметры сетки
x_vals = np.linspace(1, 4, 4)
y_vals = np.linspace(1, 4, 4)
z_vals = np.array([
    [100, 150, 200, 250],
    [150, 200, 250, 300],
    [200, 250, 300, 350],
    [250, 300, 350, 400]
])

# Создание сетки для интерполяции
X, Y = np.meshgrid(np.linspace(1, 4, 50), np.linspace(1, 4, 50))
Z = np.array([[bilinear_interpolate(x, y, x_vals, y_vals, z_vals) for x in np.linspace(1, 4, 50)] for y in np.linspace(1, 4, 50)])

# Визуализация
plt.figure(figsize=(8, 6))
contour = plt.contourf(X, Y, Z, 20, cmap='viridis')
plt.colorbar(contour)
plt.scatter(x_vals, y_vals, color='red', zorder=5)
plt.title('Bilinear Interpolation Visualization')
plt.xlabel('X')
plt.ylabel('Y')
plt.grid(True)
plt.show()
