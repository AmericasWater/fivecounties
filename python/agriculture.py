# -*- coding: utf-8 -*-
### Agriculture component
## Simulates crop yields as a Cobb-Douglas model of water and energy
## Defines a partial objective of satisfying food demand and selling excess
## Sole objective includes cost of energy
## Run as `python agriculture.py` to just optimize yields

import pandas
import numpy as np
import lib

## Yields in US: 7000 kg / Ha * 1 Ha / .01 km = 700000 kg / km^2
## All else producing results around 100000, so
yield_scaling = 5

# Load county data for parameters
county_data = pandas.read_csv('ComplexData.csv')
#county_data = county_data[0:1]

#################### GLOBAL PARAMETERS #####################
N = len(county_data['county']) # number of counties
f_p = 250 # average food demand, kg of corn per person per year
    # derivation: (2500 kcal/day)*(365 day/year)/(3650 kcal/kg of corn)

# Elasticities for production functions (unitless)
delta = 0.6 # elasticity of crop production (corn) with respect to land
    # (i.e., exponent of land resource in agricultural production function
gamma = 0.3 # elasticity of crop production (corn) with respect to energy
    # (i.e., exponent of land resource in agricultural production function)

p_F = 0.25  # the global price of food (per kg of corn)

########## COUNTY PARAMETERS- INITIAL CONDITIONS ###########
# Demographics
P= list(county_data['population']) # population

# Land Use and Resources
Area = list(county_data['co_area']) # total land area of the county, sq.km.
alpha= list(county_data['ag_area']/county_data['co_area'])  # fraction of land used for agriculture
theta= list(county_data['soil']) # local soil productivity, unitless
W_surf= list(county_data['water_cap']) # total water rights (i.e. max water drawn from river)

def generate():
    # agricutural water demand, liters per sq.km. per year, avg for US is 500
    # 197e9 m^3 = 1.97e14 liters, / 1.78871e6 km^2 = 110135237 average
    # But there's not that much available, so do as fraction of available
    lambda_As = np.random.uniform(0, 1, N) * np.array(W_surf) / (np.array(alpha) * np.array(Area))

    # agricutural energy demand, kilowatt-hours per sq.km. per year
    # from US total food production taking 14.4 - (4.1 + 1.7)% = 95.058 * .086 qd Btu = 2.39585248e12 kWh
    # Agricultural land of 442 million acres = 1.78871e6 km^2
    # So 1339430 kWh / km^2
    sigma_As = np.random.uniform(0, 3e6, N)

    return lambda_As.tolist() + sigma_As.tolist()

def simulate_county(lambda_A, sigma_A, beta, county):
    """Simulates crop yields as a Cobb-Douglas model of water and energy."""
    Crop_yield = yield_scaling * alpha[county] * Area[county] * (((theta[county]) ** (delta)) * ((sigma_A) ** (gamma)) * ((lambda_A) ** (1 - delta - gamma)))   # in kg corn

    Food_S = (1 - beta) * Crop_yield    # in kg corn
    Food_D = P[county] * f_p         # in kg corn

    Water_Draw = lambda_A * alpha[county] * Area[county]
    Energy_D = sigma_A * alpha[county] * Area[county]

    return Crop_yield, Food_S, Food_D, Water_Draw, Energy_D

def simulate_all(lambda_As, sigma_As, betas):
    Crop_yields = []
    Food_Ss = []
    Food_Ds = []

    Water_Draws = []
    Energy_Ds = []

    for county in range(N):
        Crop_yield, Food_S, Food_D, Water_Draw, Energy_D = \
            simulate_county(lambda_As[county], sigma_As[county], betas[county], county)

        Crop_yields.append(Crop_yield)
        Food_Ss.append(Food_S)
        Food_Ds.append(Food_D)
        Water_Draws.append(Water_Draw)
        Energy_Ds.append(Energy_D)

    return Crop_yields, Food_Ss, Food_Ds, Water_Draws, Energy_Ds

def partial_objective(Food_Ss, Food_Ds):
    """Objective of satisfying food demand and selling excess."""
    total = 0
    for county in range(N):
        if Food_Ss[county] > Food_Ds[county]:
            total += (Food_Ss[county] - Food_Ds[county])*p_F / lib.markup
        else:
            total += (Food_Ss[county] - Food_Ds[county])*p_F

    return total

def sole_objective(params, betas):
    """Partial objective, plus cost of energy."""
    lambda_As = params[0:N]
    sigma_As = params[N:2*N]

    Crop_yields, Food_Ss, Food_Ds, Water_Draws, Energy_Ds = simulate_all(lambda_As, sigma_As, betas)

    return partial_objective(Food_Ss, Food_Ds) - sum(Energy_Ds)*lib.p_E

# Cannot use more water than available, but may use any amount of nergy
bounds = [(0, W_surf[county] / (alpha[county] * Area[county])) for county in range(N)] + \
         [(0, None)] * N

if __name__ == '__main__':
    betas = [0.5] * 5

    result = lib.maximize(sole_objective, generate, bounds, args=(betas,))
    print result

    Crop_yields, Food_Ss, Food_Ds, Water_Draws, Energy_Ds = simulate_all(result['x'][0:N], result['x'][N:2*N], betas)
    print np.mean(Crop_yields)


