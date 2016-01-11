### Shared functions and parameters
## Parameters:
## This is mainly for the cost of energy on the market, and the markup parameter
## Functions:
## maximize is the general optimization function, which adjust the scale of parameters

from scipy import optimize

objective_scaling = 1e6

# Shared parameters
p_E = 0.4 # the global price of fuel (per kWh)
markup = 2.0 # difference between selling price and buying price

# Scaling for better optimization

def divide_scalings(params, scalings):
    return [params[ii] / scalings[ii] for ii in range(len(params))]

def multiply_scalings(params, scalings):
    return [params[ii] * scalings[ii] for ii in range(len(params))]

def fix_bounds(my_result, my_bounds, my_objective, args=()):
    my_params = my_result['x']
    for ii in range(len(my_params)):
        if my_params[ii] < my_bounds[ii][0]:
            my_params[ii] = my_bounds[ii][0]

        if my_bounds[ii][1] is not None and my_params[ii] > my_bounds[ii][1]:
            my_params[ii] = my_bounds[ii][1]

    my_result['fun'] = my_objective(my_params, *args)

def maximize(objective, generate, bounds, iterations=100, args=(), constraints=[]):
    scalings = map(lambda bound: bound[1] if bound[1] is not None else 1, bounds)

    def my_objective(my_params, *args):
        params = multiply_scalings(my_params, scalings)
        return -objective(params, *args) / objective_scaling

    def my_generate():
        return divide_scalings(generate(), scalings)

    my_bounds = [(0, None) if bound[1] is None else (0, 1) for bound in bounds]

    best_result = dict(x=None, fun=-float('inf'), njev=0, nfev=0, nit=0, success=False, message=None)

    for ii in xrange(iterations):
        result = optimize.minimize(my_objective, my_generate(), args=args, method='SLSQP', bounds=my_bounds)
        if not result['success'] and best_result['success']:
            continue

        fix_bounds(result, my_bounds, my_objective, args=args)
        result['fun'] *= -objective_scaling

        if result['fun'] > best_result['fun']:
            result['x'] = multiply_scalings(result['x'], scalings)
            result['njev'] += best_result['njev']
            result['nfev'] += best_result['nfev']
            result['nit'] += best_result['nit']
            best_result = result
            print "Improved! ({})".format(ii + 1)

            if result['fun'] > 0:
                break

    return best_result
