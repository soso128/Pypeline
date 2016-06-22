import yaml
import card_edit as cd
import re
from itertools import product, chain
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
    # Iterate over the cartesian product of 
    # parameters in the param card
    param_prod = (dict(zip(param_info.keys(), x)) for x in 
                  product(*[make_list(param_info[k]) for k in param_info.keys()]))
    for p in param_prod:
        par_name = cd.param_card_edit(p, proc_info['model'], out_dir)
        # Launch the run
        run_events(out_dir, par_name, cluster_info) 

def run_events(jobdir, par_name, cluster):
    submit_command = ['./run_madgraph.sh', jobdir, par_name]
    # If cluster, specify the cluster options
    if cluster != None:
        submit_command = ['bsub'] + list(chain(*[['-' + c, str(cluster[c])] 
                                    for c in cluster])) + submit_command
    print(submit_command)
    call(submit_command)

script_from_yaml("../input/input.yaml")
        
