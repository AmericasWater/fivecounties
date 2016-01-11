## JAMES NOTES:
## objective function should not change global variables
## constraint functions should rely on passed in arguments

from __future__ import division
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy import optimize
import random
from collections import deque
import operator
import matplotlib.patches as mpatches
import pandas
from deap import base, creator, tools

county_data = pandas.read_csv("ComplexData.csv")
T= 50 # currently in years
N= len(county_data['county']) # number of counties
p_mn= 1 # world price of the manufactured good (normalized to 1)
f_p = 250 # average food demand, kg of corn per person per year
    # derivation: (2500 kcal/day)*(365 day/year)/(3650 kcal/kg of corn)

  # Future Considerations: change timescale to months, allow for multiple crops

# Elasticities for production functions (unitless)
delta= 0.6 # elasticity of crop production (corn) with respect to land
    # (i.e., exponent of land resource in agricultural production function
gamma= 0.3 # elasticity of crop production (corn) with respect to energy
    # (i.e., exponent of land resource in agricultural production function)
eta=  0.8 # elasticity of commercial output with respect to energy
    # (i.e., exponent of energy resource in commercial production function)

p_F = 0.25  # the global price of food (per kg of corn)
p_E = 0.4 # the global price of fuel (per kWh)


# Resource to Energy conversion rates (kilowatt hours per...)
epsilon_b= 1.75 # per kg of crop (corn)
epsilon_f= 8.33 # per kg of fossil resource (coal)

# Average Water Demand (liters per ...)
lambda_p= 100000  # residential, per person per year
lambda_b=  0.856 # biofuel energy production, Liters per kg corn
lambda_f= 150 # fossil fuel energy production, Liters per kWh

  # Future Considerations: residential demand out by housing type or relate to
    #density of residential land

# Average Energy Demand (Kilowatt-Hours per...)
sigma_p= 100000 # residential, per person per year

  # Future Considerations: Allow for sigma_p and sigma_w to vary.
delta= 0.6 # elasticity of crop production (corn) with respect to land
    # (i.e., exponent of land resource in agricultural production function
gamma= 0.3 # elasticity of crop production (corn) with respect to energy
    # (i.e., exponent of land resource in agricultural production function)


p_F = 0.25  # the global price of food (per kg of corn)
p_E = 0.4 # the global price of fuel (per kWh)


# Resource to Energy conversion rates (kilowatt hours per...)
epsilon_b= 1.75 # per kg of crop (corn)
epsilon_f= 8.33 # per kg of fossil resource (coal)

# Average Water Demand (liters per ...)
lambda_p= 100000  # residential, per person per year
lambda_b=  0.856 # biofuel energy production, Liters per kg corn
lambda_f= 150 # fossil fuel energy production, Liters per kWh

  # Future Considerations: residential demand out by housing type or relate to
    #density of residential land

# Average Energy Demand (Kilowatt-Hours per...)
sigma_p= 100000 # residential, per person per year

  # Future Considerations: Allow for sigma_p and sigma_w to vary.


########## COUNTY PARAMETERS- INITIAL CONDITIONS ###########
# Demographics
P= list(county_data['population']) # population

  # Future Considerations: allow P to vary, break out P by housing type,
    # include density measure for residential land

# Land Use and Resources
Area = list(county_data['co_area']) # total land area of the county, sq.km.
alpha= list(county_data['ag_area']/county_data['co_area'])  # fraction of land used for agriculture
theta= list(county_data['soil']) # local soil productivity, unitless
Fossil_stock= list(county_data['fossil'])  # fossil resource stock at time t=0
W_surf= list(county_data['water_cap']) # total water rights (i.e. max water drawn from river)
sigma_w = list(county_data['sigma_w'])
eta = list(county_data['eta'])  # elasticity of commercial output with respect to energy
    # (i.e., exponent of energy resource in commercial production function)

def objectiveFunct(x, county, sign = -1.0):
    (beta, sigma_A, sigma_C, lambda_A, lambda_C) = x

    # Objective function
    Crop_yield[county] = alpha[county] * Area[county] * (((theta[county]) ** (delta)) * ((sigma_A) ** (gamma)) * ((lambda_A) ** (1 - delta - gamma)))   # in kg corn
    Food_S[county] = (1 - beta) * Crop_yield[county]    # in kg corn
    Biofuel_Stock[county] = beta * Crop_yield[county]   # in kg corn
    Food_D[county] = P[county] * f_p         # in kg corn

    Fossil_E[county] = epsilon_f * phi[county]
    Biofuel_E[county] = Biofuel_Stock[county] * epsilon_b
    Energy_S[county] = Fossil_E[county] + Biofuel_E[county]

    Water_Draw[county] = P[county] * lambda_p + lambda_A * alpha[county] * Area[county] - lambda_C * (1- alpha[county]) * Area[county] + lambda_f * Fossil_E[county] + lambda_b * Biofuel_E[county]

    Energy_D[county] = (P[county] * sigma_p) + (sigma_A * alpha[county] * Area[county]) + (sigma_C * (1 - alpha[county]) * (Area[county])) + (sigma_w[county] * Water_Draw[county])

    Mfct_good[county] = (1 - alpha[county]) * Area[county] * (sigma_C ** eta[county]) * (lambda_C) ** (1-eta[county])

    return sign * ((Food_S[county] - Food_D[county])*p_F + (Energy_S[county] - Energy_D[county])*p_E + Mfct_good[county] * p_mn)

Biofuel_Stock = []
Crop_yield = []
Food_S = []
Food_D = []
Water_Draw = []
Energy_D = []
Mfct_good = []
Fossil_E = []
Biofuel_E = []
Energy_S = []

beta = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
phi = [120000, 0, 500000, 500000, 0]
sigma_A = [160000, 160000, 160000, 160000, 160000, 160000]
sigma_C = [160000, 160000, 160000, 160000, 160000, 160000]
lambda_A = [180000, 180000, 180000, 180000, 180000, 180000]
lambda_C = [180000, 180000, 180000, 180000, 180000, 180000]

for j in range(0, N):
    county = j

    Crop_yield.append(alpha[county] * Area[county] * (((theta[county]) ** (delta)) * ((sigma_A[county]) ** (gamma)) * ((lambda_A[county]) ** (1 - delta - gamma))))   # in kg corn
    Food_S.append((1 - beta[county]) * Crop_yield[county])    # in kg corn
    Biofuel_Stock.append(beta[county] * Crop_yield[county])   # in kg corn
    Food_D.append( P[county] * p_F )        # in kg corn

    Fossil_E.append(epsilon_f * phi[county])
    Biofuel_E.append(Biofuel_Stock[county] * epsilon_b)
    Energy_S.append(Fossil_E[county] + Biofuel_E[county])

    Water_Draw.append(P[county] * lambda_p + lambda_A * alpha[county] * Area[county] - lambda_C[county] * (1- alpha[county]) * Area[county] + lambda_f * Fossil_E[county] + lambda_b * Biofuel_E[county])

    Energy_D.append((P[county] * sigma_p) + (sigma_A[county] * alpha[county] * Area[county]) + (sigma_C[county] * (1 - alpha[county]) * (Area[county])) + (sigma_w[county] * Water_Draw[county]))

    Mfct_good.append( (1 - alpha[county]) * Area[county] * (sigma_C[county] ** eta[county]) * (lambda_C[county]) ** (1-eta[county]))

    cons = ({'type': 'ineq', 'fun': lambda x: W_surf[county] - Water_Draw[county]}, {'type': 'ineq', 'fun': lambda x: Fossil_stock[county]-phi[county]}, {'type': 'ineq', 'fun': lambda x: beta[county]}, {'type': 'ineq', 'fun': lambda x: 1 - beta[county]}, {'type': 'eq', 'fun': lambda x: sum(Energy_D[:]) - sum(Energy_S[ : ])} , {'type': 'eq', 'fun': lambda x: sum(Food_D[:]) - sum(Food_S[ :])})

    print objectiveFunct([0.5, 50000, 50000, 50000, 100000], county)

    result = optimize.minimize(objectiveFunct, [0.5, 50000, 50000, 50000, 100000], args=(county,), method = 'SLSQP', constraints = cons, options = {'disp': True})
    print result
