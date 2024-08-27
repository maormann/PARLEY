import os

import umc_synthesis
import prism_caller
import run_evochecker
import evaluation
import plot_fronts
import itertools

MAX_REPLICATIONS = 10

MIN_FREQUENCY = 0
MAX_FREQUENCY = 15

URS = ('s1', 's2', 's3')  # Uncertainty Reduction Services

constains = [
    ("0_0_1_s3", 0),
    ("0_1_1_s3", 0),
    ("0_2_1_s3", 0),
    ("1_0_1_s3", 0),
    ("1_1_1_s3", 0),
    ("1_2_1_s3", 0),
    ("2_0_1_s3", 0),
    ("2_1_1_s3", 0),
    ("2_2_1_s3", 0),
    ("0_1_0_s2", 0),
    ("0_1_1_s2", 0),
    ("0_1_2_s2", 0),
    ("1_1_0_s2", 0),
    ("1_1_1_s2", 0),
    ("1_1_2_s2", 0),
    ("2_1_0_s2", 0),
    ("2_1_1_s2", 0),
    ("2_1_2_s2", 0),
    ("1_0_0_s1", 0),
    ("1_0_1_s1", 0),
    ("1_0_2_s1", 0),
    ("1_1_0_s1", 0),
    ("1_1_1_s1", 0),
    ("1_1_2_s1", 0),
    ("1_2_0_s1", 0),
    ("1_2_1_s1", 0),
    ("1_2_2_s1", 0),
]


def models():
    infile = os.getenv('PARLEY_MODEL_FILE_IN', 'Applications/EvoChecker-master/models/TAS.prism')
    outfile = os.getenv('PARLEY_MODEL_FILE_OUT', 'Applications/EvoChecker-master/models/TAS_umc.prism')
    umc_synthesis.manipulate_prism_model(infile,
                                         outfile,
                                         before_actions=['set_alarm_sender'],
                                         after_actions=['start_UAC'],
                                         possible_decisions=[MIN_FREQUENCY, MAX_FREQUENCY],
                                         urs=URS,
                                         controller=umc_synthesis.add_tas_controller,
                                         add_trun_module=False)

    umc_synthesis.decision_constrains(outfile, constains)


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


def fronts():
    plot_fronts.plot_tas_pareto_front()


def main():
    models()
    # baseline()
    # evo_checker()
    # fronts()
    # evaluation.main()


if __name__ == '__main__':
    os.makedirs('plots/fronts', exist_ok=True)
    os.makedirs('plots/box-plots', exist_ok=True)
    main()
