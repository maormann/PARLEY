import os
import re
import sys
import subprocess

prism_bin = 'Applications/prism/bin/prism' if sys.platform == "darwin" else 'prism'  # use local prism if not OS X
properties = ('\'P=?[F(x=9 & y=9 & crashed=0)]\'', '\'R{"cost"}=?[C<=100]\'')
command = f'{prism_bin} -maxiters 50000 out.prism -pf '

# evolve_pattern_s1 = re.compile(r'evolve (int decision_.*s1)\[\d+..\d+\];')
# evolve_pattern_s2 = re.compile(r'evolve (int decision_.*s2)\[\d+..\d+\];')
# evolve_pattern_s3 = re.compile(r'evolve (int decision_.*s3)\[\d+..\d+\];')


def compute_baseline(infile, period):
    with open(infile, 'r') as file:
        file_content = file.read()
        file_content = re.sub(r'evolve (int decision_.*s1)\[\d+..\d+\];',
                              r'const \1 = ' + str(period[0]) + r';',
                              file_content)
        file_content = re.sub(r'evolve (int decision_.*s2)\[\d+..\d+\];',
                              r'const \1 = ' + str(period[1]) + r';',
                              file_content)
        file_content = re.sub(r'evolve (int decision_.*s3)\[\d+..\d+\];',
                              r'const \1 = ' + str(period[2]) + r';',
                              file_content)
        with open('out.prism', 'w') as tmp_file:
            tmp_file.write(file_content)
            # for line in file:
            #     # replace all evolves to constants
            #     evolve_constant_s1 = re.match(evolve_pattern_s1, line)
            #     evolve_constant_s2 = re.match(evolve_pattern_s2, line)
            #     evolve_constant_s3 = re.match(evolve_pattern_s3, line)
            #     if evolve_constant_s1:
            #         tmp_file.write(f'const {evolve_constant_s1.group(1)} = {period[0]};\n')
            #     elif evolve_constant_s2:
            #         tmp_file.write(f'const {evolve_constant_s2.group(1)} = {period[1]};\n')
            #     elif evolve_constant_s3:
            #         tmp_file.write(f'const {evolve_constant_s3.group(1)} = {period[2]};\n')
            #     else:
            #         tmp_file.write(line)
    resultline = ''
    for prop, i in zip(properties, range(0, len(properties))):
        # Execute the command and capture the output
        try:
            result = subprocess.run(
                command + prop,
                stdout=subprocess.PIPE,  # Capture standard output
                stderr=subprocess.PIPE,  # Capture standard error
                shell=True,  # Use shell for command execution
                universal_newlines=True,  # Return output as text (str)
            )
            # Check if the command was successful (return code 0)
            if result.returncode == 0:
                # Capture standard output and standard error
                stdout = result.stdout

                # Print or process the captured output as needed
                # Find and print the line that starts with "Result:"
                lines = stdout.splitlines()
                for line in lines:
                    if line.startswith("Result:"):
                        resultline += line.split(' ')[1] + '\t'
                        # print("PRISM: " + prop + ' = ' + str(result))
                        break  # Stop searching after finding the first matching line
            else:
                print(f"Command failed with return code {result.returncode}")
                print(result.stdout)
                print(result.stderr)

        except Exception as e:
            print(f"An error occurred: {e}")
    # os.remove("out.prism")
    return resultline
