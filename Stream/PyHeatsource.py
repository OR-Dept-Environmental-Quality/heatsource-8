
class HeatSourceError(Exception): pass

class heatsource(object):

    def CalcSolarPosition(self, lat, lon, hour, min, sec, offset, JDC):
        toRadians = pi/180.0
        toDegrees = 180.0/pi
        MeanObliquity = 23.0 + (26.0 + ((21.448 - JDC * (46.815 + JDC * (0.00059 - JDC * 0.001813))) / 60.0)) / 60.0
        Obliquity = MeanObliquity + 0.00256 * cos(toRadians*(125.04 - 1934.136 * JDC))
        Eccentricity = 0.016708634 - JDC * (0.000042037 + 0.0000001267 * JDC)
        GeoMeanLongSun = 280.46646 + JDC * (36000.76983 + 0.0003032 * JDC)

        while GeoMeanLongSun < 0:
            GeoMeanLongSun += 360
        while GeoMeanLongSun > 360:
            GeoMeanLongSun -= 360
        GeoMeanAnomalySun = 357.52911 + JDC * (35999.05029 - 0.0001537 * JDC)

        Dummy1 = toRadians*GeoMeanAnomalySun
        Dummy2 = sin(Dummy1)
        Dummy3 = sin(Dummy2 * 2)
        Dummy4 = sin(Dummy3 * 3)
        SunEqofCenter = Dummy2 * (1.914602 - JDC * (0.004817 + 0.000014 * JDC)) + Dummy3 * (0.019993 - 0.000101 * JDC) + Dummy4 * 0.000289
        SunApparentLong = (GeoMeanLongSun + SunEqofCenter) - 0.00569 - 0.00478 * sin(toRadians*((125.04 - 1934.136 * JDC)))

        Dummy1 = sin(toRadians*Obliquity) * sin(toRadians*SunApparentLong)
        Declination = toDegrees*(atan(Dummy1 / sqrt(-Dummy1 * Dummy1 + 1)))

        SunRadVector = (1.000001018 * (1 - pow(Eccentricity,2))) / (1 + Eccentricity * cos(toRadians*(GeoMeanAnomalySun + SunEqofCenter)))

        #======================================================
        #Equation of time (minutes)
        Dummy = pow((tan(Obliquity * pi / 360)),2)
        Dummy1 = sin(toRadians*(2 * GeoMeanLongSun))
        Dummy2 = sin(toRadians*(GeoMeanAnomalySun))
        Dummy3 = cos(toRadians*(2 * GeoMeanLongSun))
        Dummy4 = sin(toRadians*(4 * GeoMeanLongSun))
        Dummy5 = sin(toRadians*(2 * GeoMeanAnomalySun))
        Et = toDegrees*(4 * (Dummy * Dummy1 - 2 * Eccentricity * Dummy2 + 4 * Eccentricity * Dummy * Dummy2 * Dummy3 - 0.5 * pow(Dummy,2) * Dummy4 - 1.25 * pow(Eccentricity,2) * Dummy5))

        SolarTime = (hour*60.0) + minute + (second/60.0) + (Et - 4.0 * -lon + (offset*60.0))

        while SolarTime > 1440.0:
            SolarTime -= 1440.0
        HourAngle = SolarTime / 4.0 - 180.0
        if HourAngle < -180.0:
            HourAngle += 360.0

        Dummy = sin(toRadians*lat) * sin(toRadians*Declination) + cos(toRadians*lat) * cos(toRadians*Declination) * cos(toRadians*HourAngle)
        if Dummy > 1.0:
            Dummy = 1.0
        elif Dummy < -1.0:
            Dummy = -1.0

        Zenith = toDegrees*(acos(Dummy))
        Dummy = cos(toRadians*lat) * sin(toRadians*Zenith)
        if abs(Dummy) >= 0.000999:
            Azimuth = (sin(toRadians*lat) * cos(toRadians*Zenith) - sin(toRadians*Declination)) / Dummy
            if abs(Azimuth) > 1.0:
                if Azimuth < 0:
                    Azimuth = -1.0
                else:
                    Azimuth = 1.0

            Azimuth = 180 - toDegrees*(acos(Azimuth))
            if HourAngle > 0:
                Azimuth *= -1.0
        else:
            if lat > 0:
                Azimuth = 180.0
            else:
                Azimuth = 0.0
        if Azimuth < 0:
            Azimuth += 360.0

        AtmElevation = 90 - Zenith
        if AtmElevation > 85:
            RefractionCorrection = 0
        else:
            Dummy = tan(toRadians*(AtmElevation))
            if AtmElevation > 5:
                RefractionCorrection = 58.1 / Dummy - 0.07 / pow(Dummy,3) + 0.000086 / pow(Dummy,5)
            elif AtmElevation > -0.575:
                RefractionCorrection = 1735 + AtmElevation * (-518.2 + AtmElevation * (103.4 + AtmElevation * (-12.79 + AtmElevation * 0.711)))
            else:
                RefractionCorrection = -20.774 / Dummy
            RefractionCorrection = RefractionCorrection / 3600

        Zenith = Zenith - RefractionCorrection
        Altitude = 90 - Zenith
        Daytime = 0
        if Altitude > 0.0:
                Daytime = 1

        dir = bisect.bisect((0.0,67.5,112.5,157.5,202.5,247.5,292.5),Azimuth)-1

        return Altitude, Zenith, Daytime, dir


    def GetStreamGeometry(self, Q_est, W_b, z, n, S, D_est, dx, dt):
        pass

    def CalcMuskingum(self, Q_est, U, W_w, S, dx, dt):
        """Return the values for the Muskigum routing coefficients
        using current timestep and optional discharge"""
        #Calculate an initial geometry based on an estimated discharge (typically (t,x-1))
        # Taken from the VB source.
        c_k = (5/3) * U  # Wave celerity
        X = 0.5 * (1 - Q_est / (W_w * S * dx * c_k))
        if X > 0.5: X = 0.5
        elif X < 0.0: X = 0.0
        K = dx / c_k
        dt = dt

        # Check the celerity to ensure stability. These tests are from the VB code.
        if dt >= (2 * K * (1 - X)):  #Unstable - Decrease dt or increase dx
            raise Exception("Unstable timestep. K=%0.3f, X=%0.3f, tests=(%0.3f, %0.3f)" % (K,X,test0,test1))

        # These calculations are from Chow's "Applied Hydrology"
        D = K * (1 - X) + 0.5 * dt
        C1 = (0.5*dt - K * X) / D
        C2 = (0.5*dt + K * X) / D
        C3 = (K * (1 - X) - 0.5*dt) / D
        # TODO: reformulate this using an updated model, such as Moramarco, et.al., 2006
        return C1, C2, C3

    def CalcFlows(self, U, W_w, W_b, S, dx, dt, z, n, D_est, Q, Q_up, Q_up_prev, inputs, Q_bc):
        pass

    def GetSolarFlux(self, hour, JD, Altitude, Zenith, cloud, d_w, W_b, Elevation, TopoFactor,
                     ViewToSky, SampleDist, phi, emergent, VDensity, VHeight, rip, veg,
                     FullSunAngle, TopoShadeAngle, BankShadeAngle):
        """Old method, now pushed down to a C module. This is left for testing only"""
        F_Direct = [0]*8
        F_Diffuse = [0]*8
        F_Solar = [0]*8
        Cloud = self.ContData[bc_hour][0]
        FullSunAngle,TopoShadeAngle,BankShadeAngle,RipExtinction,VegetationAngle = self.ShaderList[dir]
        # Make all math functions local to save time by preventing failed searches of local, class and global namespaces
        #======================================================
        # 0 - Edge of atmosphere
        # TODO: Original VB code's JulianDay calculation:
        # JulianDay = -DateDiff("d", theTime, DateSerial(year(theTime), 1, 1))
        # THis calculation for Rad_Vec should be checked, with respect to the DST hour/24 part.
        Rad_Vec = 1 + 0.017 * cos((2 * pi / 365) * (186 - JD + hour / 24))
        Solar_Constant = 1367 #W/m2
        F_Direct[0] = (Solar_Constant / (Rad_Vec ** 2)) * sin(radians(Altitude)) #Global Direct Solar Radiation
        F_Diffuse[0] = 0
        ########################################################
        #======================================================
        # 1 - Above Topography
        Air_Mass = (35 / sqrt(1224 * sin(radians(Altitude)) + 1)) * \
            exp(-0.0001184 * self.Elevation)
        Trans_Air = 0.0685 * cos((2 * pi / 365) * (JD + 10)) + 0.8
        #Calculate Diffuse Fraction
        F_Direct[1] = F_Direct[0] * (Trans_Air ** Air_Mass) * (1 - 0.65 * Cloud ** 2)
        if F_Direct[0] == 0:
            Clearness_Index = 1
        else:
            Clearness_Index = F_Direct[1] / F_Direct[0]

        Dummy = F_Direct[1]
        Diffuse_Fraction = (0.938 + 1.071 * Clearness_Index) - \
            (5.14 * (Clearness_Index ** 2)) + \
            (2.98 * (Clearness_Index ** 3)) - \
            (sin(2 * pi * (JD - 40) / 365)) * \
            (0.009 - 0.078 * Clearness_Index)
        F_Direct[1] = Dummy * (1 - Diffuse_Fraction)
        F_Diffuse[1] = Dummy * (Diffuse_Fraction) * (1 - 0.65 * Cloud ** 2)

        ########################################################
        #======================================================
        #2 - Above Land Cover
        # Empty
        ########################################################
        #======================================================
        #3 - Above Stream Surface (Above Bank Shade)
        if Altitude <= TopoShadeAngle:    #>Topographic Shade IS Occurring<
            F_Direct[2] = 0
            F_Diffuse[2] = F_Diffuse[1] * self.TopoFactor
            F_Direct[3] = 0
            F_Diffuse[3] = F_Diffuse[2] * self.ViewToSky
        elif Altitude < FullSunAngle:  #Partial shade from veg
            F_Direct[2] = F_Direct[1]
            F_Diffuse[2] = F_Diffuse[1] * (1 - self.TopoFactor)
            Dummy1 = F_Direct[2]
            zone = 0
            for vegangle in VegetationAngle:  #Loop to find if shading is occuring from veg. in that zone
                if Altitude < vegangle:  #veg shading is occurring from this zone
                    Dummy1 *= (1-(1-exp(-1* RipExtinction[zone] * (IniParams["longsample"]/cos(radians(Altitude))))))
                zone += 1
            F_Direct[3] = Dummy1
            F_Diffuse[3] = F_Diffuse[2] * self.ViewToSky
        else: # Full sun
            F_Direct[2] = F_Direct[1]
            F_Diffuse[2] = F_Diffuse[1] * (1 - self.TopoFactor)
            F_Direct[3] = F_Direct[2]
            F_Diffuse[3] = F_Diffuse[2] * self.ViewToSky
        #4 - Above Stream Surface (What a Solar Pathfinder measures)
        #Account for bank shade
        if Altitude > TopoShadeAngle and Altitude <= BankShadeAngle:  #Bank shade is occurring
            F_Direct[4] = 0
            F_Diffuse[4] = F_Diffuse[3]
        else:  #bank shade is not occurring
            F_Direct[4] = F_Direct[3]
            F_Diffuse[4] = F_Diffuse[3]

        #Account for emergent vegetation
        if IniParams["emergent"]:
            pathEmergent = self.VHeight / sin(radians(Altitude))
            if pathEmergent > self.W_b:
                pathEmergent = self.W_b
            if self.VDensity == 1:
                self.VDensity = 0.9999
                ripExtinctEmergent = 1
                shadeDensityEmergent = 1
            elif self.VDensity == 0:
                self.VDensity = 0.00001
                ripExtinctEmergent = 0
                shadeDensityEmergent = 0
            else:
                ripExtinctEmergent = -log(1 - self.VDensity) / 10
                shadeDensityEmergent = 1 - exp(-ripExtinctEmergent * pathEmergent)
            F_Direct[4] = F_Direct[4] * (1 - shadeDensityEmergent)
            if self.VHeight: # if there's no VHeight, we get ZeroDivisionError because we don't need this next step
                pathEmergent = self.VHeight
                ripExtinctEmergent = -log(1 - self.VDensity) / self.VHeight
                shadeDensityEmergent = 1 - exp(-ripExtinctEmergent * pathEmergent)
                F_Diffuse[4] = F_Diffuse[4] * (1 - shadeDensityEmergent)

        #:::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        #5 - Entering Stream
        if Zenith > 80:
            Stream_Reflect = 0.0515 * (Zenith) - 3.636
        else:
            Stream_Reflect = 0.091 * (1 / cos(Zenith * pi / 180)) - 0.0386
        if abs(Stream_Reflect) > 1:
            Stream_Reflect = 0.0515 * (Zenith * pi / 180) - 3.636
        if abs(Stream_Reflect) > 1:
            Stream_Reflect = 0.091 * (1 / self.cos(Zenith * pi / 180)) - 0.0386
        F_Diffuse[5] = F_Diffuse[4] * 0.91
        F_Direct[5] = F_Direct[4] * (1 - Stream_Reflect)
        #:::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        #6 - Received by Water Column
        #=========================================================
        #:::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        #7 - Received by Bed
        Water_Path = self.d_w / cos(atan((sin(radians(Zenith)) / 1.3333) / sqrt(-(sin(radians(Zenith)) / 1.3333) * (sin(radians(Zenith)) / 1.3333) + 1)))         #Jerlov (1976)
        Trans_Stream = 0.415 - (0.194 * log10(Water_Path * 100))
        if Trans_Stream > 1:
            Trans_Stream = 1
        Dummy1 = F_Direct[5] * (1 - Trans_Stream)       #Direct Solar Radiation attenuated on way down
        Dummy2 = F_Direct[5] - Dummy1                   #Direct Solar Radiation Hitting Stream bed
        Bed_Reflect = exp(0.0214 * (Zenith * pi / 180) - 1.941)   #Reflection Coef. for Direct Solar
        BedRock = 1 - self.phi
        Dummy3 = Dummy2 * (1 - Bed_Reflect)                #Direct Solar Radiation Absorbed in Bed
        Dummy4 = 0.53 * BedRock * Dummy3                   #Direct Solar Radiation Immediately Returned to Water Column as Heat
        Dummy5 = Dummy2 * Bed_Reflect                      #Direct Solar Radiation Reflected off Bed
        Dummy6 = Dummy5 * (1 - Trans_Stream)               #Direct Solar Radiation attenuated on way up
        F_Direct[6] = Dummy1 + Dummy4 + Dummy6
        F_Direct[7] = Dummy3 - Dummy4
        Trans_Stream = 0.415 - (0.194 * log10(100 * self.d_w))
        if Trans_Stream > 1:
            Trans_Stream = 1
        Dummy1 = F_Diffuse[5] * (1 - Trans_Stream)      #Diffuse Solar Radiation attenuated on way down
        Dummy2 = F_Diffuse[5] - Dummy1                  #Diffuse Solar Radiation Hitting Stream bed
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # TODO: The following ALWAYS becomes exp(-1.941)
        Bed_Reflect = exp(0.0214 * (0) - 1.941)               #Reflection Coef. for Diffuse Solar
        Dummy3 = Dummy2 * (1 - Bed_Reflect)                #Diffuse Solar Radiation Absorbed in Bed
        Dummy4 = 0.53 * BedRock * Dummy3                   #Diffuse Solar Radiation Immediately Returned to Water Column as Heat
        Dummy5 = Dummy2 * Bed_Reflect                      #Diffuse Solar Radiation Reflected off Bed
        Dummy6 = Dummy5 * (1 - Trans_Stream)               #Diffuse Solar Radiation attenuated on way up
        F_Diffuse[6] = Dummy1 + Dummy4 + Dummy6
        F_Diffuse[7] = Dummy3 - Dummy4
        #=========================================================
#        '   Flux_Solar(x) and Flux_Diffuse = Solar flux at various positions
#        '       0 - Edge of atmosphere
#        '       1 - Above Topography
#        '       2 - Above Land Cover
#        '       3 - Above Stream (After Land Cover Shade)
#        '       4 - Above Stream (What a Solar Pathfinder Measures)
#        '       5 - Entering Stream
#        '       6 - Received by Water Column
#        '       7 - Received by Bed
        F_Solar[0] = F_Diffuse[0] + F_Direct[0]
        F_Solar[1] = F_Diffuse[1] + F_Direct[1]
        F_Solar[2] = F_Diffuse[2] + F_Direct[2]
        F_Solar[3] = F_Diffuse[3] + F_Direct[3]
        F_Solar[4] = F_Diffuse[4] + F_Direct[4]
        F_Solar[5] = F_Diffuse[5] + F_Direct[5]
        F_Solar[6] = F_Diffuse[6] + F_Direct[6]
        F_Solar[7] = F_Diffuse[7] + F_Direct[7]
        return F_Solar



    def GetGroundFluxes(self, Cloud, Wind, Humidity, T_air, Elevation, phi, VHeight, ViewToSky, SedDepth, dx,
                        dt, SedThermCond, SedThermDiff, FAlluvium, P_w, W_w, emergent, penman, wind_a,
                        wind_b, calcevap, T_prev, T_sed, Q_hyp, F_Solar5, F_Solar7):
        from math import exp
        #SedThermCond units of W/(m *C)
        #SedThermDiff units of cm^2/sec

        SedRhoCp = self.SedThermCond / (self.SedThermDiff / 10000)
        #NOTE: SedRhoCp is the product of sediment density and heat capacity
        #since thermal conductivity is defined as density * heat capacity * diffusivity,
        #therefore (density * heat capacity) = (conductivity / diffusivity)  units of (J / m3 / *C)

        #Water Variable
        rhow = 1000                             #density of water kg / m3
        H2O_HeatCapacity = 4187                 #J/(kg *C)

        #Conduction flux (positive is heat into stream)
        F_Cond = self.SedThermCond * (self.T_sed - self.T_prev) / (self.SedDepth / 2)             #units of (W / m2)
        #Calculate the conduction flux between deeper alluvium & substrate
        if IniParams["calcalluvium"]:
            Flux_Conduction_Alluvium = self.SedThermCond * (self.T_sed - self.T_alluv) / (self.SedDepth / 2)
        else:
            Flux_Conduction_Alluvium = 0

        #Hyporheic flux (negative is heat into sediment)
        F_hyp = self.Q_hyp * rhow * H2O_HeatCapacity * (self.T_sed - self.T_prev) / (self.W_w * self.dx)

        NetFlux_Sed = self.F_Solar[7] - F_Cond - Flux_Conduction_Alluvium - F_hyp
        DT_Sed = NetFlux_Sed * self.dt / (self.SedDepth * SedRhoCp)
        T_sed_new = self.T_sed + DT_Sed
        if T_sed_new > 50 or T_sed_new < 0:
            raise Exception("Sediment temperature not bounded in 0<=temp<=50")

        #=====================================================
        #Calculate Longwave FLUX
        #=====================================================
        #Atmospheric variables
        Cloud, Wind, Humidity, Air_T = self.ContData[bc_hour]
        Sat_Vapor = 6.1275 * exp(17.27 * Air_T / (237.3 + Air_T)) #mbar (Chapra p. 567)
        Air_Vapor = Humidity * Sat_Vapor
        Sigma = 5.67e-8 #Stefan-Boltzmann constant (W/m2 K4)
        Emissivity = 1.72 * (((Air_Vapor * 0.1) / (273.2 + Air_T)) ** (1 / 7)) * (1 + 0.22 * Cloud ** 2) #Dingman p 282
        #======================================================
        #Calcualte the atmospheric longwave flux
        F_LW_Atm = 0.96 * self.ViewToSky * Emissivity * Sigma * (Air_T + 273.2) ** 4
        #Calcualte the backradiation longwave flux
        F_LW_Stream = -0.96 * Sigma * (self.T_prev + 273.2) ** 4
        #Calcualte the vegetation longwave flux
        F_LW_Veg = 0.96 * (1 - self.ViewToSky) * 0.96 * Sigma * (Air_T + 273.2) ** 4
        #Calcualte the net longwave flux
        F_Longwave = F_LW_Atm + F_LW_Stream + F_LW_Veg

        #===================================================
        #Calculate Evaporation FLUX
        #===================================================
        #Atmospheric Variables
        Pressure = 1013 - 0.1055 * self.Elevation #mbar
        Sat_Vapor = 6.1275 * exp(17.27 * self.T_prev / (237.3 + self.T_prev)) #mbar (Chapra p. 567)
        Air_Vapor = Humidity * Sat_Vapor
        #===================================================
        #Calculate the frictional reduction in wind velocity
        if IniParams["emergent"] and self.VHeight > 0:
            Zd = 0.7 * self.VHeight
            Zo = 0.1 * self.VHeight
            Zm = 2
            Friction_Velocity = Wind * 0.4 / log((Zm - Zd) / Zo) #Vertical Wind Decay Rate (Dingman p. 594)
        else:
            Zo = 0.00023 #Brustsaert (1982) p. 277 Dingman
            Zd = 0 #Brustsaert (1982) p. 277 Dingman
            Zm = 2
            Friction_Velocity = Wind
        #===================================================
        #Wind Function f(w)
        Wind_Function = float(IniParams["wind_a"]) + float(IniParams["wind_b"]) * Friction_Velocity #m/mbar/s
#        Wind_Function = 0.000000001505 + 0.0000000016 * Friction_Velocity #m/mbar/s

        #===================================================
        #Latent Heat of Vaporization
        LHV = 1000 * (2501.4 + (1.83 * self.T_prev)) #J/kg
        #===================================================
        #Use Jobson Wind Function
        if IniParams["penman"]:
            #Calculate Evaporation FLUX
            P = 998.2 # kg/m3
            Gamma = 1003.5 * Pressure / (LHV * 0.62198) #mb/*C  Cuenca p 141
            Delta = 6.1275 * exp(17.27 * Air_T / (237.3 + Air_T)) - 6.1275 * exp(17.27 * (Air_T - 1) / (237.3 + Air_T - 1))
            NetRadiation = self.F_Solar[5] + F_Longwave  #J/m2/s
            if NetRadiation < 0:
                NetRadiation = 0 #J/m2/s
            Ea = Wind_Function * (Sat_Vapor - Air_Vapor)  #m/s
            Evap_Rate = ((NetRadiation * Delta / (P * LHV)) + Ea * Gamma) / (Delta + Gamma)
            F_Evap = -Evap_Rate * LHV * P #W/m2
            #Calculate Convection FLUX
            Bowen = Gamma * (self.T_prev - Air_T) / (Sat_Vapor - Air_Vapor)
        else:
            #===================================================
            #Calculate Evaporation FLUX
            Evap_Rate = Wind_Function * (Sat_Vapor - Air_Vapor)  #m/s
            P = 998.2 # kg/m3
            F_Evap = -Evap_Rate * LHV * P #W/m2
            #Calculate Convection FLUX
            if (Sat_Vapor - Air_Vapor) <> 0:
                Bowen = 0.61 * (Pressure / 1000) * (self.T_prev - Air_T) / (Sat_Vapor - Air_Vapor)
            else:
                Bowen = 1
            F_Conv = F_Evap * Bowen
        F_Conv = F_Evap * Bowen
        E = Evap_Rate*self.W_w if IniParams["calcevap"] else 0
        return F_Cond, T_sed_new, F_Longwave, F_LW_Atm, F_LW_Stream, F_LW_Veg, F_Evap, F_Conv, E



    def MacCormick(self, dt, dx, U, T_sed, T_prev, Q_hyp, Q_tup, T_tup, Q_up, Delta_T, Disp, S1, S1_value,
                   T0, T1, T2, Q_accr, T_accr):
        pass

    def CalcMacCormick(self, dt, dx, U, T_sed, T_prev, Q_hyp, Q_tup, T_tup, Q_up, Delta_T, Disp, S1,
                       S1_value, T0, T1, T2, Q_accr, T_accr):
        pass

    def CalcHeatFluxes(self, ContData, C_args, d_w, area, P_w, W_w, U, Q_tribs, T_tribs, T_alluv, T_prev,
                       T_sed, Q_hyp, T_dn_prev, ShaderList, Disp, hour, JD, daytime, Altitude, Zenith,
                       Q_up_prev, T_up_prev):
        pass



