import os
import matplotlib.pyplot as plt


def pareto_front(data):
    pareto_data = []
    for x, y in data:
        if not is_dominated(x, y, pareto_data):
            pareto_data.append((x, y))
    return pareto_data


def is_dominated(x, y, data):
    for other_x, other_y in data:
        if other_x >= x and other_y <= y:
            return True
    return False


def tas_pareto_front(data):
    pareto_data = []
    for i in range(len(data)):
        dominated = False
        for j in range(len(data)):
            if i != j and data[i][0] >= data[j][0] and data[i][1] >= data[j][1]:
                # print(data[j], "dominates", data[i])
                dominated = True
                break
        if not dominated:
            pareto_data.append(data[i])
    return pareto_data


def plot_tas_pareto_front():
    data = []
    filename = ''
    file_path = 'Applications/EvoChecker-master/data/TAS/NSGAII'
    for f_name in os.listdir(file_path):
        if "Front" in f_name:
            filename = f_name
    with open(os.path.join(file_path, filename), 'r') as file:
        next(file)
        for line in file:
            x, y = map(float, line.strip().split('\t'))
            data.append((x, y))

    pareto_data = tas_pareto_front(data)

    x_values = [x for y, x in pareto_data]
    y_values = [y for y, x in pareto_data]

    data = []
    with open(f'Applications/EvoChecker-master/data/TAS_BASELINE/Front', 'r') as file:
        for line in file:
            x, y = map(float, line.strip().split('	'))
            data.append((x, y))

    baseline_data = tas_pareto_front(data)

    x_values_b = [x for y, x in baseline_data]
    y_values_b = [y for y, x in baseline_data]

    plt.figure(figsize=(8, 6))

    plt.scatter(x_values, y_values, color='blue', label='URC')

    # Add red crosses for the baseline
    plt.scatter(x_values_b, y_values_b, color='red', marker='x', label='Baseline')

    plt.xlabel('Time per alarm')
    plt.ylabel('Cost')
    output_filename = f'TAS'
    plt.title(output_filename)
    plt.xlim(1, 1.3)
    plt.ylim(0, 200)
    plt.legend()
    plt.grid(True)

    # Save the plot as an image file
    plt.savefig('plots/fronts/' + output_filename + '.pdf')
    plt.close()


def plot_pareto_front(m=10, replication=0, header=True):
    data = []
    filename = ''
    file_path = f'Applications/EvoChecker-master/data/ROBOT{m}_REP{replication}/NSGAII/'
    for f_name in os.listdir(file_path):
        if "Front" in f_name:
            filename = f_name
    with open(file_path + filename, 'r') as file:
        if header:
            next(file)  # Skip the header row
        for line in file:
            x, y = map(float, line.strip().split('\t'))
            data.append((x, y))

    pareto_data = pareto_front(data)

    x_values = [x for x, y in pareto_data]
    y_values = [y for x, y in pareto_data]

    data = []
    with open(f'Applications/EvoChecker-master/data/ROBOT{m}_BASELINE/Front', 'r') as file:
        for line in file:
            x, y = map(float, line.strip().split('	'))
            data.append((x, y))

    baseline_data = pareto_front(data[:20])

    x_values_b = [x for x, y in baseline_data]

    y_values_b = [y for x, y in baseline_data]

    plt.figure(figsize=(8, 6))

    plt.scatter(x_values, y_values, color='blue', label='URC')

    # Add red crosses for the baseline
    plt.scatter(x_values_b, y_values_b, color='red', marker='x', label='Baseline')

    plt.xlabel('Probability of mission success')
    plt.ylabel('Cost')
    output_filename = f'robot{m}_rep{replication}'
    plt.title(output_filename)
    plt.xlim(1, 0.2)
    plt.ylim(0, 200)
    plt.legend()
    plt.grid(True)

    # Save the plot as an image file
    plt.savefig('plots/fronts/' + output_filename + '.pdf')
    plt.close()
