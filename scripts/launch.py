import run_madgraph as rm
from sys import argv

# Get the card name
card = argv[1]

# Get the value of truncate (default 0)
truncate = 0 if len(argv) < 2 else int(argv[2])

rm.script_from_yaml(card, truncate = truncate)
