from time import sleep
from subprocess import call, Popen, PIPE, STDOUT

#Parses the maximal time allowed for the queue and convert in seconds
def convert_time(time):
    if ':' in str(time):
        [hours, minutes] = map(int, time.split(':'))
        return 60 * minutes + 3600 * hours
    return 60 * int(time)


# Check whether all jobs have ran
def check_if_finished(ids, total_time, nsteps = 50):
    total_time = convert_time(total_time)
    pause = total_time/nsteps
    n = 0
    ids = set(ids)
    while n < nsteps and ids:
        p = Popen(["bjobs"], stdout = PIPE, stderr = STDOUT)
        output = (p.communicate()[0]).decode('utf-8').strip()
        running_ids = set([int(line.split()[0]) 
                           for line in output.split('\n')[1:-1]])
        ids = ids.intersection(running_ids)
        n += 1
        sleep(pause)
    if ids:
        raise RunTimeError("Too little time ({}) allowed for the queue.The jobs\
                           {} had to be killed.".format(total_time, ids))
    return True

# Cleans up job directory
def cleanup_job_dir(jobdir, ids, total_time, nsteps = 50):
    finished = check_if_finished(ids, total_time, nsteps = nsteps)
    if finished:
        call(["rm", "-r", "{}".format(jobdir)])
