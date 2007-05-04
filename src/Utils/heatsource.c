/* Generated by py2cmod
 *
 * py2cmod (c) 2001 Mark Rowe
 */

#include "Python.h"
#include <math.h>
#include <stdlib.h>

static PyObject *ErrorObject;

/* ----------------------------------------------------- */

static char heatsource_CalcSolarPosition__doc__[] =
"Calculates relative position of sun"
;

static PyObject *
heatsource_CalcSolarPosition(PyObject *self, PyObject *args)
{
	double lat;
	double lon;
	double hour;
	double min;
	double sec;
	double offset;
	double JDC;
	double Dummy; double Dummy1; double Dummy2; double Dummy3; double Dummy4; double Dummy5;
	/* temporary values calculated */
	double MeanObliquity; /* Average obliquity (degrees) */
	double Obliquity; /* Corrected obliquity (degrees) */
    double Eccentricity; /* Eccentricity of earth's orbit (unitless) */
    double GeoMeanLongSun; /*Geometric mean of the longitude of the sun*/
	double GeoMeanAnomalySun; /* Geometric mean of anomaly of the sun */
    double SunEqofCenter; /* Equation of the center of the sun (degrees)*/
    double SunApparentLong; /*Apparent longitude of the sun (degrees) */
    double Declination; /*Solar declination (degrees)*/
	double SunRadVector; /*    #Distance to the sun in AU */
	double Et; /* Equation of time (minutes)*/
	double SolarTime; /*Solar Time (minutes)*/
	double HourAngle;
	double Zenith; /*Solar Zenith Corrected for Refraction (degrees)*/
	double Azimuth; /* Solar azimuth in degrees */
	double Altitude; /*Solar Altitude Corrected for Refraction (degrees)*/
	double RefractionCorrection;
	double AtmElevation;
	double pi = 3.1415926535897931;
	double toRadians = pi/180.0;
	double toDegrees = 180.0/pi;


	if (!PyArg_ParseTuple(args, "ddddddd", &lat, &lon, &hour, &min, &sec, &offset, &JDC))
		return NULL;

    MeanObliquity = 23.0 + (26.0 + ((21.448 - JDC * (46.815 + JDC * (0.00059 - JDC * 0.001813))) / 60.0)) / 60.0;
    Obliquity = MeanObliquity + 0.00256 * cos(toRadians*((125.04 - 1934.136 * JDC)));
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

    /*#======================================================
    #Equation of time (minutes)*/
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

	return Py_BuildValue("fff",Azimuth,Altitude,Zenith);
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
    double Converge = 10.0;
    double dy = 0.01;
    int count = 0;
	double Fy;
	double Fyy;
	double dFy;
	double thed;
	double power = 2.0/3.0;
	double D_est = 0.0;
	if (!PyArg_ParseTuple(args, "dddddd", &Q_est, &W_b, &z, &n, &S, &D_est))
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
	/*        if ((D_est < 0) || (D_est > 5000) || (count > 10000))
	        {
	        	D_est = (double)rand();
	        	Converge = 0;
	        	count = 0;
	        }
	*/        Converge = fabs(Fy/dFy);
	        count += 1;
		}
	}
	double A = (D_est * (W_b + z * D_est));
	double Pw = (W_b + 2 * D_est * sqrt(1+ pow(z,2)));
	double Rh = A/Pw;
	double Ww = W_b + 2 * z * D_est;
	double U = Q_est / A;
    return Py_BuildValue("ffffff",D_est,A,Pw,Rh,Ww,U);
}
/* List of methods defined in the module */

static struct PyMethodDef heatsource_methods[] = {
	{"CalcSolarPosition", (PyCFunction) heatsource_CalcSolarPosition, METH_VARARGS,  heatsource_CalcSolarPosition__doc__},
		{"GetStreamGeometry", (PyCFunction) heatsource_GetStreamGeometry, METH_VARARGS,  heatsource_GetStreamGeometry__doc__},
	{NULL,	 (PyCFunction)NULL, 0, NULL}		/* sentinel */
};


/* Initialization function for the module (*must* be called initheatsource) */

static char heatsource_module_documentation[] =
""
;

void
initheatsource()
{
	PyObject *m, *d;

	/* Create the module and add the functions */
	m = Py_InitModule4("heatsource", heatsource_methods,
		heatsource_module_documentation,
		(PyObject*)NULL,PYTHON_API_VERSION);

	/* Add some symbolic constants to the module */
	d = PyModule_GetDict(m);
	ErrorObject = PyString_FromString("heatsource.error");
	PyDict_SetItemString(d, "error", ErrorObject);

	/* XXXX Add constants here */
	PyDict_SetItemString(d, "__file__", PyString_FromString("heatsource.py"));
	PyDict_SetItemString(d, "__name__", PyString_FromString("heatsource"));


	/* Check for errors */
	if (PyErr_Occurred())
		Py_FatalError("can't initialize module heatsource");
}
