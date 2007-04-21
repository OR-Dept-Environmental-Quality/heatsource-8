from __future__ import division
"""Various mathematical routines and classes"""

def NewtonRaphson(f, df, a, b, tol=1.0e-7, maxiter=500):
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


