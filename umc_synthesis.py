import re
import os
import shutil


def manipulate_prism_model(input_path, output_path,
                           possible_decisions=[0, 3],
                           decision_variables=[],
                           before_actions=[],
                           after_actions=[],
                           urs=('urs'),  # Uncertainty Reduction Services
                           controller=None,
                           module_name='Knowledge',
                           add_trun_module=True
                           ):
    if os.path.abspath(input_path) == os.path.abspath(output_path):
        raise ValueError("Input and output files cannot be the same.")

    assert len(urs) >= 1

    shutil.copyfile(input_path, output_path)

    variables, beliefs = get_variables(input_path, decision_variables)

    # add_transition_to_module(output_path, beliefs, module_name)
    if controller is None:
        add_periodic_controller(output_path, possible_decisions, variables, urs)
    else:
        controller(output_path, possible_decisions, variables, urs)
    if add_trun_module:
        add_turn(output_path, before_actions, after_actions, urs)


def get_variables(prism_model_path, decision_variables):
    # get all int constants
    int_constants_pattern = re.compile(r'const\s+int\s+(\w+)\s*=\s*(-?\s*\d+)\s*;')
    int_constants = {}

    with open(prism_model_path, 'r') as prism_model_file:
        # Process the file line by line
        for line in prism_model_file:
            # Match constants in each line
            matches = int_constants_pattern.finditer(line)
            for match in matches:
                int_constants[match.group(1)] = int(match.group(2).replace(" ", ""))

    int_variable_declaration_pattern = re.compile(r'(\w+)\s*:\s*\[(-?\s*\w+)\s*\.\.\s*(-?\s*\w+)\]\s*init\s*(-?\s*\w+)\s*;')
    _vars = []
    _bel = []

    with open(prism_model_path, 'r') as prism_model_file:
        # Process the file line by line again
        for line in prism_model_file:
            # Match variables in each line
            matches = int_variable_declaration_pattern.finditer(line)
            for match in matches:
                if match.group(1)[-3:] == 'hat':
                    _bel.append(match.group(1))
                elif match.group(1) not in decision_variables:
                    continue
                lower_limit = __get_limit(match.group(2).replace(" ", ""), int_constants)
                upper_limit = __get_limit(match.group(3).replace(" ", ""), int_constants)
                _vars.append([match.group(1), lower_limit, upper_limit])

    return _vars, _bel


def __get_limit(string, constants):
    if not string.lstrip("-").isdigit():
        return constants[string]
    else:
        return int(string)


def add_transition_to_module(file_path, beliefs, module_name='Knowledge'):
    # figure out what the transition should look like
    new_transition = '  [update] true ->'
    for identifier in beliefs:
        new_transition += f' ({identifier}\'={identifier[:-3]}) &'
    # remove the last '&'
    new_transition = new_transition[:-2]
    new_transition += ';'

    # Identify the position of the module declaration
    module_declaration_pattern = re.compile(fr'(?<=module {module_name}).*(?=endmodule)', re.DOTALL)
    file_content = ''
    with open(file_path, 'r') as file:
        file_content = file.read()
    module_content_old_match = module_declaration_pattern.search(file_content)
    if module_content_old_match is None:
        print(f"Module '{module_name}' not found in the model.")
        return  # TODO maybe throw an error
    module_content_old = module_content_old_match.group()
    # append the new transition to the module
    module_content_new = f"{module_content_old}{new_transition}\n"
    # overwrite the file with the new content
    with open(file_path, 'w') as file:
        file.write(file_content.replace(module_content_old, module_content_new))


def add_periodic_controller(file_path, possible_decisions, variables, urs):
    # write decision variables
    combinations = generate_combinations_list(variables)
    __add_controller_prefix(file_path, possible_decisions, combinations, variables, urs)
    with open(file_path, 'a') as file:
        for u_reduction_service in urs:
            file.write(f'  step_{u_reduction_service} : [{possible_decisions[0]}..{possible_decisions[1]}] init {possible_decisions[0]};\n')
    transitions = ['no_update', 'update']
    decisions = ['step<decision', 'step>=decision']
    changes = ['(step\'=step+1)', '(step\'=1)']
    __add_specific_controller(file_path, transitions, decisions, changes, combinations, variables, urs)


def add_tas_controller(file_path, possible_decisions, variables, urs):
    # write decision variables
    combinations = generate_combinations_list(variables)
    __add_controller_prefix(file_path, possible_decisions, combinations, variables, urs)
    with open(file_path, 'a') as file:
        for u_reduction_service in urs:
            file.write(f'  step_{u_reduction_service} : [{possible_decisions[0]}..{possible_decisions[1]}] init {possible_decisions[0]};\n')
    transitions = ['no_update', 'update']
    decisions = ['step<decision', 'step>=decision']
    changes = ['(step\'=step+1)', '(step\'=1)']
    # Generate formulas
    formulas = []
    for transition, decision, change in zip(transitions, decisions, changes):
        for u_reduction_service in urs:
            new_formula = {"name": f'{transition}_{u_reduction_service}', "sub_formulas": []}
            for combination in combinations:
                sub_formula = f'({decision}'
                for var in range(0, len(variables)):
                    sub_formula += '_' + str(combination[var])
                sub_formula += '_' + u_reduction_service
                sub_formula += ')'
                for var in range(0, len(variables)):
                    sub_formula += f' & ({variables[var][0]}={combination[var]})'
                sub_formula = sub_formula.replace('step', f'step_{u_reduction_service}')  # Ditry fix
                new_formula["sub_formulas"].append(sub_formula)
            formulas.append(new_formula)
    with open(file_path, 'a') as file:
        file.write('  urc_s: [0..1] init 0;\n')
        # Write UMC module to endmodule
        for transition, decision, change in zip(transitions, decisions, changes):
            if transition == "update":
                continue
            if transition == "no_update":
                continue
            for u_reduction_service in urs:
                new_line = f'  [{transition}_{u_reduction_service}] f_{transition}_{u_reduction_service} -> {change};\n'
                new_line = new_line.replace('step', f'step_{u_reduction_service}')  # Ditry fix
                file.write(new_line)
        # Additionals
        for u_reduction_service in urs:
            file.write(f"  [{u_reduction_service}_invocation] true -> 1: (step_{u_reduction_service}' = {possible_decisions[0]});\n")
        file.write(f"  [start_URC] urc_s = 0 & step_s1 < {possible_decisions[1]} & step_s2 < {possible_decisions[1]} & step_s3 < {possible_decisions[1]} "
                   f"-> 1: (urc_s' = 1) & (step_s1' = step_s1 + 1 ) & (step_s2' = step_s2 + 1 ) & (step_s3' = step_s3 + 1);\n")  # Not generic
        file.write("  [end_round] urc_s = 1 -> (urc_s' = 0);")
        file.write('endmodule\n\n')
        # Write formulas
        for formula in formulas:
            new_formula = f'formula f_{formula["name"]} = \n'
            for sub_formula in formula["sub_formulas"][:-1]:
                new_formula += f'({sub_formula}) |\n'
            new_formula += f'({formula["sub_formulas"][-1]});\n\n'
            file.write(new_formula)
        file.write('\n')


def add_static_controller(file_path, possible_decisions, variables, urs):
    # write decision variables
    combinations = generate_combinations_list(variables)
    possible_decisions = [0, 1]
    __add_controller_prefix(file_path, possible_decisions, combinations, variables, urs)
    transitions = ['no_update', 'update']
    decisions = ['zero=decision', 'one=decision']
    changes = ['true', 'true']
    __add_specific_controller(file_path, transitions, decisions, changes, combinations, variables, urs)


def __add_specific_controller(file_path, transitions, decisions, changes, combinations, variables, urs):
    with open(file_path, 'a') as file:
        for transition, decision, change in zip(transitions, decisions, changes):
            for combination in combinations:
                for u_reduction_service in urs:
                    new_line = f'  [{transition}_{u_reduction_service}] ({decision}'
                    for var in range(0, len(variables)):
                        new_line += '_' + str(combination[var])
                    new_line += '_' + u_reduction_service
                    new_line += ')'
                    for var in range(0, len(variables)):
                        new_line += f' & ({variables[var][0]}={combination[var]})'
                    new_line += f' -> {change};\n'
                    new_line = new_line.replace('step', f'step_{u_reduction_service}')  # Ditry fix
                    file.write(new_line)

        file.write('endmodule\n\n')


def __add_controller_prefix(file_path, possible_decisions, combinations, variables, urs):
    # write decision variables
    with open(file_path, 'a') as file:
        file.write('\n\n')
        for combination in combinations:
            for u_reduction_service in urs:
                new_line = 'evolve int decision'
                for var in range(0, len(variables)):
                    new_line += '_' + str(combination[var])
                new_line += '_' + u_reduction_service
                new_line += f' [{possible_decisions[0]}..{possible_decisions[1]}];\n'
                file.write(new_line)
        file.write('\nmodule UMC\n')


def add_turn(file_path, before_actions, after_actions, urs):
    with open(file_path, 'a') as file:
        file.write('module Turn\n')
        file.write(f'  t : [0..{len(urs)+1}] init 0;\n')
        # actions that precede
        for action in before_actions:
            file.write(f'  [{action}] (t=0) -> (t\'=1);\n')
        counter = 2
        file.write('\n')
        for u_reduction_service in urs:
            file.write(f'  [no_update_{u_reduction_service}] (t={counter-1}) -> (t\'={counter});\n')
            file.write(f'  [update_{u_reduction_service}] (t={counter-1}) -> (t\'={counter});\n')
            counter += 1
        file.write('\n')
        for action in after_actions:
            file.write(f'  [{action}] (t={counter-1}) -> (t\'=0);\n')
        if len(after_actions) == 0:
            file.write(f'  [] (t={counter-1}) -> (t\'=0);\n')
        file.write('endmodule\n')


def generate_combinations_list(variables):
    result = []

    def generate_combinations_recursive(current_combination, remaining_variables):
        if not remaining_variables:
            result.append(tuple(current_combination))
            return

        current_variable = remaining_variables[0]
        for value in range(current_variable[1], current_variable[2] + 1):
            generate_combinations_recursive(
                current_combination + [value],
                remaining_variables[1:]
            )

    generate_combinations_recursive([], variables)
    return result
