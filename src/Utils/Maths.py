from __future__ import division
import math
"""Various mathematical routines and classes"""

def NewtonRaphson(f, df, a, b, tol=1.0e-9, maxiter=500):
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

def NewtonRaphsonSecant(Q_est, W_b, z, n, S, D_est=0):
    """Copy of the method used in the HeatSource VB code"""
    dy = 0.01
    count = 0
    A = lambda d: d * (W_b + z * d)
    P_w = lambda d: W_b + 2 * d * math.sqrt(1+ z**2) or 0.00001
    R_h = lambda d: A(d)/P_w(d)
    Converge = 10
    while Converge > 0.0001:
        if not D_est: D_est = 10
        Fy = A(D_est) * (R_h(D_est)**(2/3)) - (n * Q_est) / math.sqrt(S)
        thed = D_est + dy
        Fyy = A(thed) * (R_h(thed)**(2/3)) - (n * Q_est) / math.sqrt(S)
        dFy = (Fyy - Fy) / dy or 0.99
        thed = D_est - Fy / dFy
        D_est = thed
        if D_est < 0 or D_est > 1.0e10 or count > 1000:
            D_est = random(randint(0,100))
            Converge = 10
            count = 0
        Converge = abs(Fy/dFy)
        count += 1
    return D_est

