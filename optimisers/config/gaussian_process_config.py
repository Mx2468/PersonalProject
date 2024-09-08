# Number of points to sample before gaussian process estimator starts estimating
# the best points to select. Default is 103 due to LHS being used as default for sampling
# for shorter runs, the value will need to be reduced
N_INITIAL_POINTS = 12

# Generator of initial set of random points - default set to latin hypercube
INITIAL_POINT_GENERATOR_METHOD = "random"

# Acquisition function to use
# default value "gp_hedge" chooses one of 3 functions each iteration
ACQUISITION_FUNCTION = "gp_hedge"

# Method used to optimise the acquisition function
# default value "auto" is set to be configured on the basis of search space
ACQUISITION_OPTIMISATION_METHOD = "auto"

# Set to "gaussian" as objective function (runtime evaluation) returns noisy results
# Not recommended to set this to any other value
NOISE = 'gaussian'

