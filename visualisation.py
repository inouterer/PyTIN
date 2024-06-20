from traceback import print_list
import numpy as np  # Импортируем numpy для генерации случайных цветов
import matplotlib.pyplot as plt

#Отобразим результат
def plot_triangulation(surface):
    """Отобразить треугольники и изолинии в матплотлибе
    """
        
    plt.figure(figsize=(10, 10))

    # Визуализация ребер триангуляции
    for triangle in surface.triangles:
        for edge in triangle.edges:
            plt.plot([edge.start.x, edge.end.x], [edge.start.y, edge.end.y], color='gray')

    # Визуализация границ триангуляции
    for i in range(len(surface.bounds)):
        plt.plot([surface.bounds[i - 1].x, surface.bounds[i].x], [surface.bounds[i - 1].y, surface.bounds[i].y], color='blue')
    
    # Добавление точек с отметками
    i=0
    for point in surface.points:
        plt.scatter(point.x, point.y, color='red')  # Рисуем точку
        plt.annotate(f'h{round(point.z,2)} n{i}', (point.x, point.y), textcoords="offset points", xytext=(0,10), ha='center')
        i+=1

    #Визуализация изолиний

    for contour_line in surface.contour_lines:
        # Генерация случайного цвета
        color = np.random.rand(3,)
        x = [point.x for point in contour_line.points]
        y = [point.y for point in contour_line.points]
        plt.plot(x, y, color='pink')

    # Визуализация сглаженных изолиний
    for contour_line in surface.sm_contour_lines:
        # Генерация случайного цвета
        color = np.random.rand(3,)
        x = [point.x for point in contour_line.points]
        y = [point.y for point in contour_line.points]
        plt.plot(x, y, color=color)

    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Triangulation Plot')
    plt.grid(True)
    plt.show()

def visualize_contours(graf_points, points, isolines, bounds, isocontours):
    """Отобразить изоконтуры IsoCоnturer в матплотлибе
    """
    size = 0.5
    plt.figure(figsize=(10, 10))

    # Визуализация границ
    x = [point.x for point in bounds]
    y = [point.y for point in bounds]
    plt.plot(x, y, 'g-')  # Зеленая линия

    import random

    # Визуализация изоконтуров с заливкой
    print ("Визуализация изоконтуров")
    for isocontour in isocontours:
        contour_points = isocontour.get_contour_points()
        # Разделяем координаты x и y
        x_values = [point.x for point in contour_points]
        y_values = [point.y for point in contour_points]
        # Добавляем первую точку в конец для замыкания линии
        x_values.append(contour_points[0].x)
        y_values.append(contour_points[0].y)
        
        color = tuple(c / 255 for c in isocontour.rgb_color)  # Нормализуем значения цвета к диапазону [0, 1]
        print (isocontour.from_height,"-", isocontour.to_height,":",isocontour.calculate_area(), "Color:",color, "RGBColor:",isocontour.rgb_color)
        plt.fill(x_values, y_values, color=color)  # Заливка цветом

    # Визуализация изолиний и их точек
    print ("Визуализация изолиний и их точек")
    for isoline in isolines:
        x = [point.x for point in isoline]
        y = [point.y for point in isoline]
        plt.plot(x, y, 'r-')  # Красные линии

        for point in points:
            plt.plot(point.x, point.y, 'ro', markersize=size)  # Красные точки

    # Добавление точек с отметками
    print ("Добавление точек с отметками")
    i=0
    for point in points:
        plt.scatter(point.x, point.y, color='red', s=size)  # Рисуем точку
        plt.annotate(f'h{round(point.z,2)} n{i}', (point.x, point.y), textcoords="offset points", xytext=(0,10), ha='center')
        i+=1
    # Добавление точек с отметками
    i=0
    for point in graf_points:
        plt.scatter(point.x, point.y, color='blue', s=size)  # Рисуем точку
        plt.annotate(f'h{round(point.z,2)} n{i}', (point.x, point.y), textcoords="offset points", xytext=(0,10), ha='center')
        i+=1

    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Visualization')
    plt.grid(True)
    print ("Показываем")
    plt.show()