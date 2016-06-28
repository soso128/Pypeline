import yaml
import card_edit as cd
import re
from itertools import product
from subprocess import call
from utils import make_list

# Reads the yaml card and processes the information
def script_from_yaml(filename, jobdir = "../jobs/"):
    # Read yaml card and put parameters in dictionary
    f = open(filename)
    card = yaml.load(f)
    proc_info = card["proc"]
    param_info = card["param"]
    run_info = card["run"]
    output_info = card["output"]
    # Possible decays
    decay_info = None
    if "decays" in card:
        decay_info = card["decays"]
    # Pythia 6 info
    pythia6_info = None
    if "pythia6" in card:
        pythia6_info = card["pythia6"]
    # Delphes info
    delphes_info = None
    if "delphes" in card:
        delphes_info = card["delphes"]
    # Cluster options
    cluster_info = None
    if "cluster" in card:
        cluster_info = card["cluster"]
    # Make a job directory with name model_process_output
    proc_suffix = ''
    for p in sorted(proc_info.keys()):
        proc_suffix += re.sub("[~>]", '', re.sub('\s', '_', proc_info[p]))
        proc_suffix += '_'
    out_dir = jobdir + proc_suffix.rstrip('_')
    call(['mkdir', '-p', out_dir])
    # Edit the proc card and copy it into job dir
    cd.proc_card_edit(proc_info, out_dir)
    # Edit the run card and copy it into job dir
    cd.run_card_edit(run_info, out_dir)
    # Edit the pythia6 card and copy it into job dir
    cd.pythia6_card_edit(pythia6_info, out_dir)
    # Edit the delphes card and copy it into job dir
    cd.delphes_card_edit(delphes_info, out_dir)
    # Iterate over the cartesian product of 
    # parameters in the param card
    param_prod = (dict(zip(param_info.keys(), x)) for x in 
                  product(*[make_list(param_info[k]) for k in param_info.keys()]))
    for p in param_prod:
        par_name = cd.param_card_edit(p, decay_info, proc_info['model'], out_dir)
        # Launch the run
        run_events(out_dir, par_name, cluster_info, output_info) 

def run_events(jobdir, par_name, cluster, output):
    submit_command = ['./run_madgraph.sh']
    # If output (script, etc, ...)
    output_options = {"script": 's', "dir": 'o', "files": 'f'}
    for o in output_options:
        try:
            submit_command += ["-{}".format(output_options[o]), output[o]]
        except KeyError:
            pass
    # If cluster, specify the cluster options
    if cluster != None:
        submit_command = ['bsub'] + list(sum([['-' + c, str(cluster[c])] 
                                    for c in cluster], [])) + submit_command
    else:
        submit_command += ["-l", "{}/{}/".format(jobdir,par_name)]
    submit_command += [jobdir, par_name]
    print(submit_command)
    call(submit_command)

script_from_yaml("../input/input.yaml")
        
