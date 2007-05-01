from __future__ import division
import math, psyco
"""Various mathematical routines and classes"""

def NewtonRaphsonTangent(a, b, tol=1.0e-9, maxiter=500):
    """Calculate the root of f(x) using the Newton-Raphson method.

    This method is taken from "Numerical Methods in Engineering with Python",
    Section 4.5, and assumes that the the root of f(x) lies within the
    bounds (a,b). It requires the derivative of f(x), which, if necessary, can
    be calculated using the secant method and an appropriate dx value.

    Details on this can be found in the HeatSource manual Sec. 3.2.
    More general details on the technique can be found in Applied Hydrology
    in section 10.4.
    """
    first = lambda x: x * (W + z * x) # Cross-sectional area formula
    second = lambda x: (first(x) / (W + 2 * x * math.sqrt(1+z**2)))**(2/3) # Hydraulic Radius to the 2/3,
    # The functional definition of wetted depth:
    Fd = lambda x: first(x) * second(x) - ((Q_est*self.n)/(self.S**(1/2)))
    # Here is the formula in terms of x, where x is the wetted depth.
    # (x*(w+(z*x))*((x*(w+(z*x)))/(w+(2*x*sqrt(1+z^2))))^(2/3))-((Q*n)/(s^(1/2)))
    # This can be used to calculate the derivative using software such as that on
    # http://wims.unice.fr/wims/ which will calculate derivatives online. Not that I'm too lazy
    # to do it myself or anything.

    # Here is the derivative of the equation in sections.
    first = lambda x: (5 * (x**(2/3)) * ((x*z+W)**(5/3))) / (3*((2*x*math.sqrt((z**2)+1)+W)**(2/3)))
    second = lambda x: (5 * (x**(5/3)) * z * ((x*z+W)**(2/3))) / (3*((2*x*math.sqrt((z**2)+1)+W)**(2/3)))
    third = lambda x: (4 * (x**(5/3)) * ((x*z+W)**(5/3)) * math.sqrt(z**2+1)) / (3*((2*x*math.sqrt((z**2)+1)+W)**(5/3)))

    Fdd = lambda x: first(x) + second(x) - third(x)

    fa = Fd(a)
    if fa == 0.0: return a
    fb = Fd(b)
    if fb == 0.0: return b
    if fa*fb > 0.0:
        print fa, fb
        raise Exception("Root not in (%0.3f,%0.3f)" % (a,b))
    x = 0.5*(a+b)
    for i in xrange(maxiter):
        fx = Fd(x)
        if abs(fx) < tol: return x
        # else, tighten brackets on the root
        if fa*fx < 0.0: b = x
        else:
            a = x
            fa = fx
        # Try a Newton-Raphson step
        dfx = Fdd(x)
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
    Converge = 10
    while Converge > 0.0001:
        if not D_est: D_est = 10
        Fy = (D_est * (W_b + z * D_est)) * ((D_est * (W_b + z * D_est))/ (W_b + 2 * D_est * math.sqrt(1+ z**2)))**(2/3) - (n * Q_est) / math.sqrt(S)
        thed = D_est + dy
        Fyy = (thed * (W_b + z * thed)) * ((thed * (W_b + z * thed))/ (W_b + 2 * thed * math.sqrt(1+ z**2)))**(2/3) - (n * Q_est) / math.sqrt(S)
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
psyco.bind(NewtonRaphsonSecant)
