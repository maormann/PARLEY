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

URS = ('s1')  # Uncertainty Reduction Services


def models():
    infile = 'Applications/EvoChecker-master/models/TAS_1_service.prism'
    outfile = 'Applications/EvoChecker-master/models/TAS_1_service_umc.prism'
    umc_synthesis.manipulate_prism_model(infile,
                                         outfile,
                                         before_actions=['start_UAC'],
                                         after_actions=['end_round'],
                                         possible_decisions=[MIN_FREQUENCY, MAX_FREQUENCY],
                                         urs=URS)


# TODO
def baseline():
    baseline_file = 'Applications/EvoChecker-master/data/TAS_1_service_BASELINE/Front'
    infile = 'Applications/EvoChecker-master/models/TAS_1_service_umc.prism'
    os.makedirs(f'Applications/EvoChecker-master/data/TAS_1_service_BASELINE', exist_ok=True)
    prism_caller.properties = ['\'R{"model_drift"}=? [ C<=200 ]\'', '\'R{"total_costs"}=? [ C<=200 ]\'']
    with open(baseline_file, 'w') as b_file:
        for period in itertools.product(range(MIN_FREQUENCY, MAX_FREQUENCY + 1), range(MIN_FREQUENCY, MAX_FREQUENCY + 1), range(MIN_FREQUENCY, MAX_FREQUENCY + 1)):
            b_file.write(prism_caller.compute_baseline(infile, period))
            if period < MAX_FREQUENCY**3:  # TODO MAX_FREQUENCY^3 asumes MIN_FREQUENCY = 1
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
