import os

import umc_synthesis
import prism_caller
import run_evochecker
import evaluation
import plot_fronts

max_replications = 10


def models():
    infile = f'Applications/EvoChecker-master/models/TAS.prism'
    outfile = f'Applications/EvoChecker-master/models/TAS_umc.prism'
    umc_synthesis.manipulate_prism_model(infile,
                                         outfile,
                                         before_actions=['start_UAC'],
                                         after_actions=['end_round'],
                                         possible_decisions=[1, 10],
                                         module_name='adaptation_MAPE_controller')


def baseline(i):
    baseline_file = f'Applications/EvoChecker-master/data/ROBOT{i}_BASELINE/Front'
    infile = f'Applications/EvoChecker-master/models/model_{i}.prism'
    os.makedirs(f'Applications/EvoChecker-master/data/ROBOT{i}_BASELINE', exist_ok=True)
    with open(baseline_file, 'w') as b_file:
        for period in range(1, 11):
            b_file.write(prism_caller.compute_baseline(infile, period))
            if period < 10:
                b_file.write('\n')
            print('finished baseline map {0}, value {1}'.format(str(i), str(period)))


def evo_checker():
    # invoke EvoChecker
    run_evochecker.simple_run()


def fronts(i):
    for period in range(max_replications):
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
