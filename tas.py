import os

import umc_synthesis
import prism_caller
import run_evochecker
import evaluation
import plot_fronts

MAX_REPLICATIONS = 10

MIN_FREQUENCY = 1
MAX_FREQUENCY = 10


def models():
    infile = f'Applications/EvoChecker-master/models/TAS.prism'
    outfile = f'Applications/EvoChecker-master/models/TAS_umc.prism'
    umc_synthesis.manipulate_prism_model(infile,
                                         outfile,
                                         before_actions=['start_UAC'],
                                         after_actions=['end_round'],
                                         possible_decisions=[MIN_FREQUENCY, MAX_FREQUENCY],)


def baseline():
    baseline_file = f'Applications/EvoChecker-master/data/TAS_BASELINE/Front'
    infile = f'Applications/EvoChecker-master/models/TAS.prism'
    os.makedirs(f'Applications/EvoChecker-master/data/TAS_BASELINE', exist_ok=True)
    prism_caller.properties = ""  # TODO
    with open(baseline_file, 'w') as b_file:
        for period in range(MIN_FREQUENCY, MAX_FREQUENCY + 1):
            b_file.write(prism_caller.compute_baseline(infile, period))
            if period < MAX_FREQUENCY:
                b_file.write('\n')
            print('finished baseline')


def evo_checker():
    # invoke EvoChecker
    run_evochecker.simple_run()


def fronts(i):
    for period in range(MAX_REPLICATIONS):
        plot_fronts.plot_pareto_front(i, period)


def main():
    models()
    # baseline(i)
    evo_checker()
    # fronts(i)
    # evaluation.main()


if __name__ == '__main__':
    os.makedirs('plots/fronts', exist_ok=True)
    os.makedirs('plots/box-plots', exist_ok=True)
    main()
