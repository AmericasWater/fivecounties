## Run from julia in directory, not in Juno

push!(LOAD_PATH, "/Users/jrising/projects/iam/")

using Mimi

include("SimpleAgriculture.jl")

my_model = Model(Number)

setindex(my_model, :time, 1)
setindex(my_model, :regions, 5)

addcomponent(my_model, agriculture)

# From ComplexData
setparameter(my_model, :agriculture, :area, Number[270., 637., 1267., 582., 255.])
setparameter(my_model, :agriculture, :theta, Number[.2, .3, .5, .7, .8])

# To be optimized
setparameter(my_model, :agriculture, :fertilizer, Number[1. for i in 1:5]) # [1339430. for i in 1:5])

#=
println("Checking model...")
run(my_model)

#Check results
println(my_model[:agriculture, :cornproduction])
println(my_model[:agriculture, :cornenergyuse])
=#

println("Running optimization...")

using OptiMimi

# Prices of goods
p_F = 0.25  # the global price of food (per kg of corn)
p_E = 0.4   # the global price of fuel (per kWh)

# Objective to maximize economic output
function objective(model::Model)
    sum(my_model[:agriculture, :cornproduction] * p_F - my_model[:agriculture, :cornenergyuse] * p_E)
end

constraints = [model -> sum(model.components[:agriculture].Parameters.fertilizer) - 1e6]

println("Setup...")
optprob = problem(my_model, [:agriculture], [:fertilizer], [0.], [1e6], objective, constraints=constraints)
println("Solve...")
##(minf, minx) = solution(opt, () -> rand() < .5 ? [1339430. for i in 1:5] : [0. for i in 1:5]) #, verbose=true)
(maxf, maxx) = solution(optprob, () -> [0. for i in 1:5])

println(maxf)
println(maxx)
