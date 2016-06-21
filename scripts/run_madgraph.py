import yaml
import card_edit as cd
from itertools import product, izip
from Subprocess import call

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
    proc_name = ''
    for p in proc_info:
        proc_suffix += re.sub("[~>]", '', re.sub('\s', '_', parameters[p]))
        proc_suffix += '_'
    out_dir = jobdir + proc_suffix.rstrip('_')
    call(i['mkdir', '-p'], out_dir)
    # Edit the proc card and copy it into job dir
    cd.edit_proc_card(proc_info, out_dir)
    # Edit the run card and copy it into job dir
    cd.edit_run_card(run_info, jobdir)
    # Iterate over the cartesian product of 
    # parameters in the param card
    param_prod = (dict(izip(param_info, x)) for x in 
                  product(*param_info.itervalues()))
    for p in param_prod:
        par_name = cd.edit_param_card(p, proc_info['model'], jobdir)
        # Launch the run
        run_events(jobdir, par_name, cluster_info) 

def run_events(jobdir, par_name, cluster):
    submit_command = ['./launch_madgraph.py', jobdir, par_name]
    # If cluster, specify the cluster options
    if cluster != None:
        submit_command = ['bsub'] + list(chain([c, '-' + cluster[c]] 
                                    for c in cluster)) + submit_command
    call(submit_command)
        
