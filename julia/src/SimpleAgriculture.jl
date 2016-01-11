using Mimi
using OptiMimi

#################### GLOBAL PARAMETERS #####################
## Yields in US: 7000 kg / Ha * 1 Ha / .01 km = 700000 kg / km^2
## All else produces results around 25, so
yield_scaling = 25000

delta = 0.6 # elasticity of crop production (corn) with respect to land
# (i.e., exponent of land resource in agricultural production function
gamma = 0.3 # elasticity of crop production (corn) with respect to energy
# (i.e., exponent of land resource in agricultural production function)

@defcomp agriculture begin
    regions = Index()

    # agricutural energy demand, kilowatt-hours per sq.km. per year
    fertilizer = Parameter(index=[regions])

    # total land area of the county, sq.km.
    area = Parameter(index=[regions])

    # local soil productivity, unitless
    theta = Parameter(index=[regions])

    cornproduction = Variable(index=[regions])
    cornenergyuse = Variable(index=[regions])
end

"""Simulates crop yields as a Cobb-Douglas model of water and energy."""
function timestep(state::agriculture, tt::Int)
    v = state.Variables
    p = state.Parameters

    v.cornproduction = yield_scaling * p.area .* (p.theta.^delta) .* (p.fertilizer.^gamma) # in kg corn
    v.cornenergyuse = p.fertilizer .* p.area
end
