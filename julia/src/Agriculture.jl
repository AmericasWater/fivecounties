using Mimi

#################### GLOBAL PARAMETERS #####################
## Yields in US: 7000 kg / Ha * 1 Ha / .01 km = 700000 kg / km^2
## All else producing results around 100000, so
yield_scaling = 5

delta = 0.6 # elasticity of crop production (corn) with respect to land
# (i.e., exponent of land resource in agricultural production function
gamma = 0.3 # elasticity of crop production (corn) with respect to energy
# (i.e., exponent of land resource in agricultural production function)

p_F = 0.25  # the global price of food (per kg of corn)

@defcomp agriculture begin
    regions = Index()

    # agricutural water demand, liters per sq.km. per year, avg for US is 500
    lambda_a = Parameter(index=[regions])

    # agricutural energy demand, kilowatt-hours per sq.km. per year
    sigma_a = Parameter(index=[regions])

    # total land area of the county, sq.km.
    area = Parameter(index=[regions])

    # fraction of land used for agriculture
    alpha = Parameter(index=[regions])

    # local soil productivity, unitless
    theta = Parameter(index=[regions])

    # fraction of agricultural land for biofuel
    beta = Parameter(index=[regions])

    cropyield = Variable(index=[regions])
    food_s = Variable(index=[regions])
    agriculturewaterdraw = Variable(index=[regions])
    agricultureenergyuse = Variable(index=[regions])
end

@doc """Simulates crop yields as a Cobb-Douglas model of water and energy."""
function simulate(state::agriculture)
    v = state.Variables
    p = state.Parameters

    v.cropyield = yield_scaling * p.alpha .* p.area .* (p.theta.^delta) .* (p.sigma_a.^gamma) * p.lambda_a.^(1 - delta - gamma) # in kg corn

    v.food_s = (1 - p.beta) * v.cropyield    # in kg corn

    v.agriculturewaterdraw = p.lambda_a * p.alpha .* p.area
    v.agricultureenergyuse = p.sigma_a * p.alpha .* p.area
end

@doc """Sell all the food at the market price."""
function objective(state::agriculture)
    return v.food_s * p_F
