class Point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.marked = False
    def __ne__(self, other):
        # Перегрузка оператора неравенства (!=)
        return (self.x != other.x) or (self.y != other.y)
    def __eq__(self, other):
        # Перегрузка оператора равенства (==)
        return (self.x == other.x) and (self.y == other.y)


def assemble_polygon_from_noodles( noodles):#noodles это список списков точек
    """Собирает лапшу (список списка точек) в одну полилинию"""
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

    return polyline

finded =[(14551229.2825, 7664428.215, 125.99), (14551304.78, 7664374.608571429, 125.99), (14551319.231666667, 7664337.02, 125.99), (14551282.953, 7664302.635, 125.99), (14551239.854285715, 7664279.355714286, 125.99)]
cont =[(14551343, 7664809, 126), (14551519.42857143, 7664830.428571428, 131), (14551445.142857144, 7664780.428571428, 131), (14551370.0, 7664726.333333333, 131), (14551326.222222222, 7664699.111111111, 131), (14551318.0, 7664695.785714285, 131), (14551311.7, 7664692.6, 131), (14551225.545454545, 7664617.0, 131), (14551251.538461538, 7664495.153846154, 131), (14551384.6, 7664433.4, 
131), (14551393.214285715, 7664428.357142857, 131), (14551456.0, 7664450.5, 131), (14551417.0, 7664411.857142857, 131), (14551440.25, 7664343.5, 131), (14551426.222222222, 7664305.666666667, 131), (14551393.0, 7664269.5, 131), (14551356.6, 7664235.0, 131), (14551289.333333334, 7664198.666666667, 131), (14551241, 7664194, 130), (14551239.854285715, 7664279.355714286, 125.99)] 
finded = [Point(*coord) for coord in finded]
cont = [Point(*coord) for coord in cont]

noodles = [finded, cont]
x = assemble_polygon_from_noodles(noodles)
print (x)