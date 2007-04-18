from __future__ import division
"""Various mathematical routines and classes"""

def NewtonRaphson(f, df, a, b, tol=1.0e-5, maxiter=30):
    """Calculate the root of f(x) using the Newton-Raphson method.

    This method is taken from "Numerical Methods in Engineering with Python",
    Section 4.5, and assumes that the the root of f(x) lies within the
    bounds (a,b). It requires the derivative of f(x), which, if necessary, can
    be calculated using the secant method and an appropriate dx value.
    """
    fa = f(a)
    if fa == 0.0: return a
    fb = f(b)
    if fb == 0.0: return b
    if fa*fb > 0.0:
        print fa, fb
        raise Exception("Root not in (%0.3f,%0.3f)" % (a,b))
    x = 0.5*(a+b)
    for i in xrange(maxiter):
        fx = f(x)
        if abs(fx) < tol: return x
        # else, tighten brackets on the root
        if fa*fx < 0.0: b = x
        else:
            a = x
            fa = fx
        # Try a Newton-Raphson step
        dfx = df(x)
        # If division by zero, push x out of bounds
        try: dx = -fx/dfx
        except ZeroDivisionError: dx = b-a
        x = x + dx
        # If the result is inside, use bisection to dial down area
        if (b-x)*(x-a) < 0.0:
            dx = 0.5*(b-a)
            x = a+dx
        # Check for convergence
        if abs(dx) < tol * max(abs(b), 1.0): return x
    # If we get past the loop, then we've exceeded our maximum number of iterations
    #print x, abs(dx), tol + max(abs(b), 1.0)
    raise Exception("No convergences when calculating NewtonRaphson, is there a code problem?")

def NewtonRaphsonSecant(Fy):
    iterations = 1000
    Convergence = 10000
    dy = 0.001
    while True:
        y = y if y else 10
        data2.append(y)
        Fy = Yj(y)
#        print Fy, y,
        y += dy
        Fyy = Yj(y)
#        print Fyy, y
        dFy = (Fyy - Fy) / dy
        if y < 0 or y > 1e10 or iterations > 500:
          y = random.randint(1,100)
          Converge = 10
          iterations = 0
        Converge = abs(Fy/dFy)
        if Converge < 0.001:
            print "y is ", y
            break
        iterations += 1
        print y

##########################################################################
### Older version of Newton Raphson tests using SciPy and the secant method
#from __future__ import division
#from scipy import *
#from pylab import *
#import math, random
#data = []
#data2 = []
#
#Wbf = 8.5
#z = 0.5
#WD = 15
#Dbf = Wbf/WD
#S = 0.012
#n = 0.25
#
#dy = 0.001
#iterations = 0
#Converge = 10000
#
#def Wb(): return Wbf - 2*z*Dbf
#def A(dw): return dw*(Wb()+z*dw)
#def Pw(dw): return Wb() + 2*dw*math.sqrt(1+z**2)
#def Rh(dw): return A(dw)/Pw(dw)
#def Q(dw): return (1/n)*A(dw)*(Rh(dw)**(2/3))*(S**(1/2))
#def Yj(dw): return A(dw)*(Rh(dw)**(2/3))-((Q(dw)*n)/(S**(1/2)))
#
#
#def func(dw):
#  global data
#  data.append(dw)
#  return Yj(dw)
#
#def newton(x0):
#  root = optimize.newton(func, x0, fprime=None, args=(), tol=1.48e-08,
#  maxiter=500)
#  plot(range(len(data)),data)
#  xlabel('Iteration')
#  show()
#  print data
