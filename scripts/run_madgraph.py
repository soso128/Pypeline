import yaml
import os
import card_edit as cd
import re
import pathlib
from itertools import product
from subprocess import call, Popen, PIPE
from utils import make_list
from sys import executable

# Reads the yaml card and processes the information
def script_from_yaml(filename, jobdir = "../jobs/", truncate = 2):
    # Read yaml card and put parameters in dictionary
    f = open(filename)
    card = yaml.load(f)
    # New job directory if one wants to keep the files
    if "jobdir" in card:
        jobdir = card["jobdir"]
    # Proc card
    proc_info = None
    if "proc" in card:
        proc_info = card["proc"]
    # Param card
    param_info = None
    if "param" in card:
        param_info = card["param"]
    # Run card
    run_info = None
    if "run" in card:
        run_info = card["run"]
    # Output options
    output_info = None
    if "output" in card:
        output_info = card["output"]
    # If gridpack, get grid_info
    # and update run card if needed
    grid_info = None
    if "gridpack" in card:
        grid_info = card["gridpack"]
        if grid_info["status"] == 0:
            run_info["gridpack"] = "True"
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
        proc_suffix = proc_suffix.replace(',', '_')
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
    # Get the job launch command if cluster
    cluster_command = os.environ["CLUS_LAUNCH"] \
            if cluster_info != None else ""
    # Iterate over the cartesian product of 
    # parameters in the param card
    param_prod = (dict(zip(param_info.keys(), x)) for x in 
                  product(*[make_list(param_info[k]) 
                            for k in param_info.keys()]))
    print(*[make_list(param_info[k]) for k in param_info.keys()])
    job_ids = []
    for p in param_prod:
        par_name = cd.param_card_edit(p, decay_info, proc_info['model'], 
                                      out_dir, truncate = truncate)
        # Launch the run
        par_name = par_name.replace("param_card_", '').replace(".dat", '')
        job_id = run_events(out_dir, par_name, cluster_info, 
                            output_info, grid_info, cluster_command) 
        job_ids.append(job_id)
    # If cluster, launch process checking jobs and cleanup the job directory
    # when all the jobs are done running
    if cluster_info != None:
        time = cluster_info[os.environ["CLUS_TIME"]]
        submit_command = [cluster_command] + list(sum([['-' + c, str(cluster_info[c])] 
                                    for c in cluster_info], []))
        submit_command += [executable] + ["-c"]
        jobpath = str(pathlib.Path(out_dir).resolve())
        python_command = "import check_processes as ch;ch.cleanup_job_dir('{}', [{}], {})".format(
                    jobpath, ','.join(map(str, job_ids)), time)
        submit_command += [python_command]
        print(submit_command)
        call(submit_command)


def run_events(jobdir, par_name, cluster, output, gridpack, clus_command = ""):
    submit_command = ['./run_madgraph.sh']
    # If gridpack, set grid options
    grid_options = {"status": 'g', "dir": 'h'}
    for o in grid_options:
        try:
            submit_command += ["-{}".format(grid_options[o]), format(gridpack[o])]
        except (KeyError, TypeError):
            pass
    # If output (script, etc, ...)
    output_options = {"script": 's', "dir": 'o', "files": 'f'}
    for o in output_options:
        try:
            submit_command += ["-{}".format(output_options[o]), output[o]]
        except (KeyError, TypeError):
            pass
    # If cluster, specify the cluster options
    if cluster != None:
        submit_command = [clus_command] + list(sum([['-' + c, str(cluster[c])] 
                                    for c in cluster], [])) + submit_command
    else:
        submit_command += ["-l", "{}/{}/".format(jobdir,par_name)]
    submit_command += ['-j', jobdir, '-p', par_name]
    print(submit_command)
    p = Popen(submit_command, stdout = PIPE)
    out = p.communicate()[0]
    print(out)
    # Get job ID
    if cluster != None:
        jobid = int(out.split()[1][1:-1])
        return jobid
    return 0
