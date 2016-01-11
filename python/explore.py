### Iterates over a range of food and fuel prices
## Writes the optimum found for each

import csv
import numpy as np
import merged, agriculture, lib

with open('prices.csv', 'w') as fp:
    writer = csv.writer(fp)
    writer.writerow(['p_E', 'p_F', 'objective'] +
                    ['beta' + str(ii) for ii in range(1, 6)] + \
                    ['phi' + str(ii) for ii in range(1, 6)] + \
                    ['lambda_A' + str(ii) for ii in range(1, 6)] + \
                    ['sigma_A' + str(ii) for ii in range(1, 6)] + \
                    ['lambda_C' + str(ii) for ii in range(1, 6)] + \
                    ['sigma_C' + str(ii) for ii in range(1, 6)])

    for p_E in np.exp(np.linspace(np.log(.1), np.log(10), 60)): #[.1, .2, .5, 1.0, 2.0, 5.0, 10.0]:
        for p_F in np.exp(np.linspace(np.log(.1), np.log(10), 60)): #[.1, .2, .5, 1.0, 2.0, 5.0, 10.0]:
            print p_E, p_F
            lib.p_E = p_E
            agriculture.p_F = p_F

            result = lib.maximize(merged.objective, merged.safe_generate, merged.bounds, iterations=20, constraints=merged.constraints)
            writer.writerow([p_E, p_F] + [result['fun']] + result['x'])
