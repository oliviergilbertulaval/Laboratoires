import numpy as np
import matplotlib.pyplot as plt
import scipy as sp
from spline_lineare_cubique import cubic_spline_interpolation, CubicSplinePiecewise

class ExponentialSplinePiecewise():
    def __init__(self, a, b, c, d, exes, p):
        self.a =  a
        self.b = b
        self.c = c
        self.d = d
        self.exes = exes
        self.p = p
        pass

    def exponential(self, x, a, b, c, d, x_k, p):
        return a+b*x+c*np.exp(p*x)+d*np.exp(-p*x)

    def __call__(self, x):
        i = 0
        if x < self.exes[0]:
            return self.exponential(x, self.a[0], self.b[0], self.c[0], self.d[0], self.exes[0], self.p[0])
        while self.exes[i] <= x and i < len(self.a):
            i += 1
        return self.exponential(x, self.a[i-1], self.b[i-1], self.c[i-1], self.d[i-1], self.exes[i-1], self.p[i-1])

def exponential_spline_interpolation_initial_tension(x, y, tension):
    """
    x: array-like of N values
    y: array-like of N values

    We will have (N-1) segments of exponential functions, which means we'll have 4(N-1) coefficients to store

    returns a Spline object which is a piecewise function (e.g. Spline(x)=y)

    **THIS FUNCTION IS NOT MEANT TO BE CALLED DIRECTLY, IT IS CALLED BY exponential_spline_interpolation()**
    """
    #Check if x and y are the same length:
    if len(x) != len(y):
        raise IndexError("x and y are not the same size")
    N = len(x)
    for i in range(1,N):
        if x[i-1] > x[i]:
            raise ValueError("x is not increasing")
    p = tension
    #We will have N-1 piecewise functions:
    #S[i] = a[i]*x**3+b[i]*x**2+c[i]*x+d[i]

    #We'll try to find the coefficients using *linear algebra*
    A = np.zeros((4*(N-1),4*(N-1)))
    B = np.zeros((4*(N-1),))

    for i in range(N-1):
        B[i] = y[i]
        A[i,4*i:4*(i+1)] = [1, x[i], np.exp(p[i]*x[i]), np.exp(-p[i]*x[i])]
    for i in range(N-1):
        B[N-1+i] = y[i+1]
        A[N-1+i,4*i:4*(i+1)] = [1, x[i+1], np.exp(p[i+1]*x[i+1]), np.exp(-p[i+1]*x[i+1])]
    for i in range(N-2):
        B[2*(N-1)+i] = 0
        A[2*(N-1)+i, 4*i:4*(i+2)] = [0, 1, p[i]*np.exp(p[i]*x[i+1]), -p[i]*np.exp(-p[i]*x[i+1]), 0, -1, -p[i+1]*np.exp(p[i+1]*x[i+1]), p[i+1]*np.exp(-p[i+1]*x[i+1])]
    for i in range(N-2):
        B[2*(N-1)+N-2+i] = 0
        A[2*(N-1)+N-2+i, 4*i:4*(i+2)] = [0, 0, p[i]**2*np.exp(p[i]*x[i+1]), p[i]**2*np.exp(-p[i]*x[i+1]), 0, 0, -p[i+1]**2*np.exp(p[i+1]*x[i+1]), -p[i+1]**2*np.exp(-p[i+1]*x[i+1])]
    #Conditions frontières
    B[-2:] = 0
    A[-2, :4] = [0, 0, p[0]**2*np.exp(p[0]*x[0]), p[0]**2*np.exp(-p[0]*x[0])]
    A[-1, -4:] = [0, 0, p[-1]**2*np.exp(p[-1]*x[-1]), p[0]**2*np.exp(-p[-1]*x[-1])]

    #Calculate the coefficient matrix
    X = np.linalg.solve(A, B)
    a = []
    b = []
    c = []
    d = []
    for i in range(int(len(X)/4)):
        a.append(X[i*4])
        b.append(X[i*4+1])
        c.append(X[i*4+2])
        d.append(X[i*4+3])

    return ExponentialSplinePiecewise(a, b, c, d, x, p)


def exponential_spline_interpolation(x, y, p='None'):
    #Check if x and y are the same length:
    if len(x) != len(y):
        raise IndexError("x and y are not the same size")
    N = len(x)
    for i in range(1,N):
        if x[i-1] > x[i]:
            raise ValueError("x is not increasing")
    #We calculate the cubic spline coefficients to find undesirable inflexion points
    cubic = cubic_spline_interpolation(x,y)
    ds = [(y[1]-y[0])/(x[1]-x[0])-cubic.b[0]]
    for i in range(1,N-1):
        h1 = x[i]-x[i-1]
        h2 = x[i+1]-x[i]
        ds.append((((y[i+1]-y[i])/h2)-((y[i]-y[i-1])/h1))/((h1+h2)/2))
        #ds.append((((cubic(x[i+1])-cubic(x[i]))/h2)-((cubic(x[i])-cubic(x[i-1]))/h1))/((h1+h2)/2))
    ds.append(cubic.b[-1]-(y[-1]-y[-2])/(x[-1]-x[-2]))

    undesirable_inflexion = []
    for i in range(N-1):
        if ds[i]*ds[i+1] > 0:
            undesirable_inflexion.append(1)
        else:
            undesirable_inflexion.append(0)
    #Create the tension vector:
    tension = []
    for i in range((len(undesirable_inflexion))):
        if undesirable_inflexion[i] == 1:
            tension.append(int(np.abs(ds[i]/(x[i+1]-x[i]))))
        else:
            tension.append(0)

    input_vector = np.ones(N,)*np.max(tension)
    if np.max(tension) > 30:
        #Even if the function is really weird, we don't want to make a linear-piecewise
        input_vector = np.ones(N,)*30
    #If user chose a specific exponent
    if p != "None":
        if p == 0:
            return cubic
        return exponential_spline_interpolation_initial_tension(x,y,tension=np.ones(N,)*int(p))
    if np.max(tension) == 0:
        return cubic
    return exponential_spline_interpolation_initial_tension(x,y,tension=input_vector)


if True:
    x = [0, .1, .499, .5, .6, 1.0, 1.4, 1.5, 1.899, 1.9, 2.0]
    y = [0, .06, .17, .19, .21, .26, .28, .29, .30, .31, .32]
    x_range = np.linspace(x[0], x[-1], 1000)
    

    ax1 = plt.subplot(111)
    ticklabels = ax1.get_xticklabels()
    ticklabels.extend( ax1.get_yticklabels() )
    for label in ticklabels:
        label.set_fontsize(14)
    tension_list = [0, 5, 10, 50, 100, 300]
    for k in tension_list:
        expSpline = exponential_spline_interpolation(x, y, p=k)
        expSpline_y = []
        for i in range(len(x_range)):
            expSpline_y.append(expSpline(x_range[i]))
        plt.plot(x_range, expSpline_y, linewidth=2, label=f'p={k}')
    plt.plot(x, y, 'o', color='black', label='Données')
    plt.legend(fontsize=11, loc='lower right')
    plt.show()

if True:
    x = [0.0, 1.0, 1.5, 2.5, 4.0, 4.5, 5.5, 6.0, 8.0, 10.0]
    y = [10, 8, 5, 4, 3.5, 3.4, 6, 7.1, 8, 8.5]

    x_range = np.linspace(x[0], x[-1], 1000)
    #expSpline = exponential_spline_interpolation_initial_tension(x, y, tension=5)
    expSpline = exponential_spline_interpolation(x, y)
    cubicSpline = cubic_spline_interpolation(x, y)

    ax1 = plt.subplot(111)
    ticklabels = ax1.get_xticklabels()
    ticklabels.extend( ax1.get_yticklabels() )
    for label in ticklabels:
        label.set_fontsize(14)
    expSpline_y = []
    cubicSpline_y = []
    for i in range(len(x_range)):
        expSpline_y.append(expSpline(x_range[i]))
        cubicSpline_y.append(cubicSpline(x_range[i]))
    plt.plot(x, y, 'o', color='red')
    plt.plot(x_range, cubicSpline_y, linewidth=2, label='Spline Cubique', color='orange')
    plt.plot(x_range, expSpline_y, linewidth=2, label='Spline Exponentielle', color='blue')
    plt.legend()
    plt.show()

if True:
    x = np.linspace(0, 4*np.pi, 30)
    def func(x):
        return np.sin(x)+np.exp(-x/2)
    y = []
    for i in range(len(x)):
        y.append(func(x[i]))

    x_range = np.linspace(x[0], x[-1], 1000)
    expSpline = exponential_spline_interpolation(x, y)
    cubicSpline = cubic_spline_interpolation(x, y)

    ax1 = plt.subplot(111)
    ticklabels = ax1.get_xticklabels()
    ticklabels.extend( ax1.get_yticklabels() )
    for label in ticklabels:
        label.set_fontsize(14)
    expSpline_y = []
    cubicSpline_y = []
    for i in range(len(x_range)):
        expSpline_y.append(expSpline(x_range[i]))
        cubicSpline_y.append(cubicSpline(x_range[i]))
    plt.plot(x, y, 'o', color='red')
    plt.plot(x_range, cubicSpline_y, linewidth=2, label='Spline Cubique', color='orange')
    plt.plot(x_range, expSpline_y, linewidth=2, label='Spline Exponentielle', color='blue')
    plt.legend(fontsize=11, loc='upper left')
    plt.show()

if True:
    x = [0, 1, 2, 3, 4, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 5, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 6, 7, 8, 9, 10]
    def func(x):
        if x > 4 and x < 6:
            return np.cos((x-5)*(np.pi/2))
        return 0
    y = []
    for i in range(len(x)):
        y.append(func(x[i]))

    x_range = np.linspace(x[0], x[-1], 1000)
    y_range = []
    expSpline = exponential_spline_interpolation(x, y)
    cubicSpline = cubic_spline_interpolation(x, y)

    ax1 = plt.subplot(111)
    ticklabels = ax1.get_xticklabels()
    ticklabels.extend( ax1.get_yticklabels() )
    for label in ticklabels:
        label.set_fontsize(14)
    expSpline_y = []
    cubicSpline_y = []
    for i in range(len(x_range)):
        expSpline_y.append(expSpline(x_range[i]))
        cubicSpline_y.append(cubicSpline(x_range[i]))
        y_range.append(func(x_range[i]))
    plt.plot(x, y, 'o', color='red')
    plt.plot(x_range, y_range, label='f(x)', color='green')
    plt.plot(x_range, cubicSpline_y, linewidth=2, label='Spline Cubique', color='orange')
    plt.plot(x_range, expSpline_y, linewidth=2, label='Spline Exponentielle', color='blue')
    plt.legend(fontsize=11, loc='upper left')
    plt.show()