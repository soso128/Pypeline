import re
from subprocess import call

def proc_card_edit(parameters, out_dir, proc_dir = '../Cards'):
    proc_suffix = ''
    with open("{}/proc_card_mg5.dat".format(proc_dir)) as card:
        content = card.read()
        for p in parameters:
            content = content.replace("${}".format(p), parameters[p])
        output_name =  out_dir + '/proc_card_mg5.dat'
        print(content, file = open(output_name, 'w'))
    return out_dir

def param_card_edit(parameters, decays, model_name, output_dir, param_dir = '../Cards'):
    with open("{}/param_card_{}.dat".format(param_dir, model_name)) as card:
        par_suffix = ''
        content = card.read()
        for p in sorted(parameters.keys()):
            content = re.sub(r"([^\\n]*)\s[^\\s]*\s# {0} (.*)".format(p), 
                             r"\1 {1} # {0} \2".format(p, parameters[p]), 
                             content)
            par_suffix += "{}{}_".format(p, str(parameters[p]).replace(
                '.', 'p')).replace('p0_', '_').replace(' ', '')
        for p in sorted(decays.keys()):
            dsplit = decays[p].split()
            br = dsplit[0]
            products = " ".join(dsplit[1:])
            nbody = len(dsplit[1:])
            d_string = r"(DECAY\s*{}[^\n]*\n)".format(p)
            content = re.sub(d_string, r"\1   {}   {}  {}\n".format(
                br, nbody, products), content)
        par_file_name = 'param_card_{}.dat'.format(par_suffix.rstrip('_'))
        par_path = "{}/{}".format(output_dir, par_file_name)
        print(content, file = open(par_path, 'w'))
    return par_file_name

def run_card_edit(parameters, output_dir, run_dir = '../Cards'):
    with open("{}/run_card.dat".format(run_dir)) as card:
        content = card.read()
        for p in parameters:
            content = re.sub(r"(\s*)[0-9\.]*(\s*)=(\s*){0}\s([^\n]*)\n".format(p), 
                             r"\1 {1}\2=\3{0} \4\n".format(p, parameters[p]), content)
        print(content, file = open("{}/run_card.dat".format(output_dir), 'w'))

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
