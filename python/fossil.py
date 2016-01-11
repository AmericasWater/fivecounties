# -*- coding: utf-8 -*-
### Fossil fuel component
## Optimizes phi, the amount of fossil fuel purchased on the market
## Within this component, fossil fuel is a direct cost with no benefit
## Call `python fossil.py` to optimize only fuel purchases (goes to 0)

import pandas
import numpy as np
import lib

# Load county data for parameters
county_data= pandas.read_csv('ComplexData.csv')

#################### GLOBAL PARAMETERS #####################
N= len(county_data['county']) # number of counties

W_surf= list(county_data['water_cap']) # total water rights (i.e. max water drawn from river)

epsilon_f= 8.33 # kWh per kg of fossil resource (coal)
lambda_f= 150e-3 # fossil fuel energy production, Liters per kWh
# From http://www.ucsusa.org/clean_energy/our-energy-choices/energy-and-water-use/water-energy-electricity-coal.html

def generate():
    # Fossils burned by county
    phis = np.random.uniform(0, 1e9, N)

    return phis.tolist()

def simulate_county(phi):
    Fossil_E = epsilon_f * phi
    Water_Draw = lambda_f * Fossil_E

    return Fossil_E, Water_Draw

def simulate_all(phis):
    Fossil_Es = []
    Water_Draws = []

    for county in range(N):
        Fossil_E, Water_Draw = simulate_county(phis[county])

        Fossil_Es.append(Fossil_E)
        Water_Draws.append(Water_Draw)

    return Fossil_Es, Water_Draws

def objective(phis):
    total = 0
    for county in range(N):
        total -= phis[county] * lib.p_E # this all costs us

    return total

bounds = [(0, 1e9)] * N

if __name__ == '__main__':
    result = lib.maximize(objective, generate, bounds)
    print result

    print bounds
