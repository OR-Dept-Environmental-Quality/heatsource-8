from __future__ import division

class StreamChannel(object):
    """Class that describes the geometry of a stream channel

    This class includes all of the mathematics and geometry
    routines to define a trapezoidal stream channel, including
    methods for calculation of wetted depth from discharge
    using the Newton-Raphson iteration method. In the future,
    an argument can be added to the constructor to define other
    kinds of channels, or some of this can be pushed down to
    a base class.
    """
    def __init__(self):
        self.S = 0      # Slope
        self.n = 0      # Manning's n
        self.W_bf = 0    # Bankfull width (surface)
        self.z = 0      # z factor: Ration of run to rise of the side of a trapazoidal channel
        self.d_bf = 0    # Bankfull depth, calculated as W_bf/WD
        self.d_w = 0     # Wetted depth. Calculated in GetWettedDepth()
        self.W_b = 0     # Bottom width, calculated as W_bf - (2 * d_bf * z)
        self.W_w = 0     # Wetted width, calculated as W_b + 2*z*d_w
        self.A_x = 0     # Cross-sectional Area, calculated d_w * (W_b + z * d_w)
        self.P_w = 0     # Wetted Perimeter, calculated as W_b + 2 * d_w * sqrt(1 + z**2)
        self.R_h = 0     # Hydraulic Radius, calculated as A_x/P_w
        self.WD = 0     # Width/Depth ratio, constant
        self.dx = 0     # Length of this stream reach.

    def CalculateMorphology(self):
        """Calculate morphological characteristics in terms of W_bf, z and WD"""
        if self.z >= self.WD/2:
            raise Warning("Reach %s has no bottom width. Z: %0.3f, WD:%0.3f. Recalculating Channel angle." % (self, self.z, self.WD))
            self.z = 0.99 * (self.WD/2)

        # Estimate depth of the trapazoid from the width/depth ratio
        self.d_bf = self.W_bf/self.WD
        # Calculated the bottom of the channel by subtracting the differences between
        # Top and bottom of the trapazoid
        self.W_b = self.W_bf - (2 * self.d_bf * self.z)
        # Calculate the area of this newly estimated trapazoid
        self.A_x = (self.z * self.d_bf) * ((self.W_b + self.W_bf)/2)
        # NOTE: What follows is a strange calculation of the max depth, that was taken from
        # the original VB code. It basically increases depth until the area equals the
        # area of the bankfull rectangle (see the note in the docstring). This is not
        # an accurate representation of the maximum bankfull depth, but is included for
        # legacy reasons.
        BW = self.W_b
        D_Est = self.D_bf
        XArea = BW / self.WD
        # Here, we add to depth until the area equals the bankfull area.
        while True:
            Delta = (XArea - (BW + self.z * D_Est) * D_Est)
            if Delta < 0.0001: break
            D_Est += 0.01
        self.d_max = D_Est

    def GetWettedDepth(self, Q_est=None):
        """Use Newton-Raphson method to calculate wetted depth from current conditions

        Details on this can be found in the HeatSource manual Sec. 3.2.
        More general details on the technique can be found in Applied Hydrology
        in section 10.4.
        This method uses the NewtonRaphson method defined in Maths. It requires the
        derivative of the function, but we go ahead and work that out because using the
        derivative is more accurate and faster (programatically) than the secant method
        used in the original code.
        """
        # The function def is given in the HeatSource manual Sec 3.2... in three sections
        first = lambda x: x * (W + self.z * x) # Cross-sectional area formula
        second = lambda x: x * ((W + self.z * x) / (W + 2 * x * math.sqrt(1+(self.z**2))))**(2/3) # Hydraulic Radius to the 2/3,
        # The functional definition of wetted depth:
        Fd = lambda x: first(x) * second(x) - ((Q*self.n)/(self.S**(1/2)))
        # Here is the formula in terms of x, where x is the wetted depth.
        # (x*(w+(z*x))*((x*(w+(z*x)))/(w+(2*x*sqrt(1+z^2))))^(2/3))-((Q*n)/(s^(1/2)))
        # This can be used to calculate the derivative using software such as that on
        # http://wims.unice.fr/wims/ which will calculate derivatives online. Not that I'm too lazy
        # to do it myself or anything.

        # Here is the derivative of the equation in sections.
        first = lambda x: (5 * (x**(2/3)) * (x*z+w)**(5/3)) / (3*((2*x*math.sqrt((z**2)+1)+w)**(2/3)))
        second = lambda x: (5 * (x**(5/3)) * z * ((x*z+w)**(2/3))) / (3*((2*x*sqrt((z**2)+1)+w)**(2/3)))
        third = lambda x: (4 * (x**(5/3)) * (x*z+w)**(5/3) * sqrt(z^2+1)) / (3*((2*x*sqrt((z**2)+1)+w)**(5/3)))

        Fdd = lambda x: first(x) + second(x) - third(x)

        # Our Newton-Raphson method uses bracketing and binary search methods to dial down the function's zero.
        # Since we don't know our brackets each time, we make one up here, and assume that no stream is more than
        # 20 meters deep. We CAN put these minimum and maximum values in the IniParams class just to make things
        # easier to change, but until we know we need to, they will be left here.
        try:
            NewtonRaphson(Fd, Fdd, 0, 20) # Assume minimum (0) and maximum (20) meters in depth
        except:
            print "Failure to converge on a depth. Check minimum and maximum values for depth"
            raise
