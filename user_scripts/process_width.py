#!/cluster/Apps/Python/2.7.7/bin/python

import sys

param_name = sys.argv[1]

#Get MDM and delta
split_param = param_name.split('_')
mx = -1
delta = -1
width = -1
for s in split_param:
    if s.startswith("MX"):
        mx = s[2:].replace('p', '.')
    if s.startswith("delta"):
        delta = s[5:].replace('p', '.')

with open("width.txt") as w:
    width = w.readline()

with open("newwidth_{}.txt".format(param_name), 'w') as fout:
    print >> fout, " ".join([mx.strip(), delta.strip(), width.strip()])
