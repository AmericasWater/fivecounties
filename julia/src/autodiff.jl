## Run from julia in directory, not in Juno

push!(LOAD_PATH, "/Users/jrising/projects/iam/")

using ForwardDiff

#=
function f(xx::Vector)
    yy::Vector{Number} = xx .^ 2
    dump(yy)
    sum(yy)
end

println(f([3.0, 5.0]))
println(ForwardDiff.gradient(f, [3.0, 5.0]))

function f(fertilizer::Vector)
    area = [270., 637., 1267., 582., 255.]

    cornenergyuse = fertilizer .* area

    dump(sum(cornenergyuse))

    sum(cornenergyuse * .4)
end

println(ForwardDiff.gradient(f, rand(5)))

function f(fertilizer::Vector)
    yield_scaling = 25000
    delta = 0.6
    gamma = 0.3
    area = [270., 637., 1267., 582., 255.]
    theta = [.2, .3, .5, .7, .8]

    cornproduction::Vector = yield_scaling * area .* (theta.^delta) .* (fertilizer.^gamma) # in kg corn
    cornenergyuse::Vector = fertilizer .* area

    dump(sum(cornproduction))

    sum(cornproduction * .25 - cornenergyuse * .4)
end

println(ForwardDiff.gradient(f, rand(5)))
=#

using Mimi

include("SimpleAgriculture.jl")

my_model = Model(true)

setindex(my_model, :regions, 5)

addcomponent(my_model, agriculture)

# From ComplexData
setparameter(my_model, :agriculture, :area, [270., 637., 1267., 582., 255.])
setparameter(my_model, :agriculture, :theta, [.2, .3, .5, .7, .8])

# To be optimized -- XXX: I think I need to set this initially
setparameter(my_model, :agriculture, :fertilizer, [1. for i in 1:5]) # [1339430. for i in 1:5])

#=
println("Checking model...")
run(my_model)

#Check results
println(my_model[:agriculture, :cornproduction])
println(my_model[:agriculture, :cornenergyuse])
=#

using OptiMimi

# Prices of goods
p_F = 0.25  # the global price of food (per kg of corn)
p_E = 0.4   # the global price of fuel (per kWh)

function objective(model::Model)
    sum(my_model[:agriculture, :cornproduction] * p_F - my_model[:agriculture, :cornenergyuse] * p_E)
end


uo = unaryobjective(my_model, [:agriculture], [:fertilizer], objective)

guo = ForwardDiff.gradient(uo)

guo([0. for i in 1:5])
