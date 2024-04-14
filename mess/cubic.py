# Cubic Spline Interpolation

import matplotlib.pyplot as plt


def cubic_interpolation(x, y):
    n = len(x) - 1

    h = [0 for i in range(n)]
    b = h[:]
    v = h[:]
    u = h[:]

    # SOME PRE-CALCULATIONS
    h[0] = x[1] - x[0]
    b[0] = (y[1] - y[0]) / h[0]
    for i in range(0, n):
        h[i] = x[i + 1] - x[i]
        b[i] = (y[i + 1] - y[i]) / h[i]
    for i in range(1, n):
        v[i] = 2*(h[i-1] + h[i])
        u[i] = 6*(b[i] - b[i-1])
    u = u[1:]

    # MAKE THE MATRICES
    A = [[0 for col in range(n-1)] for row in range(n-1)]

    # Fill in the first row of A
    A[0][0] = v[1]
    A[0][1] = h[1]

    # Fill in the other rows of A
    for i in range(1, n-2):
        row = []
        row.extend(0 for row in range(i-1))
        row.extend([h[i], v[i+1], h[i+1]])
        A[i] = row

    # Fill in the last row of A
    A[n-2][n-3] = h[n-2]
    A[n-2][n-2] = v[n-1]

    z = solve_matrix_tridiagonal(A, u)
    temp = [0]
    temp.extend(z)
    temp.append(0)
    z = temp

    return generate_spline_coefficients(h, z, y)


def solve_matrix_tridiagonal(A, u):
    n = len(A)
    # ELIMINATION STAGE
    for i in range(1, n):
        m = A[i][i-1]/A[i-1][i-1]
        A[i][i-1] = 0
        A[i][i] = A[i][i] - m*A[i-1][i]
        u[i] = u[i] - m * u[i - 1]

    # BACKWARDS SUBSTITUTION
    z = [0 for i in range(n)]
    z[n-1] = u[n - 1] / A[n - 1][n - 1]
    for i in reversed(range(n-1)):
        z[i] = (u[i] - A[i][i + 1] * z[i + 1]) / A[i][i]
    return z


def generate_spline_coefficients(h, z, y):
    n = len(z) - 1
    S = [[0, 0, 0, 0] for i in range(n)]
    for i in range(n):
        c1 = z[i+1]/(6*h[i])
        c2 = z[i]/(6*h[i])
        c3 = y[i+1]/h[i] - z[i+1]*h[i]/6
        c4 = y[i]/h[i] - h[i]*z[i]/6
        S[i] = [c1, c2, c3, c4]
    return S


def get_points(xi, xip1, step, coefficient):
    pts = []
    xval = xi

    if (xval < xip1):
        while xval < xip1:
            y = spline_eq(xval, xi, xip1, coefficient)
            pts.append([xval, y])
            xval += step
    else:
        while xval > xip1:
            y = spline_eq(xval, xi, xip1, coefficient)
            pts.append([xval, y])
            xval -= step
    return pts


def spline_eq(xval, xi, xip1, coefficient):
    return coefficient[0] * (xval - xi)**3 + coefficient[1] * (xip1 - xval)**3 \
           + coefficient[2] * (xval - xi) + coefficient[3] * (xip1 - xval)


def plot_splines(x, y, C, step):
    n = len(x) - 1
    pts = []
    for i in range(n):
        ipts = get_points(x[i], x[i+1], step, C[i])
        pts.extend(ipts)

    xinterpolated = [pts[i][0] for i in range(len(pts))]
    yinterpolated = [pts[i][1] for i in range(len(pts))]

    plt.scatter(xinterpolated, yinterpolated)
    plt.scatter(x, y)
    plt.show()


# Test Data Points
xv = [0.9, 1.3, 1.9, 2.1]
yv = [1.3, 1.5, 1.85, 0.1]
# xv = [1, 2, 3, 9, 1]
# yv = [2, 4, 7, 8, 12]
# xv = [1, 2, 3, 9, 5, 2]
# yv = [2, 9, 2, 2, 4, 1]

C = cubic_interpolation(xv, yv)
plot_splines(xv, yv, C, 0.01)




# A = [[1, 2, 0, 0], [2, 3, 1, 0], [0, 1, 2, 3], [0, 0, 4, 1]]
# b = [4, 9, 2, 1]
# solve_matrix_tridiagonal(A, b)