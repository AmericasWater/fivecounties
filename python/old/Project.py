# -*- coding: utf-8 -*-
# PROJECT.PY

import os
import pandas
import numpy as np
import matplotlib.pyplot as plt
import scipy
import random
from __future__ import division
from deap import base, creator, tools

# Load county data for parameters
county_data= pandas.read_csv('ComplexData.csv')


#################### GLOBAL PARAMETERS #####################
T= 50 # currently in years
N= len(county_data['county']) # number of counties
p_food= 0.1 # world price of food per kg corn
p_mn= 1 # world price of the manufactured good (normalized to 1)
f_p = 250 # average food demand, kg of corn per person per year
    # derivation: (2500 kcal/day)*(365 day/year)/(3650 kcal/kg of corn)

  # Future Considerations: change timescale to months, allow for multiple crops

# Elasticities for production functions (unitless)
delta= 0.6 # elasticity of crop production (corn) with respect to land
    # (i.e., exponent of land resource in agricultural production function
gamma= 0.3 # elasticity of crop production (corn) with respect to energy
    # (i.e., exponent of land resource in agricultural production function)

# Resource to Energy conversion rates (kilowatt hours per...)
epsilon_b= 1.75 # per kg of crop (corn)
epsilon_f= 8.33 # per kg of fossil resource (coal)

# Average Water Demand (liters per ...)
lambda_p= 100000  # residential, per person per year
lambda_b= 0.5 # biofuel energy production, per kilowatt hour
lambda_f= 150 # fossil fuel energy production, per kilowatt hour

  # Future Considerations: residential demand out by housing type or relate to
    #density of residential land

# Average Energy Demand (Kilowatt-Hours per...)
sigma_p= 2900 # residential, per person per year

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

  # Future Considerations: allow A to vary with time, allow theta to vary with
    # farming practices, add groundwater, add precipitation, allow surface water
    # availability to vary with time

# Production Elasticities (unitless)
eta= list(county_data['eta']) # elasticity of commercial output with respect to energy
    # (i.e., exponent of energy resource in commercial production function)

# Average Energy Demand (Kilowatt-Hours per...)
sigma_w= list(county_data['sigma_w']) # water pumping/treatment, per liter



########## GENETIC ALGORITHM (GA) SET UP ###########

# Fitness Measure- Maximization- multiple diff objectives (e.g.1 min 1 max)
optim_goals = ones(N+1)
optim_goals[-1]=-optim_goals[-1]
creator.create("FitnessMulti", base.Fitness, weights=tuple(optim_goals))

# GA Individuals (i.e. potential optimal solutions)
creator.create("Individual", list, fitness=creator.FitnessMulti)

    ########## TOOLS FOR CREATING INDIVIDUALS ###########
# Toolbox
toolbox = base.Toolbox()
# fraction of agricultural land used for biofuels, between 0 and 1
toolbox.register("beta", random.uniform, 0, 1)
# agricutural water demand, liters per sq.km. per year, avg for US is 500
toolbox.register("lambda_a", random.uniform, 300, 700)
# commercial water demand, liters per sq.km. per year
toolbox.register("lambda_c", random.uniform, 200, 700)
# agricutural energy demand, kilowatt-hours per sq.km. per year, avg for US is 500
toolbox.register("sigma_a", random.uniform, 300000 , 500000)
# commercial energy demand, liters per sq.km. per year, avg for US is 500
toolbox.register("sigma_c", random.uniform, 2000000, 4000000)
# energy production from fossil sources, between 0 and 1
toolbox.register("phi", random.uniform, 0, 1)

toolbox.register("individual", tools.initCycle, creator.Individual,
                 (toolbox.beta, toolbox.lambda_a, toolbox.lambda_c,toolbox.sigma_a,
                 toolbox.sigma_c,toolbox.phi), n=N)

########## FITNESS MEASURE-OBJECTIVE FUNCTION ###########


########## OPTIMIZATION ###########
def evaluate(individual):

    Crop_yield=[]
    Food_S= []
    Energy_S=[]
    Mfctd_good=[]
    Water_Draw=[]
    Energy_D=[]

    for j in range(N):

        beta=individual[j*6]
        lambda_a=individual[j*6+1]
        lambda_c=individual[j*6+2]
        sigma_a=individual[j*6+3]
        sigma_c=individual[j*6+4]
        phi=individual[j*6+5]

        # Agricultural Production
        Crop_yield.append(alpha[j]*Area[j]*( (theta[j]**delta) * (sigma_a**gamma) * (lambda_a**(1-delta-gamma)))) # kg corn
        Food_S.append((1-beta)*Crop_yield[-1])    # kg corn
        Biofuel_Stock= Crop_yield[-1] - Food_S[-1]   # kg corn
        # Energy Production
        Fossil_E = epsilon_f*phi*Fossil_stock[j]
        Biofuel_E = Biofuel_Stock*epsilon_b
        Energy_S.append(Fossil_E + Biofuel_E)
        # Production of Manufactured Good
        Mfctd_good.append((1-alpha[j])*Area[j]* (sigma_c**eta[j])*(lambda_c**(1-eta[j])))
        # Water Demand
        Water_Draw.append(P[j]*lambda_p + lambda_a*alpha[j]*Area[j] - lambda_c*(1-alpha[j])*Area[j] + lambda_f*Fossil_E + lambda_b*Biofuel_E)
        # Energy Demand
        Energy_D.append((P[j]*sigma_p) + (sigma_a*alpha[j]*Area[j]) + (sigma_c*(1-alpha[j])*(Area[j])) + (sigma_w[j]*Water_Draw[-1]))

    p_energy= 0.08 -0.25*(2000000000-sum(Energy_D))
    p_water = 0.001-0.75*(191320000000-sum(Water_Draw))

#    ----------------------UNDER CONSTRUCTION---------------------------------
    optim = []
    for j in range(N):
        optim.append(([Food_S[j]-Food_D[j])*p_food


    return


        # Food Demand
        Food_D= P[j]*f_p[j]  # kg corn
