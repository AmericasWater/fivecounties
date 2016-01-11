# -*- coding: utf-8 -*-
### Industry component
## Optimizes the amount of water and fuel to industry
## Simulates manufacturing as a Cobb-Douglas of water and energy
## The partial objective sells all of the manufactured good on the market
## The sole objective includes the cost of fossil fuels
## Call as `python industry.py` to optimize usage with only industry

import pandas
import numpy as np
import lib

# Load county data for parameters
county_data= pandas.read_csv('ComplexData.csv')

#################### GLOBAL PARAMETERS #####################
N= len(county_data['county']) # number of counties
p_mn = 1 # world price of the manufactured good (normalized to 1)

Area = list(county_data['co_area']) # total land area of the county, sq.km.
alpha= list(county_data['ag_area']/county_data['co_area'])  # fraction of land used for agriculture
W_surf= list(county_data['water_cap']) # total water rights (i.e. max water drawn from river)
eta = list(county_data['eta'])  # elasticity of commercial output with respect to energy
    # (i.e., exponent of energy resource in commercial production function)

production_scaling = 1e-2

def generate():
    # commercial water demand, liters per sq.km. per year
    lambda_Cs = np.random.uniform(0, 1, N) * np.array(W_surf) / ((1 - np.array(alpha)) * np.array(Area))

    # commercial energy demand, liters per sq.km. per year, avg for US is 500
    sigma_Cs = np.random.uniform(0, 1000, N)

    return lambda_Cs.tolist() + sigma_Cs.tolist()

def simulate_county(lambda_C, sigma_C, county):
    """Simulates manufacturing as a Cobb-Douglas of water and energy."""
    Water_Draw = lambda_C * (1 - alpha[county]) * Area[county]
    Mfct_good = production_scaling * (1 - alpha[county]) * Area[county] * (sigma_C ** eta[county]) * (lambda_C ** (1-eta[county]))
    Energy_D = (sigma_C * (1 - alpha[county]) * (Area[county]))

    return Water_Draw, Mfct_good, Energy_D

def simulate_all(lambda_Cs, sigma_Cs):
    Water_Draws = []
    Mfct_goods = []
    Energy_Ds = []

    for county in range(N):
        Water_Draw, Mfct_good, Energy_D = simulate_county(lambda_Cs[county], sigma_Cs[county], county)

        Water_Draws.append(Water_Draw)
        Mfct_goods.append(Mfct_good)
        Energy_Ds.append(Energy_D)

    return Water_Draws, Mfct_goods, Energy_Ds

def partial_objective(Mfct_goods):
    total = 0
    for county in range(N):
        total += Mfct_goods[county] * p_mn

    return total

def sole_objective(params):
    """Partial objective, plus the cost of fossil fuels."""
    lambda_Cs = params[0:N]
    sigma_Cs = params[N:2*N]

    Water_Draws, Mfct_goods, Energy_Ds = simulate_all(lambda_Cs, sigma_Cs)

    return partial_objective(Mfct_goods) - sum(Energy_Ds)*lib.p_E

bounds = [(0, W_surf[county] / ((1 - alpha[county]) * Area[county])) for county in range(N)] + [(0, None)] * N

if __name__ == '__main__':
    result = lib.maximize(sole_objective, generate, bounds)
    print result

    print bounds
