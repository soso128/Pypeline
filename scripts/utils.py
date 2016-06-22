from re import match
from numpy import arange

# Takes the input for each parameter name and returns
# a list of values
def make_list(yaml_arg):
    yaml_arg = str(yaml_arg).strip()
    # If range, find intermediate values
    range_pattern = r"[0-9]*-[0-9]*\s*[0-9]*"
    if match(range_pattern, yaml_arg):
        bounds, step = yaml_arg.split()
        step = float(step)
        vmin, vmax = map(float, bounds.split('-'))
        vlist = list(arange(vmin, vmax, step)) + [vmax]
        return vlist
    # If not range, return list of values
    values = yaml_arg.split()
    return values
