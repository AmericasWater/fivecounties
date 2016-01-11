# -*- coding: utf-8 -*-
### Biofuel component
## Handles the choice variable beta, the amount of agriculture land for biofuels
## Simulates the energy provided and water used to generate biofuel
## Objective unctions sells any access energy
## Call as `python biofuel.py` to optimize the amount of biofuel alone (goes to 1).

import pandas
import numpy as np
import lib
from scipy import optimize

# Load county data for parameters
county_data= pandas.read_csv('ComplexData.csv')

#################### GLOBAL PARAMETERS #####################
N = len(county_data['county']) # number of counties

# Resource to Energy conversion rates (kilowatt hours per...)
epsilon_b= 1.75 # per kg of crop (corn)

# Average Water Demand (liters per ...)
lambda_b=  0.856 # P: 0.5, biofuel energy production, Liters per kg corn

def generate():
    # fraction of agricultural land used for biofuels, between 0 and 1
    betas = np.random.uniform(0, 1, N)

    return betas.tolist()

def simulate_county(beta, Crop_yield):
    """Simulates the energy provided and water used to generate biofuel."""
    Biofuel_Stock = beta * Crop_yield   # in kg corn
    Biofuel_E = Biofuel_Stock * epsilon_b
    Water_Draw = lambda_b * Biofuel_E

    return Biofuel_Stock, Biofuel_E, Water_Draw

def simulate_all(betas, Crop_yields):
    Biofuel_Stocks = []
    Biofuel_Es = []
    Water_Draws = []

    for county in range(N):
        Biofuel_Stock, Biofuel_E, Water_Draw = \
            simulate_county(betas[county], Crop_yields[county])

        Biofuel_Stocks.append(Biofuel_Stock)
        Biofuel_Es.append(Biofuel_E)
        Water_Draws.append(Water_Draw)

    return Biofuel_Stocks, Biofuel_Es, Water_Draws

# Just sells of any remaining
def partial_objective(Biofuel_Es, Energy_Ds):
    if sum(Biofuel_Es) > sum(Energy_Ds):
        return sum(Biofuel_Es) - sum(Energy_Ds)*lib.p_E / lib.markup

    return 0

# Assumes that energy supply comes from nowhere else
def sole_objective(betas, Crop_yields, Energy_Ds):
    Biofuel_Stocks, Biofuel_Es, Water_Draws = simulate_all(betas, Crop_yields)

    total = 0
    for county in range(N):
        if Biofuel_Es[county] > Energy_Ds[county]:
            total += (Biofuel_Es[county] - Energy_Ds[county])*lib.p_E / lib.markup
        else:
            total += (Biofuel_Es[county] - Energy_Ds[county])*lib.p_E

    return total

bounds = [(0, 1.0)] * N

if __name__ == '__main__':
    # External parameters
    Crop_yields = [500000] * 5
    Energy_Ds = [100] * 5

    print lib.maximize(sole_objective, generate, bounds, args=(Crop_yields, Energy_Ds))
