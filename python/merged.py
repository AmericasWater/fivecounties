# -*- coding: utf-8 -*-
### Merging of all components
## Simulates all components and combines all partial objectives
##
## The optimization constraints are that water draws in each county
## are not more than their rights, and that across all counties energy
## supplied exceeds energy demand.
##
## For a sample optimization, run `python merged.py`.


import pandas
import numpy as np
from scipy import optimize
import lib, agriculture, biofuel, industry, fossil

# Load county data for parameters
county_data= pandas.read_csv('ComplexData.csv')

#################### GLOBAL PARAMETERS #####################
N= len(county_data['county']) # number of counties

# Average Water Demand (liters per ...)
lambda_p= 31382  # residential, per person per year
# 365.25 * 27.4 billion gallons / 318.9e6 people

# Average Energy Demand (Kilowatt-Hours per...)
sigma_p= 10908 # residential, per person per year
# http://www.eia.gov/tools/faqs/faq.cfm?id=97&t=3

########## COUNTY PARAMETERS- INITIAL CONDITIONS ###########
# Demographics
P= list(county_data['population']) # population

# Land Use and Resources
Area = list(county_data['co_area']) # total land area of the county, sq.km.
alpha= list(county_data['ag_area']/county_data['co_area'])  # fraction of land used for agriculture
W_surf= list(county_data['water_cap']) # total water rights (i.e. max water drawn from river)
sigma_w = list(county_data['sigma_w'])

def generate():
    betas = biofuel.generate()
    phis = fossil.generate()
    lambda_sigma_As = agriculture.generate()
    lambda_sigma_Cs = industry.generate()

    return betas + phis + lambda_sigma_As + lambda_sigma_Cs

def simulate_county(beta, phi, lambda_A, sigma_A, lambda_C, sigma_C, county):
    Crop_yield, Food_S, Food_D, Water_Draw_agriculture, Energy_D_agriculture = agriculture.simulate_county(lambda_A, sigma_A, beta, county)
    Biofuel_Stock, Biofuel_E, Water_Draw_biofuel = biofuel.simulate_county(beta, Crop_yield)
    Water_Draw_industry, Mfct_good, Energy_D_industry = industry.simulate_county(lambda_C, sigma_C, county)
    Fossil_E, Water_Draw_fossil = fossil.simulate_county(phi)

    Water_Draw = P[county] * lambda_p + Water_Draw_agriculture + Water_Draw_industry + Water_Draw_biofuel + Water_Draw_fossil

    Energy_D = (P[county] * sigma_p) + Energy_D_agriculture + Energy_D_industry + (sigma_w[county] * Water_Draw)
    Energy_S = Biofuel_E + Fossil_E

    return Crop_yield, Food_S, Food_D, Biofuel_Stock, Biofuel_E, \
        Water_Draw, Energy_S, Energy_D, Mfct_good

def get_parameters(params):
    betas = params[0:N]
    phis = params[N:2*N]
    lambda_As = params[2*N:3*N]
    sigma_As = params[3*N:4*N]
    lambda_Cs = params[4*N:5*N]
    sigma_Cs = params[5*N:6*N]

    return betas, phis, lambda_As, sigma_As, lambda_Cs, sigma_Cs

def simulate_all(params):
    betas, phis, lambda_As, sigma_As, lambda_Cs, sigma_Cs = get_parameters(params)

    Crop_yields = []
    Food_Ss = []
    Food_Ds = []
    Biofuel_Stocks = []
    Biofuel_Es = []
    Water_Draws = []
    Energy_Ss = []
    Energy_Ds = []
    Mfct_goods = []

    for county in range(N):
        Crop_yield, Food_S, Food_D, Biofuel_Stock, Biofuel_E, \
            Water_Draw, Energy_S, Energy_D, Mfct_good = \
            simulate_county(betas[county], phis[county], lambda_As[county], \
                            sigma_As[county], lambda_Cs[county], \
                            sigma_Cs[county], county)

        Crop_yields.append(Crop_yield)
        Food_Ss.append(Food_S)
        Food_Ds.append(Food_D)
        Biofuel_Stocks.append(Biofuel_Stock)
        Biofuel_Es.append(Biofuel_E)
        Water_Draws.append(Water_Draw)
        Energy_Ss.append(Energy_S)
        Energy_Ds.append(Energy_D)
        Mfct_goods.append(Mfct_good)

    return Crop_yields, Food_Ss, Food_Ds, Biofuel_Stocks, Biofuel_Es, \
        Water_Draws, Energy_Ss, Energy_Ds, Mfct_goods

def objective(params):
    betas, phis, lambda_As, sigma_As, lambda_Cs, sigma_Cs = \
        get_parameters(params)
    Crop_yields, Food_Ss, Food_Ds, Biofuel_Stocks, Biofuel_Es, \
        Water_Draws, Energy_Ss, Energy_Ds, Mfct_goods = simulate_all(params)

    return industry.partial_objective(Mfct_goods) + fossil.objective(phis) + agriculture.partial_objective(Food_Ss, Food_Ds) + biofuel.partial_objective(Biofuel_Es, Energy_Ds)

def constraint_water(params):
    Crop_yields, Food_Ss, Food_Ds, Biofuel_Stocks, Biofuel_Es, \
        Water_Draws, Energy_Ss, Energy_Ds, Mfct_goods = simulate_all(params)

    overdraws = 0
    for county in range(N):
        overdraw = Water_Draws[county] - W_surf[county]
        if overdraw > 0:
            overdraws += overdraw

    return -overdraws

def constraint_energy(params):
    Crop_yields, Food_Ss, Food_Ds, Biofuel_Stocks, Biofuel_Es, \
        Water_Draws, Energy_Ss, Energy_Ds, Mfct_goods = simulate_all(params)

    return sum(Energy_Ss) - sum(Energy_Ds)

bounds = biofuel.bounds + fossil.bounds + agriculture.bounds + industry.bounds

constraints = [{'type': 'ineq', 'fun': constraint_water}, {'type': 'ineq', 'fun': constraint_energy}]

def safe_generate():
    """Generates a starting point that satisfies both constraints."""
    # Initial conditions
    invalid = True
    attempts = 0
    while invalid:
        params = generate()
        ineq1 = constraint_water(params)
        ineq2 = constraint_energy(params)
        invalid = ineq1 < 0 or ineq2 < 0
        attempts += 1

    return params

if __name__ == '__main__':
    result = lib.maximize(objective, safe_generate, bounds, iterations=100, constraints=constraints)
    print result
