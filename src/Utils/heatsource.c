/* Generated by py2cmod
 *
 * py2cmod (c) 2001 Mark Rowe
 */

#include "Python.h"
#include <math.h>
#include <stdlib.h>

static PyObject *HeatSourceError;

static int
internal_bisect_right(PyObject *list, PyObject *item, Py_ssize_t lo, Py_ssize_t hi)
{
	PyObject *litem;
	Py_ssize_t mid, res;

	if (hi == -1) {
		hi = PySequence_Size(list);
		if (hi < 0)
			return -1;
	}
	while (lo < hi) {
		mid = (lo + hi) / 2;
		litem = PySequence_GetItem(list, mid);
		if (litem == NULL)
			return -1;
		res = PyObject_RichCompareBool(item, litem, Py_LT);
		Py_DECREF(litem);
		if (res < 0)
			return -1;
		if (res)
			hi = mid;
		else
			lo = mid + 1;
	}
	return lo;
}
/* ----------------------------------------------------- */

static char heatsource_CalcSolarPosition__doc__[] =
"Calculates relative position of sun"
;

static PyObject *
heatsource_CalcSolarPosition(PyObject *self, PyObject *args, PyObject *kwargs)
{
	double lat = PyFloat_AsDouble(PyTuple_GetItem(args,0));
	double lon = PyFloat_AsDouble(PyTuple_GetItem(args,1));
	long hour = PyInt_AsLong(PyTuple_GetItem(args,2));
	long min = PyInt_AsLong(PyTuple_GetItem(args,3));
	long sec = PyInt_AsLong(PyTuple_GetItem(args,4));
	long offset = PyInt_AsLong(PyTuple_GetItem(args,5));
	double JDC = PyFloat_AsDouble(PyTuple_GetItem(args,6));

	double Dummy,Dummy1,Dummy2,Dummy3,Dummy4,Dummy5;
	// temporary values calculated
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

	PyObject *AzimuthBreaks = Py_BuildValue("(fffffff)",0.0,67.5,112.5,157.5,202.5,247.5,292.5);
	PyObject *Az = Py_BuildValue("f",Azimuth);
	int direction = internal_bisect_right(AzimuthBreaks, Az, 0, -1)-1;
	/////////////////////////////////////////////////////////
	// De-reference all unused Python objects
	Py_DECREF(AzimuthBreaks);
	Py_DECREF(Az);
	int Daytime = 0;
	if (Altitude > 0.0)
	{
		Daytime = 1;
	}

	return Py_BuildValue("ddii",Altitude,Zenith,Daytime,direction);
}


static char heatsource_GetStreamGeometry__doc__[] =
"Return a stream's geometry\n\nGiven the known parameters for bottom width, Z factor, Manning\'s n and slope\nas well as the estimated Discharge, this function returns the\nwetted depth (found in a Newton-Raphson iteration or as optional D_est keyword),\narea, wetted perimeter, hydraulic radius, wetted width and velocity."
;

static PyObject *
heatsource_GetStreamGeometry(PyObject *self, PyObject *args, PyObject *keywds)
{
	double Q_est;
	double W_b;
	double z;
	double n;
	double S;
	double dt,dx;
    double Converge = 10.0;
    double dy = 0.01;
    int count = 0;
	double Fy;
	double Fyy;
	double dFy;
	double thed;
	double power = 2.0/3.0;
	double D_est = 0.0;
	if (!PyArg_ParseTuple(args, "dddddddd", &Q_est, &W_b, &z, &n, &S, &D_est, &dx, &dt))
		return NULL;
	if (D_est == 0.0)
	{
	    while (Converge > 1e-8)
		{
	        Fy = (D_est * (W_b + z * D_est)) * pow(((D_est * (W_b + z * D_est)) / (W_b + 2 * D_est * sqrt(1+ pow(z,2)))),power) - ((n * Q_est) / sqrt(S));
	        thed = D_est + dy;
	        Fyy = (thed * (W_b + z * thed)) * pow((thed * (W_b + z * thed))/ (W_b + 2 * thed * sqrt(1+ pow(z,2))),power) - (n * Q_est) / sqrt(S);
	        dFy = (Fyy - Fy) / dy;
	        if (dFy <= 0) {dFy = 0.99;}
	        D_est -= Fy / dFy;
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
	double A = (D_est * (W_b + z * D_est));
	double Pw = (W_b + 2 * D_est * sqrt(1+ pow(z,2)));
	double Rh = A/Pw;
	double Ww = W_b + 2 * z * D_est;
	double U = Q_est / A;
	double Dispersion, Shear_Velocity;
    if (S == 0.0) {
        Shear_Velocity = U;
    } else {
        Shear_Velocity = sqrt(9.8 * D_est * S);
    }
    Dispersion = (0.011 * pow(U,2.0) * pow(Ww,2.0)) / (D_est * Shear_Velocity);
    if ((Dispersion * dt / pow(dx,2.0)) > 0.5)
    {
       Dispersion = (0.45 * pow(dx,2)) / dt;
    }


    return Py_BuildValue("fffffff",D_est,A,Pw,Rh,Ww,U,Dispersion);
}

static char heatsource_CalcMuskingum__doc__[] =
"Calculate the Muskingum coefficients for routing"
;

static PyObject *
heatsource_CalcMuskingum(PyObject *self, PyObject *args)
{
	float Q_est, U, W_w, S, dx, dt;
	if (!PyArg_ParseTuple(args, "ffffff", &Q_est, &U, &W_w, &S, &dx, &dt))
		return NULL;
    float c_k = (5.0/3.0) * U;  // Wave celerity
    float X = 0.5 * (1.0 - Q_est / (W_w * S * dx * c_k));
    if (X > 0.5) { X = 0.5; }
    else if (X < 0.0) {	X = 0.0; }
    float K = dx / c_k;

    // Check the celerity to ensure stability. These tests are from the VB code.
    if ((dt >= (2 * K * (1 - X))) || (dt > (dx/c_k)))  //Unstable - Decrease dt or increase dx
        PyErr_SetString(HeatSourceError, "Unstable celerity. Decrease dt or increase dx");

    // These calculations are from Chow's "Applied Hydrology"
    float D = K * (1 - X) + 0.5 * dt;
    float C1 = (0.5*dt - K * X) / D;
    float C2 = (0.5*dt + K * X) / D;
    float C3 = (K * (1 - X) - 0.5*dt) / D;
    // TODO: reformulate this using an updated model, such as Moramarco, et.al., 2006
    return Py_BuildValue("fff",C1, C2, C3);

}


static char heatsource_CalcSolarFlux__doc__[] =
"Calculate the flux from incoming solar radiation."
;

static PyObject *
heatsource_CalcSolarFlux(PyObject *self, PyObject *args)
{
	int hour, JD, emergent;
	double Altitude, Zenith, cloud, d_w, W_b;
	double Elevation, TopoFactor, ViewToSky;
	double SampleDist, phi, VDensity, VHeight;
	PyObject *ShaderList;
	if (!PyArg_ParseTuple(args, "iiddddddddddiddO", &hour, &JD, &Altitude,
														&Zenith, &cloud, &d_w, &W_b,
														&Elevation, &TopoFactor, &ViewToSky,
														&SampleDist, &phi, &emergent,
														&VDensity, &VHeight, &ShaderList))
        return NULL;

	double FullSunAngle = PyFloat_AsDouble(PyTuple_GetItem(ShaderList,0));   // Angle at which full sun hits stream
	double TopoShadeAngle = PyFloat_AsDouble(PyTuple_GetItem(ShaderList,1)); // Angle at which stream is shaded by distant topography
	double BankShadeAngle = PyFloat_AsDouble(PyTuple_GetItem(ShaderList,2)); // Angle at which stream is shaded by bank
	PyObject *RipExtinction = PyTuple_GetItem(ShaderList,3); // 4 element tuple of extinction cooefficients by zone
	PyObject *VegetationAngle = PyTuple_GetItem(ShaderList,4); // 4 element tuple of top-of-vegetation angles by zone
	double rip[4];
	double veg[4];
	int i;
	for (i=0; i<4; i++)
	{
		rip[i] = PyFloat_AsDouble(PyTuple_GetItem(RipExtinction,i));
		veg[i] = PyFloat_AsDouble(PyTuple_GetItem(VegetationAngle,i));
	}
	// Constants
	float pi = 3.14159265358979323846f;
	float radians = pi/180.0;

	// Solar fluxes
	float direct_0 = 0.0;
	float direct_1 = 0.0;
	float direct_2 = 0.0;
	float direct_3 = 0.0;
	float direct_4 = 0.0;
	float direct_5 = 0.0;
	float direct_6 = 0.0;
	float direct_7 = 0.0;
	float diffuse_0 = 0.0;
	float diffuse_1 = 0.0;
	float diffuse_2 = 0.0;
	float diffuse_3 = 0.0;
	float diffuse_4 = 0.0;
	float diffuse_5 = 0.0;
	float diffuse_6 = 0.0;
	float diffuse_7 = 0.0;
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
	float Rad_Vec = 1.0 + 0.017 * cos((2.0 * pi / 365.0) * (186.0 - JD + (float)hour / 24.0));
	float Solar_Constant = 1367.0; //W/m2
	direct_0 = (Solar_Constant / pow(Rad_Vec,2)) * sin(radians*(Altitude)); //Global Direct Solar Radiation
	///////////////////////////////////////////////////////////////////
    // 1 - Above Topography
    float Air_Mass = (35 / sqrt(1224 * sin(radians*Altitude) + 1)) * exp(-0.0001184 * Elevation);
    float Trans_Air = 0.0685 * cos((2 * pi / 365) * (JD + 10)) + 0.8;
    // Calculate Diffuse Fraction
	direct_1 = direct_0 * pow(Trans_Air,Air_Mass) * (1 - 0.65 * pow(cloud,2));
	float Clearness_Index;
    if (direct_0 == 0.0) { Clearness_Index = 1.0; }
    else {Clearness_Index = direct_1 / direct_0; }
    float Diffuse_Fraction = (0.938 + 1.071 * Clearness_Index) -
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
        float Dummy1 = direct_2;
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
    	float ripExtinctEmergent, shadeDensityEmergent;
        float pathEmergent = VHeight / sin(radians*Altitude);
        if (pathEmergent > W_b)
		{
            pathEmergent = W_b;
		}
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
	float Stream_Reflect;
    if (Zenith > 80.0)
    {
        Stream_Reflect = 0.0515 * Zenith - 3.636;
    }
    else
    {
        Stream_Reflect = 0.091 * (1 / cos(Zenith * radians)) - 0.0386;
    }
    if (fabs(Stream_Reflect) > 1)
    {
        Stream_Reflect = 0.0515 * (Zenith * radians) - 3.636;
    }
    if (fabs(Stream_Reflect) > 1)
    {
        Stream_Reflect = 0.091 * (1 / cos(Zenith * pi / 180)) - 0.0386;
    }
    diffuse_5 = diffuse_4 * 0.91;
    direct_5 = direct_4 * (1 - Stream_Reflect);
    //:::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    //6 - Received by Water Column
	// Empty-
    //:::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    //7 - Received by Bed
    float Water_Path = d_w / cos(atan((sin(radians*Zenith) / 1.3333) / sqrt(-(sin(radians*Zenith) / 1.3333) * (sin(radians*Zenith) / 1.3333) + 1))); //Jerlov (1976)
    float Trans_Stream = 0.415 - (0.194 * log10(Water_Path * 100));
    if (Trans_Stream > 1)
    {
        Trans_Stream = 1;
    }
    float Dummy1 = direct_5 * (1 - Trans_Stream);       //Direct Solar Radiation attenuated on way down
    float Dummy2 = direct_5 - Dummy1 ;                  //Direct Solar Radiation Hitting Stream bed
    float Bed_Reflect = exp(0.0214 * (Zenith * radians) - 1.941);   //Reflection Coef. for Direct Solar
    float BedRock = 1 - phi;
    float Dummy3 = Dummy2 * (1 - Bed_Reflect);                //Direct Solar Radiation Absorbed in Bed
    float Dummy4 = 0.53 * BedRock * Dummy3;                  //Direct Solar Radiation Immediately Returned to Water Column as Heat
    float Dummy5 = Dummy2 * Bed_Reflect;                   //Direct Solar Radiation Reflected off Bed
    float Dummy6 = Dummy5 * (1 - Trans_Stream);              //Direct Solar Radiation attenuated on way up
    direct_6 = Dummy1 + Dummy4 + Dummy6;
    direct_7 = Dummy3 - Dummy4;
    Trans_Stream = 0.415 - (0.194 * log10(100 * d_w));
    if (Trans_Stream > 1)
    {
        Trans_Stream = 1;
    }
    Dummy1 = diffuse_5 * (1 - Trans_Stream);      //Diffuse Solar Radiation attenuated on way down
    Dummy2 = diffuse_5 - Dummy1;                  //Diffuse Solar Radiation Hitting Stream bed
    Bed_Reflect = exp(0.0214 * (0) - 1.941);               //Reflection Coef. for Diffuse Solar
    Dummy3 = Dummy2 * (1 - Bed_Reflect);                //Diffuse Solar Radiation Absorbed in Bed
    Dummy4 = 0.53 * BedRock * Dummy3;                   //Diffuse Solar Radiation Immediately Returned to Water Column as Heat
    Dummy5 = Dummy2 * Bed_Reflect;                      //Diffuse Solar Radiation Reflected off Bed
    Dummy6 = Dummy5 * (1 - Trans_Stream);               //Diffuse Solar Radiation attenuated on way up
    diffuse_6 = Dummy1 + Dummy4 + Dummy6;
    diffuse_7 = Dummy3 - Dummy4;

	float solar_0 = diffuse_0 + direct_0;
	float solar_1 = diffuse_1 + direct_1;
	float solar_2 = diffuse_2 + direct_2;
	float solar_3 = diffuse_3 + direct_3;
	float solar_4 = diffuse_4 + direct_4;
	float solar_5 = diffuse_5 + direct_5;
	float solar_6 = diffuse_6 + direct_6;
	float solar_7 = diffuse_7 + direct_7;

//	return Py_BuildValue("(ffffffff)(ffffffff)(ffffffff)",solar_0,solar_1,solar_2,solar_3,solar_4,solar_5,solar_6,solar_7,
//														  direct_0,direct_1,direct_2,direct_3,direct_4,direct_5,direct_6,direct_7,
//														  diffuse_0,diffuse_1,diffuse_2,diffuse_3,diffuse_4,diffuse_5,diffuse_6,diffuse_7);
	return Py_BuildValue("(ffffffff)",solar_0,solar_1,solar_2,solar_3,solar_4,solar_5,solar_6,solar_7);
}

static char heatsource_CalcGroundFluxes__doc__[] =
"Calculate the flux from bed conduction, longwave (atmospheric, vegetation and stream), evaporation and convection."
;

static PyObject *
heatsource_CalcGroundFluxes(PyObject *self, PyObject *args)
{
	double Cloud, Humidity, T_air, Wind;
	double Elevation, phi, VHeight, ViewToSky, SedDepth;
	double dx, dt, SedThermCond, SedThermDiff, FAlluvium;
	double P_w, W_w;
	int emergent, penman, calcevap;
	double wind_a, wind_b, T_prev, T_sed, Q_hyp;
	double F_Solar5, F_Solar7;

	if (!PyArg_ParseTuple(args, "ddddddddddddddddiiddiddddd",
								&Cloud, &Humidity, &T_air, &Wind, &Elevation,
								&phi, &VHeight, &ViewToSky, &SedDepth, &dx,
								&dt, &SedThermCond, &SedThermDiff, &FAlluvium, &P_w,
								&W_w, &emergent, &penman, &wind_a, &wind_b,
								&calcevap, &T_prev, &T_sed, &Q_hyp, &F_Solar5,
								&F_Solar7))
        return NULL;
	//#################################################################
	// Bed Conduction Flux
    //======================================================
    //Calculate the conduction flux between water column & substrate
	float SedRhoCp = SedThermCond / (SedThermDiff/10000);
	// Water variables
	float rhow = 1000;				// water density (kg/m3)
	float H2O_HeatCapacity = 4187;	// J/(kg *C)

    float F_Conduction = SedThermCond * (T_sed - T_prev) / (SedDepth / 2);
    //Calculate the conduction flux between deeper alluvium & substrate
	float Flux_Conduction_Alluvium = 0.0;

    if (FAlluvium > 0)
    {
        Flux_Conduction_Alluvium = SedThermCond * (T_sed - FAlluvium) / (SedDepth / 2);
    }
    //======================================================
    //Calculate the changes in temperature in the substrate conduction layer
    // Negative hyporheic flow is heat into sediment
    float F_hyp = Q_hyp * rhow *H2O_HeatCapacity * (T_sed - T_prev) / ( W_w * dx);
    //Temperature change in substrate from solar exposure and conducted heat
    float NetFlux_Sed = F_Solar7 - F_Conduction - Flux_Conduction_Alluvium - F_hyp;
    float DT_Sed = NetFlux_Sed * dt / (SedDepth * SedRhoCp);
    //======================================================
    //Calculate the temperature of the substrate conduction layer
    float T_sed_new = T_sed + DT_Sed;
    if ((T_sed_new > 50.0f) || (T_sed_new < 0.0f))
	  	PyErr_SetString(HeatSourceError, "Sediment temperature calculations causing an unstable model in CalcGroundFluxes()");
    // End Conduction Flux
	//###########################################################################################
	//##############################################################################
	// Longwave Flux
    float Sat_Vapor_Air = 6.1275 * exp(17.27 * T_air / (237.3 + T_air)); //mbar (Chapra p. 567)
    float Air_Vapor_Air = Humidity * Sat_Vapor_Air;
    float Sigma = 5.67e-8; //Stefan-Boltzmann constant (W/m2 K4)
    float Emissivity = 1.72 * pow(((Air_Vapor_Air * 0.1) / (273.2 + T_air)),(1.0/7.0)) * (1 + 0.22 * pow(Cloud,2.0)); //Dingman p 282
    //======================================================
    //Calcualte the atmospheric longwave flux
    float F_LW_Atm = 0.96 * ViewToSky * Emissivity * Sigma * pow((T_air + 273.2),4.0);
    //Calcualte the backradiation longwave flux
    float F_LW_Stream = -0.96 * Sigma * pow((T_prev + 273.2),4.0);
    //Calcualte the vegetation longwave flux
    float F_LW_Veg = 0.96 * (1 - ViewToSky) * 0.96 * Sigma * pow((T_air + 273.2),4);
	float F_Longwave = F_LW_Atm + F_LW_Stream + F_LW_Veg;
	//###############################################################################
	//######################################################################
	// Evaporative and Convective flux
	float F_evap, F_conv;
    float Pressure = 1013.0 - 0.1055 * Elevation; //mbar
    float Sat_Vapor = 6.1275 * exp(17.27 * T_prev / (237.3 + T_prev)); //mbar (Chapra p. 567)
    float Air_Vapor = Humidity * Sat_Vapor;
    //===================================================
    //Calculate the frictional reduction in wind velocity
    float Zd, Zo, Zm, Friction_Velocity;
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
    float Wind_Function = wind_a + wind_b * Friction_Velocity; //m/mbar/s
    //===================================================
    //Latent Heat of Vaporization
    float LHV = 1000.0 * (2501.4 + (1.83 * T_prev)); //J/kg
    //===================================================
    //Use Jobson Wind Function
    float Bowen, K_evap;
    if (penman)
    {
        //Calculate Evaporation FLUX
        float P = 998.2; // kg/m3
        float Gamma = 1003.5 * Pressure / (LHV * 0.62198); //mb/*C  Cuenca p 141
        float Delta = 6.1275 * exp(17.27 * T_air / (237.3 + T_air)) - 6.1275 * exp(17.27 * (T_air - 1.0) / (237.3 + T_air - 1));
        float NetRadiation = F_Solar5 + F_Longwave;  //J/m2/s
        if (NetRadiation < 0.0)
        {
            NetRadiation = 0; //J/m2/s
        }
        float Ea = Wind_Function * (Sat_Vapor - Air_Vapor);  //m/s
        K_evap = ((NetRadiation * Delta / (P * LHV)) + Ea * Gamma) / (Delta + Gamma);
        F_evap = -K_evap * LHV * P; //W/m2
        //Calculate Convection FLUX
        Bowen = Gamma * (T_prev - T_air) / (Sat_Vapor - Air_Vapor);
    } else {
        //===================================================
        //Calculate Evaporation FLUX
        K_evap = Wind_Function * (Sat_Vapor - Air_Vapor);  //m/s
        float P = 998.2; // kg/m3
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
    float V_evap = 0.0;
    if (calcevap) {
		V_evap = K_evap * (dx * W_w);
    }
	// End Evap and Conv Flux
	//##############################################################################################
	return Py_BuildValue("fffffffff",F_Conduction,T_sed_new, F_Longwave, F_LW_Atm, F_LW_Stream, F_LW_Veg, F_evap, F_conv, V_evap);
}

static char heatsource_CalcMacCormick__doc__[] =
"Calculate central difference, first iteration"
;

static PyObject *
heatsource_CalcMacCormick(PyObject *self, PyObject *args)
{
	float dt, dx, U, T_sed, T_prev;
	float Q_up, T_up, Q_in, T_in;
	float Q_hyp, Q_accr, T_accr;
	float Delta_T, Disp, S1_value, Temp;
	int S1;
	float T0, T1, T2; // Grid cells for prev, this, next
	if (!PyArg_ParseTuple(args, "fffffffffffiffffff", &dt, &dx, &U, &T_sed, &T_prev, &Q_hyp, &Q_in,
												 &T_in, &Q_up, &Delta_T, &Disp,
												 &S1, &S1_value, &T0, &T1, &T2, &Q_accr, &T_accr))
		return NULL;
	T_up = T0;
    // This is basically MixItUp from the VB code
    float T_mix = ((Q_in * T_in) + (T_up * Q_up)) / (Q_up + Q_in);
    //Calculate temperature change from mass transfer from hyporheic zone
    T_mix = ((T_sed * Q_hyp) + (T_mix * (Q_up + Q_in))) / (Q_hyp + Q_up + Q_in);
    //Calculate temperature change from accretion inflows
    // Q_hyp is commented out because we are not currently sure if it should be added to the flow. This
    // is because adding it will cause overestimation of the discharge if Q_hyp is not subtracted from
    // the total discharge (Q_in) somewhere else, which it is not. We should check this eventually.
    T_mix = ((Q_accr * T_accr) + (T_mix * (Q_up + Q_in /*+ Q_hyp*/))) / (Q_accr + Q_up + Q_in /*+ Q_hyp*/);
	T_mix -= T_up;
	T0 += T_mix;

    float Dummy1 = -U * (T1 - T0) / dx;
    float Dummy2 = Disp * (T2 - 2 * T1 + T0) / pow(dx,2);
    float S = Dummy1 + Dummy2 + Delta_T / dt;
	if (S1 > 0)
	{
		Temp = T_prev + ((S1_value + S) / 2) * dt;
	} else {
		Temp = T1 + S * dt;
	}
	return Py_BuildValue("ff",Temp, S);

}

/////////////////////////////////////////////////////////////////////////////////////////////////////////////

/* List of methods defined in the module */

static struct PyMethodDef heatsource_methods[] = {
	{"CalcSolarPosition", (PyCFunction) heatsource_CalcSolarPosition, METH_VARARGS,  heatsource_CalcSolarPosition__doc__},
	{"GetStreamGeometry", (PyCFunction) heatsource_GetStreamGeometry, METH_VARARGS,  heatsource_GetStreamGeometry__doc__},
	{"CalcMuskingum", (PyCFunction) heatsource_CalcMuskingum, METH_VARARGS,  heatsource_CalcMuskingum__doc__},
	{"CalcSolarFlux", (PyCFunction) heatsource_CalcSolarFlux, METH_VARARGS,  heatsource_CalcSolarFlux__doc__},
	{"CalcGroundFluxes", (PyCFunction) heatsource_CalcGroundFluxes, METH_VARARGS,  heatsource_CalcGroundFluxes__doc__},
	{"CalcMacCormick", (PyCFunction) heatsource_CalcMacCormick, METH_VARARGS,  heatsource_CalcMacCormick__doc__},
	{NULL,	 (PyCFunction)NULL, 0, NULL}		/* sentinel */
};


/* Initialization function for the module (*must* be called initheatsource) */

static char heatsource_module_documentation[] =
""
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
	HeatSourceError = PyString_FromString("HeatSource Error");
	Py_INCREF(HeatSourceError);
	PyDict_SetItemString(d, "heatsource.error", HeatSourceError);

	/* XXXX Add constants here */
	PyDict_SetItemString(d, "__file__", PyString_FromString("heatsource.py"));
	PyDict_SetItemString(d, "__name__", PyString_FromString("heatsource"));


	/* Check for errors */
	if (PyErr_Occurred())
		Py_FatalError("can't initialize module heatsource");
}

