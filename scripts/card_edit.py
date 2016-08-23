from subprocess import call
from utils import Tree
from copy import deepcopy

def proc_card_edit(parameters, out_dir, proc_dir = '../Cards'):
    proc_suffix = ''
    param = deepcopy(parameters)
    # If several processes
    param["process"] = param["process"].replace('--', "\n\tadd process ")
    print(param["process"])
    # Restrictions
    if "restriction" in parameters:
        param["model"] += "-{}".format(param["restriction"])
    with open("{}/proc_card_mg5.dat".format(proc_dir)) as card:
        content = card.read()
        for p in param:
            content = content.replace("${}".format(p), param[p])
        output_name =  out_dir + '/proc_card_mg5.dat'
        print(content, file = open(output_name, 'w'))
    return out_dir

def param_card_edit(par_expr, decays, model_name, output_dir, param_dir = '../Cards', truncate = 2):
    # Resolve the symbolic expressions
    parameters = Tree.convert_parameters(par_expr)
    # Get parameter name
    par_suffix = ''
    for p in sorted(parameters.keys()):
        # Truncate values to n decimals in file name
        truncate_string = "{{0:.{}f}}".format(truncate)
        value_name = truncate_string.format(parameters[p])
        par_suffix += "{}{}_".format(p, value_name.replace(
            '.', 'p')).replace('p0_', '_').replace(' ', '')
    par_file_name = 'param_card_{}.dat'.format(par_suffix.rstrip('_'))
    # Build new card
    new_card = ''
    with open("{}/param_card_{}.dat".format(param_dir, model_name)) as card:
        for c in card:
            newstring = c
            comments = c.strip().split('#')
            # Change particle properties
            if len(comments) == 2:
                name = comments[1].strip()
                if name in parameters.keys():
                    leading_spaces = len(c) - len(c.lstrip(' '))
                    newstring = ' ' * leading_spaces + " ".join(
                        comments[0].split()[:-1]) + ' ' + str(parameters[name])\
                            + ' # ' + comments[1] + '\n'
            # Change decay properties
            if decays != None:
                if c.startswith("DECAY"):
                    pid = int(c.split()[1])
                    if pid in decays.keys():
                        dsplit = decays[pid].split()
                        br = dsplit[0]
                        products = " ".join(dsplit[1:])
                        nbody = len(dsplit[1:])
                        newstring += "   {}   {}   {}\n".format(
                            br, nbody, products)
            new_card += newstring
        # Print new card to file
        par_path = "{}/{}".format(output_dir, par_file_name)
        print(new_card, file = open(par_path, 'w'))
    return par_file_name

def run_card_edit(parameters, output_dir, run_dir = '../Cards'):
    new_card = ''
    with open("{}/run_card.dat".format(run_dir)) as card:
        for c in card:
            newstring = c
            result = c.split('=', 1)
            if len(result) == 2:
                name = result[1].split('!', 1)[0].strip()
                if name in parameters.keys():
                    leading_spaces = len(c) - len(c.lstrip())
                    newstring = ' ' * leading_spaces + str(parameters[name])\
                            + ' = ' + result[1]
            new_card += newstring
        print(new_card, file = open("{}/run_card.dat".format(output_dir), 'w'))

def pythia6_card_edit(parameters, output_dir, pythia6_dir = '../Cards/'):
    if parameters != None:
        with open("{}/pythia6_card.dat".format(pythia6_dir)) as card:
            content = card.read()
            for p in parameters:
                content += "      {}={}".format(p, parameters[p])
            print(content, file = open("{}/pythia_card.dat".format(output_dir), 'w'))

def delphes_card_edit(delphes_card, output_dir):
    if delphes_card != None:
        call(['cp', delphes_card, output_dir + '/delphes_card.dat'])
