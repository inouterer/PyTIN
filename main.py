from triangulation import Triangulation
from isocontourer import IsoConturer
from triangulation_classes import Point

from visualisation import plot_triangulation

from visualisation import visualize_contours

from sample_data import point_in, trn_in, real, real_levels #Main тут код запуска

# Добавим точки по исходному набору
def input_data (point_in):
    points = []
    for i in range(0,len(point_in)-1, 3):
        point = Point(point_in[i], point_in[i+1], point_in[i+2])
        points.append(point)
    return points

triangles = []

# import random
# num_points = 1000
# min_coord, max_coord = 0, 1000
# points = [Point(random.uniform(min_coord, max_coord), random.uniform(min_coord, max_coord),0) for _ in range(num_points)]

points = input_data(point_in) #Создали список объектов класса Points по рабочему набору
surface = Triangulation()
surface.triangulate(points)
surface.filter_triangles(1000, 5)
surface.get_bounds()

#surface.levels = real_levels
#surface.levels = [145]
surface.define_contours_levels(0, 1)
surface.build_contour_lines()
surface.smooth_contour_lines(5,0.25)


plot_triangulation(surface)

graf = IsoConturer()
graf.add_bounds(surface.bounds)
graf.add_isolines(surface.contour_lines)
graf.build_isocontours()

visualize_contours(graf.points, graf.isolines, graf.bounds, graf.isocontours)