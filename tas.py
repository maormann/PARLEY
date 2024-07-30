import os

import umc_synthesis
import prism_caller
import run_evochecker
import evaluation
import plot_fronts
import itertools

MAX_REPLICATIONS = 10

MIN_FREQUENCY = 1
MAX_FREQUENCY = 10

URS = ('s1', 's2', 's3')  # Uncertainty Reduction Services


def models():
    infile = os.getenv('PARLEY_MODEL_FILE_IN', 'Applications/EvoChecker-master/models/TAS.prism')
    outfile = os.getenv('PARLEY_MODEL_FILE_OUT', 'Applications/EvoChecker-master/models/TAS_umc.prism')
    umc_synthesis.manipulate_prism_model(infile,
                                         outfile,
                                         before_actions=['set_alarm_sender'],
                                         after_actions=['start_UAC'],
                                         possible_decisions=[MIN_FREQUENCY, MAX_FREQUENCY],
                                         urs=URS)


def baseline():
    baseline_file = os.getenv('PARLEY_BASELINE_FILE', 'Applications/EvoChecker-master/data/TAS_BASELINE/Front')
    infile = os.getenv('PARLEY_MODEL_FILE_OUT', 'Applications/EvoChecker-master/models/TAS_umc.prism')
    os.makedirs(os.path.dirname(baseline_file), exist_ok=True)
    prism_caller.properties = ['\'R{"model_drift"}=? [ C<=200 ]\'', '\'R{"total_costs"}=? [ C<=200 ]\'']
    with open(baseline_file, 'w') as b_file:
        for period in itertools.product(range(MIN_FREQUENCY, MAX_FREQUENCY + 1), range(MIN_FREQUENCY, MAX_FREQUENCY + 1), range(MIN_FREQUENCY, MAX_FREQUENCY + 1)):
            b_file.write(prism_caller.compute_baseline(infile, period))
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
    baseline()
    # evo_checker()
    # fronts(i)
    # evaluation.main()


if __name__ == '__main__':
    os.makedirs('plots/fronts', exist_ok=True)
    os.makedirs('plots/box-plots', exist_ok=True)
    main()
