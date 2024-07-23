import numpy as np  # Импортируем numpy для генерации случайных цветов
import matplotlib.pyplot as plt
import time

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
    for i in range(len(surface.custom_bounds)):
        plt.plot([surface.custom_bounds[i - 1].x, surface.custom_bounds[i].x], [surface.custom_bounds[i - 1].y, surface.custom_bounds[i].y], color='blue')
    # Визуализация катомных границ
    for i in range(len(surface.custom_bounds)):
        plt.plot([surface.custom_bounds[i - 1].x, surface.custom_bounds[i].x], [surface.custom_bounds[i - 1].y, surface.custom_bounds[i].y], color='green')
    
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

def visualize_contours(graf_points, points, isolines, custom_bounds, isocontours):
    """Отобразить изоконтуры IsoCоnturer в матплотлибе
    """
    size = 0.5
    plt.figure(figsize=(10, 10))

    # Визуализация границ
    x = [point.x for point in custom_bounds]
    y = [point.y for point in custom_bounds]
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
        #print (isocontour.from_height,"-", isocontour.to_height,":",isocontour.calculate_area(), "Color:",color, "RGBColor:",isocontour.rgb_color)
        plt.fill(x_values, y_values, color=color)  # Заливка цветом

    # Визуализация изолиний и их точек
    # print ("Визуализация изолиний и их точек")
    # for isoline in isolines:
    #     x = [point.x for point in isoline]
    #     y = [point.y for point in isoline]
    #     plt.plot(x, y, 'r-')  # Красные линии

    #     for point in points:
    #         plt.plot(point.x, point.y, 'ro', markersize=size)  # Красные точки

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





def visualize_profile(graf_points, points, isolines, custom_bounds, isocontours):
    """Отобразить изоконтуры IsoCоnturer в матплотлибе
    """
    start_time = time.time()  # Время начала выполнения
    size = 0.25
    plt.figure(figsize=(10, 10))


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
        #print (isocontour.from_height,"-", isocontour.to_height,":",isocontour.calculate_area(), "Color:",color, "RGBColor:",isocontour.rgb_color)
        plt.fill(x_values, y_values, color=color)  # Заливка цветом

    # Добавление точек с отметками
    print ("Добавление точек с отметками")
    i=0
    for point in points:
        plt.scatter(point.x, point.y, color='red', s=size)  # Рисуем точку
        plt.annotate(round(point.z,2), (point.x, point.y), textcoords="offset points", xytext=(0,2), ha='center', fontsize=8)
        i+=1
    # Визуализация изолиний и их точек
    # print ("Визуализация изолиний и их точек")
    for isoline in isolines:
        x = [point.x for point in isoline]
        y = [point.y for point in isoline]
        plt.plot(x, y, 'r-', linewidth=0.1)  # Красные линии

    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Visualization')
    plt.grid(True)
    print ("Показываем")
    end_time = time.time()    # Время окончания выполнения

    execution_time = end_time - start_time
    print(f"Время выполнения: {execution_time} секунд")
    plt.show()



import plotly.graph_objects as go

def plotly_iso(isocontours, points):
    fig = go.Figure()

    for isocontour in isocontours:
        x = [point.x for point in isocontour.points]
        y = [point.y for point in isocontour.points]
        rgb_color = 'rgb({},{},{})'.format(isocontour.rgb_color[0], isocontour.rgb_color[1], isocontour.rgb_color[2])
        
        fig.add_trace(go.Scatter(x=x, y=y, fill='toself', fillcolor=rgb_color, line=dict(color='gray', width=0.5), name=f'{isocontour.from_height} - {isocontour.to_height}'))

    for point in points:
        fig.add_trace(go.Scatter(x=[point.x], y=[point.y], mode='markers', marker=dict(color='red', size=5), name=point.name))

    for point in points:
        fig.add_trace(go.Scatter(x=[point.x], y=[point.y], mode='text', text=[f'{point.name} {round(point.z,1)}'], textposition='top center', textfont=dict(size=10, color='black')))

    fig.update_layout(title='Изоконтуры и точки с подписями',
                      xaxis_title='X',
                      yaxis_title='Y',
                      xaxis_scaleanchor='y',
                      yaxis_scaleanchor='x',
                      showlegend=False)

    fig.show()



