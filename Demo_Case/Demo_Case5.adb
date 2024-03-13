tdb: empty
adb: Demo_Case5
problem: Demo_Case5
description:
# Demo_Case5
# Environment regulations
# Counting the SO2 emissions from fossil fuel power plants
# Introducing renewable energy technology
# 
# Country_A
drate: 6.0
timesteps: 2000 2002 2005 2010 2015 2020 2025 2030
loadregions:
ltype	ordered seasonal 1 0
year	2002 1 11
name	 aaa aab aac \
	 aba abb \
	 baa bab bac \
	 bba bbb caa
length	 0.035342 0.176712 0.141370 \
	 0.085479 0.056986 \
	 0.007123 0.035616 0.028493 \
	 0.016438 0.010959 0.405479
energyforms:
Final f
# Final Energy Level
    Oil o  
    # 
    Electricity e l 
    # 
*
Secondary s
# Secondary Energy Level
    Electricity e l 
    # 
    Oil o  
    # 
*
Primary p
# Primary Energy Level
    Coal c  
    # 
    Oil o  
    # 
*
Resources r
# Resource Energy Level
    Coal c  
    # 
*
demand:
e-f cg 200 1.05
o-f c 50
loadcurve:
year 2002
e-f 0.058520 0.199658 0.086059 0.080945 0.034691 \
    0.014183 0.055640 0.039276 0.009669 0.011817 0.410000
relations2.1river.1riv.inflow 0.035342 0.176712 0.141370 0.085479 0.056986 \
    0.007123 0.035616 0.028493 0.016438 0.010959 0.405479
relations2.2river.2riv.inflow 0.035342 0.176712 0.141370 0.085479 0.056986 \
    0.007123 0.035616 0.028493 0.016438 0.010959 0.405479
relations2.1river.1riv.upper 0.035342 0.176712 0.141370 0.085479 0.056986 \
    0.007123 0.035616 0.028493 0.016438 0.010959 0.405479
relations2.1river.1riv.lower 0.035342 0.176712 0.141370 0.085479 0.056986 \
    0.007123 0.035616 0.028493 0.016438 0.010959 0.405479
relations2.2river.2riv.upper 0.035342 0.176712 0.141370 0.085479 0.056986 \
    0.007123 0.035616 0.028493 0.016438 0.010959 0.405479
relations2.2river.2riv.lower 0.035342 0.176712 0.141370 0.085479 0.056986 \
    0.007123 0.035616 0.028493 0.016438 0.010959 0.405479
relationsc:
relationsp:
relationss:
1stor 1sto o 0
    units	type: energy, cost:US$'00/kWyr, inv:US$'00/kW, fom:US$'00/kW/yr, pll:yr, cmix:MW, hisccap:MW, ctime:yr, reten:yr, retenhist:MWyr, upper:MWyr, lower:MWyr, transfac:%
    fyear	2010
    for_ldr	all
    upper	c 60
    lower	c 0
    stortype	continuous
    type	hydro
    inflow	p1riv	c 1
    overflow	pnone	c 1.
*
2stor 2sto o 0
    units	type: energy, cost:US$'00/kWyr, inv:US$'00/kW, fom:US$'00/kW/yr, pll:yr, cmix:MW, hisccap:MW, ctime:yr, reten:yr, retenhist:MWyr, upper:MWyr, lower:MWyr, transfac:%
    fyear	2010
    for_ldr	all
    upper	c 120
    lower	c 0
    stortype	continuous
    type	hydro
    inflow	p2riv	c 1
    overflow	pnone	c 1.
*
relations1:
SO2 SO2 o
    units	group: activity, type: weight, cost:US$'00/ton, upper:kton, lower:kton
    for_ldr	none
    upper	c 25
    type	None
*
relations2:
1river 1riv o 0
    units	group: activity, type: energy, cost:US$'00/kWyr, upper:MWyr, lower:MWyr
    for_ldr	all
    lower	c 0
    type	river
    inflow	pnatural	c 160
    outflow	pnatural	c 1
*
2river 2riv o 0
    units	group: activity, type: energy, cost:US$'00/kWyr, upper:MWyr, lower:MWyr
    for_ldr	all
    lower	c 0
    type	river
    inflow	pnatural	c 80
    outflow	pnatural	c 1
*
variables:
systems:
Coal_Extr a
    minp	c-r 1.
    moutp	c-p c 1
    vom	c 48
# 
*
Oil_Imp a
    moutp	o-p c 1
    vom	ts 110 248
    bda up	c 125
# 
*
Oil_P_S a
    minp	o-p 1.
    moutp	o-s c 1
# 
*
Coal_PP a
    minp	c-p 1.
    moutp	e-s c 0.36
    plf	c 0.80
    pll	c 17
    inv	c 1000.0
    fom	c 30.0
    vom	c 25
    hisc	0.	hc 1991 200 1996 200
    ctime	c 4.0
    bdi up	c 400
    con1a SO2	c 0.089
# 
*
Oil_PP a
    minp	o-s 1.
    moutp	e-s c .38
    plf	c .8
    pll	c 30
    inv	c 600
    fom	c 10
    vom	c 20
    hisc	0.	hc 1990 100 1995 125
    ctime	c 3
    con1a SO2	c 0.039
*
Oil_S_F a
    minp	o-s 1.
    moutp	o-f c 1
# 
*
Ele_TD a
    minp	e-s 1.
    moutp	e-f c .8
    inv	c 1000.0
    fom	c 10.0
    hisc	0.	hc 1995 600.0
# 
*
Hyd1 a
    moutp	e-s c 1
    inv	c 1200
    fom	c 20
    vom	c 2
    bdc up	ts 0 100
    con2a 2riv	c 1
    consa 1sto	c -1
# 
*
Hyd2 b
    moutp	e-s c 1
    inv	c 1500
    fom	c 25
    vom	c 2
    bdc up	ts 0 100
    consa 2sto	c -1
# 
*
Renewable R
    moutp	e-s c 1
    plf	c 0.8
    pll	c 20
    inv	ts 1800 1800 1600 1500
    fom	c 5
    vom	c 2
    optm	c 0.2
    bdc up	cg 10 1.04
# 
*
resources:
fuel c-r
# Coal/Resources
    grade a
        volume	929338.
*
endata
