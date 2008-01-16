/* Generated by py2cmod
 *
 * py2cmod (c) 2001 Mark Rowe
 */

#include "Python.h"
#include <math.h>
#include <stdlib.h>

static PyObject *HeatSourceError;

static char heatsource_CalcSolarPosition__doc__[] =
"CalcSolarPosition(*args)-> (Altitude, Zenith, Daytime, Direction) \
\
This method calculates the relative position of sun and returns a \
4 item tuple with altitude, solar zenith, a boolean telling whether \
it is daytime or not, and a direction. The direction is a number \
between 0 and 7 designating our rough cardinal direction. zero is \
north and numbers proceed clockwise around the compass directions. \
"
;

static PyObject *
heatsource_CalcSolarPosition(PyObject *self, PyObject *args, PyObject *kwargs)
{
	// Get all the arguments from the input tuple
	double lat = PyFloat_AsDouble(PyTuple_GetItem(args,0));
	double lon = PyFloat_AsDouble(PyTuple_GetItem(args,1));
	long hour = PyInt_AsLong(PyTuple_GetItem(args,2));
	long min = PyInt_AsLong(PyTuple_GetItem(args,3));
	long sec = PyInt_AsLong(PyTuple_GetItem(args,4));
	long offset = PyInt_AsLong(PyTuple_GetItem(args,5));
	double JDC = PyFloat_AsDouble(PyTuple_GetItem(args,6));

	// define a bunch of variables
	double Dummy,Dummy1,Dummy2,Dummy3,Dummy4,Dummy5;
	double MeanObliquity; // Average obliquity (degrees)
	double Obliquity; // Corrected obliquity (degrees)
    double Eccentricity; // Eccentricity of earth's orbit (unitless)
    double GeoMeanLongSun; //Geometric mean of the longitude of the sun
	double GeoMeanAnomalySun; // Geometric mean of anomaly of the sun
    double SunEqofCenter; // Equation of the center of the sun (degrees)
    double SunApparentLong; //Apparent longitude of the sun (degrees)
    double Declination; //Solar declination (degrees)
	double SunRadVector; //    #Distance to the sun in AU
	double Et; // Equation of time (minutes)
	double SolarTime; //Solar Time (minutes)
	double HourAngle;
	double Zenith; //Solar Zenith Corrected for Refraction (degrees)
	double Azimuth; // Solar azimuth in degrees
	double Altitude; //Solar Altitude Corrected for Refraction (degrees)
	double RefractionCorrection;
	double AtmElevation;
	double pi = 3.1415926535897931;
	double toRadians = pi/180.0;
	double toDegrees = 180.0/pi;

	///////////////////////////////////////////////////////////
	// Most of the following code is self-explanatory in that it is
	// essentially a bunch of math calculations. These should be relatively
	// easy to modify as long as proper C-syntax is kept (remember your semi-colons)
    MeanObliquity = 23.0 + (26.0 + ((21.448 - JDC * (46.815 + JDC * (0.00059 - JDC * 0.001813))) / 60.0)) / 60.0;
    Obliquity = MeanObliquity + 0.00256 * cos(toRadians*(125.04 - 1934.136 * JDC));
    Eccentricity = 0.016708634 - JDC * (0.000042037 + 0.0000001267 * JDC);
    GeoMeanLongSun = 280.46646 + JDC * (36000.76983 + 0.0003032 * JDC);

    while (GeoMeanLongSun < 0) { GeoMeanLongSun += 360; }
   	while (GeoMeanLongSun > 360) { GeoMeanLongSun -= 360; }
    GeoMeanAnomalySun = 357.52911 + JDC * (35999.05029 - 0.0001537 * JDC);

    Dummy1 = toRadians*(GeoMeanAnomalySun);
    Dummy2 = sin(Dummy1);
    Dummy3 = sin(Dummy2 * 2);
    Dummy4 = sin(Dummy3 * 3);
    SunEqofCenter = Dummy2 * (1.914602 - JDC * (0.004817 + 0.000014 * JDC)) + Dummy3 * (0.019993 - 0.000101 * JDC) + Dummy4 * 0.000289;
    SunApparentLong = (GeoMeanLongSun + SunEqofCenter) - 0.00569 - 0.00478 * sin(toRadians*((125.04 - 1934.136 * JDC)));

    Dummy1 = sin(toRadians*Obliquity) * sin(toRadians*SunApparentLong);
    Declination = toDegrees*(atan(Dummy1 / sqrt(-Dummy1 * Dummy1 + 1)));

    SunRadVector = (1.000001018 * (1 - pow(Eccentricity,2))) / (1 + Eccentricity * cos(toRadians*(GeoMeanAnomalySun + SunEqofCenter)));

    //======================================================
    //Equation of time (minutes)
    Dummy = pow((tan(Obliquity * pi / 360)),2);
    Dummy1 = sin(toRadians*(2 * GeoMeanLongSun));
    Dummy2 = sin(toRadians*(GeoMeanAnomalySun));
    Dummy3 = cos(toRadians*(2 * GeoMeanLongSun));
    Dummy4 = sin(toRadians*(4 * GeoMeanLongSun));
    Dummy5 = sin(toRadians*(2 * GeoMeanAnomalySun));
    Et = toDegrees*(4 * (Dummy * Dummy1 - 2 * Eccentricity * Dummy2 + 4 * Eccentricity * Dummy * Dummy2 * Dummy3 - 0.5 * pow(Dummy,2) * Dummy4 - 1.25 * pow(Eccentricity,2) * Dummy5));

    SolarTime = (hour*60.0) + min + (sec/60.0) + (Et - 4.0 * -lon + (offset*60.0));

    while (SolarTime > 1440.0) { SolarTime -= 1440.0;}
    HourAngle = SolarTime / 4.0 - 180.0;
    if (HourAngle < -180.0) { HourAngle += 360.0;}

    Dummy = sin(toRadians*lat) * sin(toRadians*Declination) + cos(toRadians*lat) * cos(toRadians*Declination) * cos(toRadians*HourAngle);
    if (Dummy > 1.0) { Dummy = 1.0; }
    else if (Dummy < -1.0) { Dummy = -1.0; }

    Zenith = toDegrees*(acos(Dummy));
    Dummy = cos(toRadians*lat) * sin(toRadians*Zenith);
    if (fabs(Dummy) >= 0.000999f)
    {
        Azimuth = (sin(toRadians*lat) * cos(toRadians*Zenith) - sin(toRadians*Declination)) / Dummy;
        if (fabs(Azimuth) > 1.0)
        {
            if (Azimuth < 0) { Azimuth = -1.0; }
            else { Azimuth = 1.0; }
        }
        Azimuth = 180 - toDegrees*(acos(Azimuth));
        if (HourAngle > 0) { Azimuth *= -1.0; }
    } else
    {
        if (lat > 0) { Azimuth = 180.0; }
        else { Azimuth = 0.0; }
    }
    if (Azimuth < 0) { Azimuth += 360.0; }

    AtmElevation = 90 - Zenith;
    if (AtmElevation > 85) { RefractionCorrection = 0;}
    else
    {
        Dummy = tan(toRadians*(AtmElevation));
        if (AtmElevation > 5) {RefractionCorrection = 58.1 / Dummy - 0.07 / pow(Dummy,3) + 0.000086 / pow(Dummy,5); }
        else if (AtmElevation > -0.575) { RefractionCorrection = 1735 + AtmElevation * (-518.2 + AtmElevation * (103.4 + AtmElevation * (-12.79 + AtmElevation * 0.711)));}
        else { RefractionCorrection = -20.774 / Dummy; }
        RefractionCorrection = RefractionCorrection / 3600;
    }
    Zenith = Zenith - RefractionCorrection;
    Altitude = 90 - Zenith;
	int Daytime = 0;
	if (Altitude > 0.0)
	{
		Daytime = 1;
	}
	/*******************************************************************
	 Here, we do a bit of Python programming from within this C
	 module. This is just so we don't have to do this in Python
	 later, since it's not actually used within Python.
	 What we have here is an implementation of a bisect routine
	 (see the Python bisect module documentation). The routine is
	 inlined here for speed. Look at the Python bisect code for details
	 on the implementation. I just took the actual code from the
	 Python module and re-created it here.

	 These are the azimuth angles which correspond to the 8 cardinal directions.
	 What we want to do is translate the Azimuth variable to a number between
	 0 and 7 to correspond to one of the directions. We do this because the
	 ShaderList (list of shade/topo angles) has 8 tuples of information, and we
	 want to slice with the correct tuple to get the shade values. Doing it
	 here is just faster than in Python because it's recalculated every time.
	**********************************************************************/
	float AzimuthBreaks[] = {0.0,67.5,112.5,157.5,202.5,247.5,292.5};
	int lo = 0;
	int hi = 7;
	int mid;
	float *litem;

	while (lo < hi) {
		mid = (lo + hi) / 2;
		litem = &AzimuthBreaks[mid];
		if (&litem == NULL)
		  	PyErr_SetString(HeatSourceError, "Bad value in SetSolarPosition's bisect routine (WTF? Better call for help.)");
		if ( Azimuth < *litem) { hi = mid;}
		else if (Azimuth >= *litem) {lo = mid + 1;}
		else {PyErr_SetString(HeatSourceError, "Bad value in SetSolarPosition's bisect routine (WTF? Better call for help.)");}

	}
	lo -= 1; // this cooresponds now to the cardinal direction

	return Py_BuildValue("ddii",Altitude,Zenith,Daytime,lo);
}

void
GetStreamGeometry(double Value[], double Q_est, double W_b, double z, double n, double S, double D_est, double dx, double dt)
{
	/*********************************************************
	 * This method takes stream characteristics, the most recently
	 * calculated discharge, and an optional estimated depth. It uses the
	 * secant method to iterate to a solution for wetted depth
	 * if the estimated depth is zero. If the estimated depth is
	 * a positive number, it uses that as wetted depth. It then
	 * uses this depth to calculate the new channel characteristics
	 * and uses those characteristics to calculate the physical
	 * dispersion.
	 ********************************************************/
    double Converge = 10.0;
    double dy = 0.01;
    int count = 0;
	double Fy;
	double Fyy;
	double dFy;
	double thed;
	double power = 2.0/3.0;
	if (W_b == 0.0) W_b = 0.01; //ASSUMPTION: Make bottom width 1 cm to prevent undefined numbers in the math.
	if (D_est == 0.0)
	{
		// This is a secant iterative solution method. It uses the equation for discharge at equality
		// then adds a slight change to the depth and solves it again. It should iterate for a solution to depth
		// within about 5-6 solutions.
	    while (Converge > 1e-6)
		{
	        Fy = (D_est * (W_b + z * D_est)) * pow(((D_est * (W_b + z * D_est)) / (W_b + 2 * D_est * sqrt(1+ pow(z,2)))),power) - ((n * Q_est) / sqrt(S));
	        thed = D_est + dy;
	        Fyy = (thed * (W_b + z * thed)) * pow((thed * (W_b + z * thed))/ (W_b + 2 * thed * sqrt(1+ pow(z,2))),power) - (n * Q_est) / sqrt(S);
	        dFy = (Fyy - Fy) / dy;
	        if (dFy <= 0) {dFy = 0.99;}
	        D_est -= Fy / dFy;
			// Damn, missed it. There may be a local minimum confusing us, so we choose another depth at random
			// and try again.
	        if ((D_est < 0) || (D_est > 5000) || (count > 10000))
	        {
	        	D_est = (double)rand();
	        	Converge = 0;
	        	count = 0;
	        }
	        Converge = fabs(Fy/dFy);
	        count += 1;
		}
	}
	// Use the calculated wetted depth to calculate new channel characteristics
	double A = (D_est * (W_b + z * D_est));
	double Pw = (W_b + 2 * D_est * sqrt(1+ pow(z,2)));
	double Rh = A/Pw;
	double Ww = W_b + 2 * z * D_est;
	double U = Q_est / A;
	double Dispersion, Shear_Velocity;

	// THis is a sheer velocity estimate, followed by an estimate of numerical dispersion
    if (S == 0.0) {
        Shear_Velocity = U;
    } else {
        Shear_Velocity = sqrt(9.8 * D_est * S);
    }
    Dispersion = (0.011 * pow(U,2.0) * pow(Ww,2.0)) / (D_est * Shear_Velocity);
    if ((Dispersion * dt / pow(dx,2.0)) > 0.5)
       Dispersion = (0.45 * pow(dx,2)) / dt;

	// The first argument is a pointer to an array, we just replace the array values in place
	// and don't return.
	Value[0] = D_est;
	Value[1] = A;
	Value[2] = Pw;
	Value[3] = Rh;
	Value[4] = Ww;
	Value[5] = U;
	Value[6] = Dispersion;
}

void CalcMuskingum(double Value[], double Q_est, double U, double W_w, double S, double dx, double dt)
{
	// Calculates the Muskingum coefficients for the routing model. Nothing complicated here,
	// look in Chow or somewhere for details on the calculations.
    double c_k = (5.0/3.0) * U;  // Wave celerity
    double X = 0.5 * (1.0 - Q_est / (W_w * S * dx * c_k));
    if (X > 0.5) { X = 0.5; }
    else if (X < 0.0) {	X = 0.0; }
    double K = dx / c_k;

    // Check the celerity to ensure stability. We throw a Python error if this test fails because
    // we want the error to propagate to the interface
    if (dt >= (2 * K * (1 - X)))
		{
			PyObject *msg = PyString_FromString("Unstable celerity. Decrease dt or increase dx");
			PyErr_SetObject(HeatSourceError, Py_BuildValue("(Offfff)", msg, dt, dx, K, X, c_k));
		}
    // These calculations are from Chow's "Applied Hydrology"
    double D = K * (1 - X) + 0.5 * dt;
    double C1 = (0.5*dt - K * X) / D;
    double C2 = (0.5*dt + K * X) / D;
    double C3 = (K * (1 - X) - 0.5*dt) / D;
	// change the array values then exit
	Value[0] = C1;
	Value[1] = C2;
	Value[2] = C3;
}

static char heatsource_CalcFlows__doc__[] =
"CalcFlows(*args)-> tuple of stream characteristics. \
\
This method takes values for discharge (Upstream, \
previous upstream and previous this node) and calls a \
method to calculate the Muskingum routing coefficients. \
It then calculates a new discharge, and calls another \
method to calculate the stream geometry. It returns a \
tuple of values with discharge, stream geometry and \
dispersion."
;

static PyObject * heatsource_CalcFlows(PyObject *self, PyObject *args)
{
	double U, W_w, S, dx, dt, W_b, z, n, D_est;
	double inputs, Q_up_prev, Q_up, Q, Q_bc;
	if (!PyArg_ParseTuple(args, "dddddddddddddd", &U, &W_w, &W_b, &S, &dx, &dt, &z, &n, &D_est,
											  	  &Q, &Q_up, &Q_up_prev, &inputs, &Q_bc))
		return NULL;
	// if there is a value for Q_bc, then we are at a boundary node and do not
	// need to calculate discharge.
	double Q_new;
	if (Q_bc >= 0)
	{
		Q_new = Q_bc;
	} else {
		double Q1 = Q_up + inputs;
		double Q2 = Q_up_prev + inputs;
		double Val[3] = {0.0,0.0,0.0}; // an array for the muskingum method to use
		CalcMuskingum(Val, Q2, U, W_w, S, dx, dt);
		Q_new = Val[0]*Q1 + Val[1]*Q2 + Val[2]*Q;
	}
	double Value[7] = {0.0,0.0,0.0,0.0,0.0,0.0,0.0,}; // an array for the geometry method to use
	if (Q_new > 0.003)
		GetStreamGeometry(Value, Q_new, W_b, z, n, S, D_est, dx, dt);

	PyObject *result = Py_BuildValue("f(fffffff)", Q_new, Value[0],Value[1],Value[2],
						 Value[3],Value[4],Value[5],Value[6]);
	return result;
}

void GetSolarFlux(double Value[], int hour, int JD, double Altitude,
					double Zenith, double cloud, double d_w, double W_b,
					double Elevation, double TopoFactor, double ViewToSky,
					double SampleDist, double phi, int emergent,
					double VDensity, double VHeight, double rip[], double veg[],
					double FullSunAngle, double TopoShadeAngle, double BankShadeAngle)
{
	// Constants
	double pi = 3.14159265358979323846f;
	double radians = pi/180.0;

	// Solar fluxes
	double direct_0 = 0.0;
	double direct_1 = 0.0;
	double direct_2 = 0.0;
	double direct_3 = 0.0;
	double direct_4 = 0.0;
	double direct_5 = 0.0;
	double direct_6 = 0.0;
	double direct_7 = 0.0;
	double diffuse_0 = 0.0;
	double diffuse_1 = 0.0;
	double diffuse_2 = 0.0;
	double diffuse_3 = 0.0;
	double diffuse_4 = 0.0;
	double diffuse_5 = 0.0;
	double diffuse_6 = 0.0;
	double diffuse_7 = 0.0;

    //#############################################################
    //Route solar radiation to the stream surface
    //   Flux_Solar(x) and Flux_Diffuse = Solar flux at various positions
    //       0 - Edge of atmosphere
    //       1 - Above Topography
    //       2 - Above Land Cover
    //       3 - Above Stream (After Land Cover Shade)
    //       4 - Above Stream (What a Solar Pathfinder Measures)
    //       5 - Entering Stream
    //       6 - Received by Water Column
    //       7 - Received by Bed
    //#######################################################
	//////////////////////////////////////////////////////////////////
	// 0 - Edge of atmosphere
	// TODO: Original VB code's JulianDay calculation:
	// JulianDay = -DateDiff("d", theTime, DateSerial(year(theTime), 1, 1))
	// THis calculation for Rad_Vec should be checked, with respect to the DST hour/24 part.
	double Rad_Vec = 1.0 + 0.017 * cos((2.0 * pi / 365.0) * (186.0 - JD + (double)hour / 24.0));
	double Solar_Constant = 1367.0; //W/m2
	direct_0 = (Solar_Constant / pow(Rad_Vec,2)) * sin(radians*(Altitude)); //Global Direct Solar Radiation
	///////////////////////////////////////////////////////////////////
    // 1 - Above Topography
    double Air_Mass = (35 / sqrt(1224 * sin(radians*Altitude) + 1)) * exp(-0.0001184 * Elevation);
    double Trans_Air = 0.0685 * cos((2 * pi / 365) * (JD + 10)) + 0.8;
    // Calculate Diffuse Fraction
	direct_1 = direct_0 * pow(Trans_Air,Air_Mass) * (1 - 0.65 * pow(cloud,2));
	double Clearness_Index;
    if (direct_0 == 0.0) { Clearness_Index = 1.0; }
    else {Clearness_Index = direct_1 / direct_0; }
    double Diffuse_Fraction = (0.938 + 1.071 * Clearness_Index) -
        (5.14 * pow(Clearness_Index,2)) +
        (2.98 * pow(Clearness_Index,3)) -
        (sin(2.0 * pi * (JD - 40.0) / 365.0)) *
        (0.009 - 0.078 * Clearness_Index);
    diffuse_1 = direct_1 * (Diffuse_Fraction) * (1 - 0.65 * pow(cloud,2));
    direct_1 *= (1 - Diffuse_Fraction);
    //########################################################
    //======================================================
    //2 - Above Land Cover
    // Empty
    //######################################################
    //======================================================
    //3 - Above Stream Surface (Above Bank Shade)
    if (Altitude <= TopoShadeAngle)	//>Topographic Shade IS Occurring<
    {
        direct_2 = 0;
        diffuse_2 = diffuse_1 * TopoFactor;
        direct_3 = 0;
        diffuse_3 = diffuse_2 * ViewToSky;
    }
    else if (Altitude < FullSunAngle) // #Partial shade from veg
    {
        direct_2 = direct_1;
        diffuse_2 = diffuse_1 * (1 - TopoFactor);
        double Dummy1 = direct_2;
        int i;
        for (i=0; i<4; i++)
        {
			if (Altitude < veg[i])
				Dummy1 *= (1.0-(1.0-exp(-1.0 * rip[i] * (SampleDist/cos(radians*Altitude)))));
		}
        direct_3 = Dummy1;
        diffuse_3 = diffuse_2 * ViewToSky;
    }
    else //Full sun
    {
        direct_2 = direct_1;
        diffuse_2 = diffuse_1 * (1 - TopoFactor);
        direct_3 = direct_2;
        diffuse_3 = diffuse_2 * ViewToSky;
    }

    //4 - Above Stream Surface (What a Solar Pathfinder measures)
    //Account for bank shade
    if ((Altitude > TopoShadeAngle) && (Altitude <= BankShadeAngle))  //Bank shade is occurring
    {
        direct_4 = 0;
        diffuse_4 = diffuse_3;
    }
    else  //bank shade is not occurring
    {
        direct_4 = direct_3;
        diffuse_4 = diffuse_3;
    }

    //Account for emergent vegetation
    if (emergent==1)
    {
    	double ripExtinctEmergent, shadeDensityEmergent;
        double pathEmergent = VHeight / sin(radians*Altitude);
        if (pathEmergent > W_b)
            pathEmergent = W_b;
        if (VDensity == 1.0)
        {
            VDensity = 0.9999;
            ripExtinctEmergent = 1.0;
            shadeDensityEmergent = 1.0;
        }
        else if (VDensity == 0.0)
        {
            VDensity = 0.00001;
            ripExtinctEmergent = 0.0;
            shadeDensityEmergent = 0.0;
        }
        else
        {
            ripExtinctEmergent = -log(1.0 - VDensity) / 10.0;
            shadeDensityEmergent = 1.0 - exp(-ripExtinctEmergent * pathEmergent);
        }
        direct_4 = direct_4 * (1.0 - shadeDensityEmergent);
		if (VHeight > 0.0)
		{
	        pathEmergent = VHeight;
    	    ripExtinctEmergent = -log(1.0 - VDensity) / VHeight;
        	shadeDensityEmergent = 1.0 - exp(-ripExtinctEmergent * pathEmergent);
        	diffuse_4 = diffuse_4 * (1.0 - shadeDensityEmergent);
		}
    }
    //:::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    //5 - Entering Stream
	double Stream_Reflect;
    if (Zenith > 80.0)
    {
        Stream_Reflect = 0.0515 * Zenith - 3.636;
    }
    else
    {
        Stream_Reflect = 0.091 * (1 / cos(Zenith * radians)) - 0.0386;
    }
    if (fabs(Stream_Reflect) > 1)
        Stream_Reflect = 0.0515 * (Zenith * radians) - 3.636;
    if (fabs(Stream_Reflect) > 1)
        Stream_Reflect = 0.091 * (1 / cos(Zenith * pi / 180)) - 0.0386;
    diffuse_5 = diffuse_4 * 0.91;
    direct_5 = direct_4 * (1 - Stream_Reflect);
    //:::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    //6 - Received by Water Column
	// Empty-
    //:::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    //7 - Received by Bed
    double Water_Path = d_w / cos(atan((sin(radians*Zenith) / 1.3333) / sqrt(-(sin(radians*Zenith) / 1.3333) * (sin(radians*Zenith) / 1.3333) + 1))); //Jerlov (1976)
    double Trans_Stream = 0.415 - (0.194 * log10(Water_Path * 100));
    if (Trans_Stream > 1)
        Trans_Stream = 1;
    double Dummy1 = direct_5 * (1 - Trans_Stream);       //Direct Solar Radiation attenuated on way down
    double Dummy2 = direct_5 - Dummy1 ;                  //Direct Solar Radiation Hitting Stream bed
    double Bed_Reflect = exp(0.0214 * (Zenith * radians) - 1.941);   //Reflection Coef. for Direct Solar
    double BedRock = 1 - phi;
    double Dummy3 = Dummy2 * (1 - Bed_Reflect);                //Direct Solar Radiation Absorbed in Bed
    double Dummy4 = 0.53 * BedRock * Dummy3;                  //Direct Solar Radiation Immediately Returned to Water Column as Heat
    double Dummy5 = Dummy2 * Bed_Reflect;                   //Direct Solar Radiation Reflected off Bed
    double Dummy6 = Dummy5 * (1 - Trans_Stream);              //Direct Solar Radiation attenuated on way up
    direct_6 = Dummy1 + Dummy4 + Dummy6;
    direct_7 = Dummy3 - Dummy4;
    Trans_Stream = 0.415 - (0.194 * log10(100 * d_w));
    if (Trans_Stream > 1)
        Trans_Stream = 1;
    Dummy1 = diffuse_5 * (1 - Trans_Stream);      //Diffuse Solar Radiation attenuated on way down
    Dummy2 = diffuse_5 - Dummy1;                  //Diffuse Solar Radiation Hitting Stream bed
    Bed_Reflect = exp(0.0214 * (0) - 1.941);               //Reflection Coef. for Diffuse Solar
    Dummy3 = Dummy2 * (1 - Bed_Reflect);                //Diffuse Solar Radiation Absorbed in Bed
    Dummy4 = 0.53 * BedRock * Dummy3;                   //Diffuse Solar Radiation Immediately Returned to Water Column as Heat
    Dummy5 = Dummy2 * Bed_Reflect;                      //Diffuse Solar Radiation Reflected off Bed
    Dummy6 = Dummy5 * (1 - Trans_Stream);               //Diffuse Solar Radiation attenuated on way up
    diffuse_6 = Dummy1 + Dummy4 + Dummy6;
    diffuse_7 = Dummy3 - Dummy4;

	//////////////////////////////////////////////
	Value[0] = diffuse_0 + direct_0;
	Value[1] = diffuse_1 + direct_1;
	Value[2] = diffuse_2 + direct_2;
	Value[3] = diffuse_3 + direct_3;
	Value[4] = diffuse_4 + direct_4;
	Value[5] = diffuse_5 + direct_5;
	Value[6] = diffuse_6 + direct_6;
	Value[7] = diffuse_7 + direct_7;
}

void GetGroundFluxes(double Value[], double Cloud, double Wind, double Humidity, double T_air, double Elevation,
					double phi, double VHeight, double ViewToSky, double SedDepth, double dx,
					double dt, double SedThermCond, double SedThermDiff, double FAlluvium, double P_w,
					double W_w, int emergent, int penman, double wind_a, double wind_b,
					int calcevap, double T_prev, double T_sed, double Q_hyp, double F_Solar5,
					double F_Solar7)
{
	//#################################################################
	// Bed Conduction Flux
    //======================================================
    //Calculate the conduction flux between water column & substrate
	double SedRhoCp = SedThermCond / (SedThermDiff/10000);
	// Water variables
	double rhow = 1000;				// water density (kg/m3)
	double H2O_HeatCapacity = 4187;	// J/(kg *C)

    double F_Conduction = SedThermCond * (T_sed - T_prev) / (SedDepth / 2);
    //Calculate the conduction flux between deeper alluvium & substrate
	double Flux_Conduction_Alluvium = 0.0;

    if (FAlluvium > 0)
    {
        Flux_Conduction_Alluvium = SedThermCond * (T_sed - FAlluvium) / (SedDepth / 2);
    }
    //======================================================
    //Calculate the changes in temperature in the substrate conduction layer
    // Negative hyporheic flow is heat into sediment
    double F_hyp = Q_hyp * rhow * H2O_HeatCapacity * (T_sed - T_prev) / ( W_w * dx);
    //Temperature change in substrate from solar exposure and conducted heat
    double NetFlux_Sed = F_Solar7 - F_Conduction - Flux_Conduction_Alluvium - F_hyp;
    double DT_Sed = NetFlux_Sed * dt / (SedDepth * SedRhoCp);
    //======================================================
    //Calculate the temperature of the substrate conduction layer
    double T_sed_new = T_sed + DT_Sed;
    if ((T_sed_new > 50.0f) || (T_sed_new < 0.0f))
	  	PyErr_SetString(HeatSourceError, "Sediment temperature not bounded in 0<=temp<=50.");
    // End Conduction Flux
	//###########################################################################################

	//##############################################################################
	// Longwave Flux
    double Sat_Vapor_Air = 6.1275 * exp(17.27 * T_air / (237.3 + T_air)); //mbar (Chapra p. 567)
    double Air_Vapor_Air = Humidity * Sat_Vapor_Air;
    double Sigma = 5.67e-8; //Stefan-Boltzmann constant (W/m2 K4)
    double Emissivity = 1.72 * pow(((Air_Vapor_Air * 0.1) / (273.2 + T_air)),(1.0/7.0)) * (1 + 0.22 * pow(Cloud,2.0)); //Dingman p 282
    //======================================================
    //Calcualte the atmospheric longwave flux
    double F_LW_Atm = 0.96 * ViewToSky * Emissivity * Sigma * pow((T_air + 273.2),4.0);
    //Calcualte the backradiation longwave flux
    double F_LW_Stream = -0.96 * Sigma * pow((T_prev + 273.2),4.0);
    //Calcualte the vegetation longwave flux
    double F_LW_Veg = 0.96 * (1 - ViewToSky) * 0.96 * Sigma * pow((T_air + 273.2),4);
	double F_Longwave = F_LW_Atm + F_LW_Stream + F_LW_Veg;
	//###############################################################################
	//######################################################################
	// Evaporative and Convective flux
	double F_evap, F_conv;
    double Pressure = 1013.0 - 0.1055 * Elevation; //mbar
    double Sat_Vapor = 6.1275 * exp(17.27 * T_prev / (237.3 + T_prev)); //mbar (Chapra p. 567)
    double Air_Vapor = Humidity * Sat_Vapor;
    //===================================================
    //Calculate the frictional reduction in wind velocity
    double Zd, Zo, Zm, Friction_Velocity;
    if ((emergent) && (VHeight > 0))
    {
        Zd = 0.7 * VHeight;
        Zo = 0.1 * VHeight;
        Zm = 2;
        Friction_Velocity = Wind * 0.4 / log((Zm - Zd) / Zo); //Vertical Wind Decay Rate (Dingman p. 594)
    } else {
        Zo = 0.00023; //Brustsaert (1982) p. 277 Dingman
        Zd = 0.0; //Brustsaert (1982) p. 277 Dingman
        Zm = 2.0;
        Friction_Velocity = Wind;
    }
    //===================================================
    //Wind Function f(w)
    double Wind_Function = wind_a + wind_b * Friction_Velocity; //m/mbar/s
    //===================================================
    //Latent Heat of Vaporization
    double LHV = 1000.0 * (2501.4 + (1.83 * T_prev)); //J/kg
    //===================================================
    //Use Jobson Wind Function
    double Bowen, K_evap;
    if (penman)
    {
        //Calculate Evaporation FLUX
        double P = 998.2; // kg/m3
        double Gamma = 1003.5 * Pressure / (LHV * 0.62198); //mb/*C  Cuenca p 141
        double Delta = 6.1275 * exp(17.27 * T_air / (237.3 + T_air)) - 6.1275 * exp(17.27 * (T_air - 1.0) / (237.3 + T_air - 1));
        double NetRadiation = F_Solar5 + F_Longwave;  //J/m2/s
        if (NetRadiation < 0.0)
        {
            NetRadiation = 0; //J/m2/s
        }
        double Ea = Wind_Function * (Sat_Vapor - Air_Vapor);  //m/s
        K_evap = ((NetRadiation * Delta / (P * LHV)) + Ea * Gamma) / (Delta + Gamma);
        F_evap = -K_evap * LHV * P; //W/m2
        //Calculate Convection FLUX
        Bowen = Gamma * (T_prev - T_air) / (Sat_Vapor - Air_Vapor);
    } else {
        //===================================================
        //Calculate Evaporation FLUX
        K_evap = Wind_Function * (Sat_Vapor - Air_Vapor);  //m/s
        double P = 998.2; // kg/m3
        F_evap = -K_evap * LHV * P; //W/m2
        //Calculate Convection FLUX
        if ((Sat_Vapor - Air_Vapor) != 0)
        {
            Bowen = 0.61 * (Pressure / 1000) * (T_prev - T_air) / (Sat_Vapor - Air_Vapor);
        } else {
            Bowen = 1.0;
        }
    }
    F_conv = F_evap * Bowen;
    double R_evap = 0.0;
    if (calcevap)
		R_evap = K_evap * W_w;
	// End Evap and Conv Flux
	//##############################################################################################
	Value[0] = F_Conduction;
	Value[1] = T_sed_new;
	Value[2] = F_Longwave;
	Value[3] = F_LW_Atm;
	Value[4] = F_LW_Stream;
	Value[5] = F_LW_Veg;
	Value[6] = F_evap;
	Value[7] = F_conv;
	Value[8] = R_evap;
}

void MacCormick(double Value[], double dt, double dx, double U, double T_sed, double T_prev, double Q_hyp,
			   PyObject *Q_tup, PyObject *T_tup, double Q_up, double Delta_T, double Disp, int S1,
			   double S1_value, double T0, double T1, double T2, double Q_accr, double T_accr)
{
	double T_up = T0;
	double Temp=0;
	double Q_in = 0.0;
	double T_in = 0.0;
	int i;
	double numerator = 0.0;
	PyObject *Qitem, *Titem;
	int size = PyTuple_Size(Q_tup);

	if (size > 0)
	{
		for (i=0; i<size; i++)
		{
			Qitem = PySequence_GetItem(Q_tup, i);
			Titem = PySequence_GetItem(T_tup, i);
			if ((Qitem == NULL) || (Titem == NULL))
				PyErr_SetString(HeatSourceError, "Null value in the tributary discharge or temperature");
			if ((PyFloat_Check(Qitem)) && (PyFloat_Check(Titem)) && (PyFloat_AsDouble(Qitem) > 0))
			{
				Q_in += PyFloat_AsDouble(Qitem);
				numerator += PyFloat_AsDouble(Qitem)*PyFloat_AsDouble(Titem);
			}
			Py_DECREF(Qitem);
			Py_DECREF(Titem);
		}
		if ((numerator > 0) && (Q_in > 0))
			T_in = numerator/Q_in;
	}
    // This is basically MixItUp from the VB code
    double T_mix = ((Q_in * T_in) + (T_up * Q_up)) / (Q_up + Q_in);
    //Calculate temperature change from mass transfer from hyporheic zone
    T_mix = ((T_sed * Q_hyp) + (T_mix * (Q_up + Q_in))) / (Q_hyp + Q_up + Q_in);
    //Calculate temperature change from accretion inflows
    // Q_hyp is commented out because we are not currently sure if it should be added to the flow. This
    // is because adding it will cause overestimation of the discharge if Q_hyp is not subtracted from
    // the total discharge (Q_in) somewhere else, which it is not. We should check this eventually.
    T_mix = ((Q_accr * T_accr) + (T_mix * (Q_up + Q_in + Q_hyp))) / (Q_accr + Q_up + Q_in + Q_hyp);
	T_mix -= T_up;
	T0 += T_mix;

    double Dummy1 = -U * (T1 - T0) / dx;
    double Dummy2 = Disp * (T2 - 2 * T1 + T0) / pow(dx,2);
    double S = Dummy1 + Dummy2 + Delta_T / dt;
	if (S1 > 0)
	{
		Temp = T_prev + ((S1_value + S) / 2) * dt;
	} else {
		Temp = T1 + S * dt;
	}
	Value[0] = Temp;
	Value[1] = S;
}

static char heatsource_CalcMacCormick__doc__[] =
"Central difference calculations for temperature ODE. \
\
This method calculates the central difference solution \
for temperature. We call it once immediately after hitting \
the solar flux calculation, which gives us an estimate of the \
current temperature. After calculating the downstream nodes \
estimated temperature, it's called again to calculate the \
central difference."
;

static PyObject *
heatsource_CalcMacCormick(PyObject *self, PyObject *args)
{
	double dt, dx, U, T_sed, T_prev, Q_up;
	double Q_hyp, Q_accr, T_accr;
	double Delta_T, Disp, S1_value;
	int S1;
	PyObject *Q_tup, *T_tup;
	double T0, T1, T2; // Grid cells for prev, this, next
	if (!PyArg_ParseTuple(args, "ddddddOOdddidddddd", &dt, &dx, &U, &T_sed,
														  &T_prev, &Q_hyp, &Q_tup, &T_tup,
												 		  &Q_up, &Delta_T, &Disp, &S1,
												 		  &S1_value, &T0, &T1, &T2, &Q_accr, &T_accr))
		return NULL;
	double Value[2] = {0.0,0.0};
	MacCormick(Value, dt, dx, U, T_sed, T_prev, Q_hyp, Q_tup, T_tup,
				Q_up, Delta_T, Disp, S1, S1_value, T0, T1, T2, Q_accr, T_accr);

	return Py_BuildValue("ff",Value[0], Value[1]);
}

static char heatsource_CalcHeatFluxes__doc__[] =
"CalcHeatFluxes(*args)-> tuple of 8 solar flux calculations \
\
Calculate the flux from incoming solar radiation for a given \
solar position. It returns a tuple of length 8 containing \
calculations for solar fluxs from incoming to stream."
;

static PyObject *
heatsource_CalcHeatFluxes(PyObject *self, PyObject *args)
{
	PyObject *ShaderList, *ContData, *C_args, *Q_tribs, *T_tribs;
	double W_b, Elevation, TopoFactor, ViewToSky, phi, VDensity, VHeight, SedDepth;
	double Altitude, Zenith, Q_up_prev, T_up_prev, T_dn_prev, Q_accr, T_accr, dx, dt;
	double SedThermCond, SedThermDiff, SampleDist, wind_a, wind_b, d_w, area, P_w, W_w;
	double U, T_alluv, T_prev, T_sed, Q_hyp, cloud, humidity, T_air, wind, Disp;
	int hour, JD, daytime, has_prev, emergent, calcevap, penman;
	if (!PyArg_ParseTuple(args, "OOdddddOOdddddOdiiidddd",
								&ContData, &C_args, &d_w, &area, &P_w, &W_w, &U,
								&Q_tribs, &T_tribs, &T_alluv, &T_prev, &T_sed, &Q_hyp,
								&T_dn_prev, &ShaderList, &Disp, &hour, &JD, &daytime,
								&Altitude, &Zenith, &Q_up_prev, &T_up_prev))
		return NULL;
	if (!PyArg_ParseTuple(ContData, "dddd", &cloud, &wind, &humidity, &T_air))
		return NULL;
	if (!PyArg_ParseTuple(C_args, "ddddddddddddddididdii",
								  &W_b, &Elevation, &TopoFactor, &ViewToSky, &phi, &VDensity, &VHeight,
								  &SedDepth, &dx, &dt, &SedThermCond, &SedThermDiff, &Q_accr, &T_accr,
								  &has_prev, &SampleDist, &emergent, &wind_a, &wind_b, &calcevap, &penman))
		return NULL;

	// Now deal with Shader list. The first three values are angles, the 4th value is
	// a tuple of riparian extinction values for the 4 zones and the 5th is a tuple of
	// angles for the top of vegetation for each zone
	double FullSunAngle = PyFloat_AsDouble(PyTuple_GetItem(ShaderList,0));   // Angle at which full sun hits stream
	double TopoShadeAngle = PyFloat_AsDouble(PyTuple_GetItem(ShaderList,1)); // Angle at which stream is shaded by distant topography
	double BankShadeAngle = PyFloat_AsDouble(PyTuple_GetItem(ShaderList,2)); // Angle at which stream is shaded by bank
	PyObject *RipExtinction = PyTuple_GetItem(ShaderList,3); // 4 element tuple of extinction cooefficients by zone
	PyObject *VegetationAngle = PyTuple_GetItem(ShaderList,4); // 4 element tuple of top-of-vegetation angles by zone
	// We strip out those 4 element tuples and put the values in an array for C to handle easily.
	double rip[4];
	double veg[4];
	int i;
	for (i=0; i<4; i++)
	{
		rip[i] = PyFloat_AsDouble(PyTuple_GetItem(RipExtinction,i));
		veg[i] = PyFloat_AsDouble(PyTuple_GetItem(VegetationAngle,i));
	}

	double solar[8] = {0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0};
	if (daytime)
	{
		GetSolarFlux(solar, hour, JD, Altitude, Zenith, cloud, d_w, W_b,
					Elevation, TopoFactor, ViewToSky, SampleDist, phi, emergent,
					VDensity, VHeight, rip, veg, FullSunAngle, TopoShadeAngle, BankShadeAngle);
	}
	double ground[9] = {0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0};
	GetGroundFluxes(ground, cloud, wind, humidity, T_air, Elevation,
					phi, VHeight, ViewToSky, SedDepth, dx,
					dt, SedThermCond, SedThermDiff, T_alluv, P_w,
					W_w, emergent, penman, wind_a, wind_b,
					calcevap, T_prev, T_sed, Q_hyp, solar[5],
					solar[7]);

	double F_Total =  solar[6] + ground[0] + ground[2] + ground[6] + ground[7];
	//////////////////////////////////////////

	//#### Calculate and set delta T
	double Delta_T = F_Total * dt / ((area / W_w) * 4182 * 998.2); // Vars are Cp (J/kg *C) and P (kgS/m3)

	if (!has_prev)
		return Py_BuildValue("(ffffffff)(fffffffff)ff",solar[0],solar[1],solar[2],solar[3],solar[4],solar[5],solar[6],solar[7],
									  ground[0],ground[1],ground[2],ground[3],ground[4],ground[5],ground[6],ground[7],ground[8],
									  F_Total, Delta_T);
	double Mac[2] = {0.0,0.0};
	MacCormick(Mac, dt, dx, U, ground[1], T_prev, Q_hyp, Q_tribs, T_tribs, Q_up_prev,
				Delta_T, Disp, 0, 0.0, T_up_prev, T_prev, T_dn_prev, Q_accr, T_accr);

	return Py_BuildValue("(ffffffff)(fffffffff)ff(ff)",solar[0],solar[1],solar[2],solar[3],solar[4],solar[5],solar[6],solar[7],
									  ground[0],ground[1],ground[2],ground[3],ground[4],ground[5],ground[6],ground[7],ground[8],
									  F_Total, Delta_T, Mac[0], Mac[1]);
}

/////////////////////////////////////////////////////////////////////////////////////////////////////////////

/* List of methods defined in the module */

static struct PyMethodDef heatsource_methods[] = {
	{"CalcSolarPosition", (PyCFunction) heatsource_CalcSolarPosition, METH_VARARGS,  heatsource_CalcSolarPosition__doc__},
	{"CalcHeatFluxes", (PyCFunction) heatsource_CalcHeatFluxes, METH_VARARGS,  heatsource_CalcHeatFluxes__doc__},
	{"CalcFlows", (PyCFunction) heatsource_CalcFlows, METH_VARARGS, heatsource_CalcFlows__doc__},
	{"CalcMacCormick", (PyCFunction) heatsource_CalcMacCormick, METH_VARARGS,  heatsource_CalcMacCormick__doc__},
	{NULL,	 (PyCFunction)NULL, 0, NULL}		/* sentinel */
};


/* Initialization function for the module (*must* be called initheatsource) */

static char heatsource_module_documentation[] =
"Provide optimized C functions for many heavy mathematical routines. \
\
The heatsource C module provides functions for calculating solar position, \
solar flux, ground fluxes, Muskingum routing, stream geometry and the \
MacCormick central difference calculation. They are provided here because \
the functions are hit every timestep and every spacestep, so we want to \
make them as fast as possible."
;

PyMODINIT_FUNC
initheatsource()
{
	PyObject *m, *d;

	/* Create the module and add the functions */
	m = Py_InitModule4("heatsource", heatsource_methods,
		heatsource_module_documentation,
		(PyObject*)NULL,PYTHON_API_VERSION);

	/* Add some symbolic constants to the module */
	d = PyModule_GetDict(m);
	HeatSourceError = PyString_FromString("HeatSourceError");
	Py_INCREF(HeatSourceError);
	PyDict_SetItemString(d, "HeatSourceError", HeatSourceError);

	/* XXXX Add constants here */
	PyDict_SetItemString(d, "__file__", PyString_FromString("heatsource.py"));
	PyDict_SetItemString(d, "__name__", PyString_FromString("heatsource"));


	/* Check for errors */
	if (PyErr_Occurred())
		Py_FatalError("can't initialize module heatsource");
}

