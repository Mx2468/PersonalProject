## Setting Up The Environment
Setting up the environment for the first time is done by using the provided environment file. Everything needed is provided in the ./setup/ directory.
The environment contains the list of all packages that conda has to install, including all the exact versions required. This is a YAML file is located in path ./setup/personal_project_environment.yml
(from the root of the project file).

To create the environment, you should run the following command:

`conda env create --file ./setup/personal_project_environment.yml`

This command is already wrapped up in the install.sh file. The recommended way to create the environment is to run the install.sh file, by running the following command:
`./setup/install.sh`. 
This will create an environment called ”PersonalProject”, with all the correct packages installed.


## Running The Code
Once the environment is created, it is accessible by using the command `conda activate PersonalProject`.

It is highly recommended that the software is run within this environment, as otherwise the
code may not behave as intended. There are two ways to run the program within the environment:

1. Use the command `conda activate PersonalProject` to activate the environment, followed by the command to run the program.
2. Prefix the command to run the program with the command as follows: `conda run --live-stream -n PersonalProject <command to run program>`

Please ensure that one of these two options are carried out when running the program, to ensure
that the environment is activated, and the software behaves as intended

## Running An Optimisation
To run the code, the command is simple `python ./flag_controller.py [flags]` (Remember to use the conda environment when running this code)

### Flags

The only flag that is necessary to provide is:
- -i or –input - The path to the input source code. Must be a c++ file with one of the common
c++ file extensions: ”.cpp”, ”.C” or ”.cc”.

The optional flags are:

- -bf or –binary-flags - The path to a .txt file listing the binary-choice flags to be optimised.
This defaults to a pre-defined file containing all the binary flags of G++. This exists to
provide the user with the ability to define their own domain of flags to optimise if they
choose to e.g. narrow down the search amongst a few flags known to have a performance
impact.
- -df or –domain-flags - The path to a .json file listing the specific-domain flags to be optimised. This defaults to a pre-defined file containing all the specific-domain flags of G++.
As with the binary flags option, this exists to provide the user with the ability to define their own domain of flags to optimise if they choose to e.g. narrow down the search
amongst a few flags known to have a performance impact.
- -o or –output - The path to the output file i.e. the file which the optimised flag choices will
be written to. This defaults to ./flags_dump.txt. The option exists to allow the user
to override this if they have conflicts with files in their environment, or need the output
to be a certain file name.
- -m or –method - The optimisation method to use for the optimisation run. There are 3
choices: random, genetic or gaussian. If no choice is provided, random is picked as the
default.
- -n or –opt-steps - An integer number of optimisation steps to run the optimisation for. (NB:
The number of optimisation steps corresponds 1-to-1 with the number of states explored in
the Gaussian process and random optimisation methods. The genetic algorithm method
will explore number of optimisation steps × population size number of states.)
- –num-code-runs - An integer number of runs used to benchmark the compiled code at the
evaluation of each optimisation choice.
- –dont-start-with-o3 - Disable the default behaviour using the -O3 optimisations as a basis
to start the optimisation with. Specifying this flag means that the optimisation will use
no optimisations (equivalent to -O0) as a starting point.
- –dont-compare-with-o3 - Disable the default behaviour using the -O3 optimisations to compare to at the end of the run. Specifying this flag means that the result of the optimisation
will be compared to no optimisations (equivalent to -O0).
- –log-results - Log the algorithm, number of steps, and the percentage result achieved to a file
at path runlog.log.


To display the list of flags and what they do, use the `command python <path to flag_controller.py> --help`
