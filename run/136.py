import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import collections
#from kube import run_openai_cluster as run
import generic_run as run
#from kube import run

LABEL = 'August-04-bigmul2'

param_sets = [[('random_seed', seed),
               ('max_steps', 80000),
               ('forward_max', 201),
               ('nmaps', nm),
               ('task', task),
               ('progressive_curriculum', 2),
               ]
              for seed in range(8)
              for task in ['mul']
              for nm in [256]
              ]

print "Running", len(param_sets), "jobs"
# Remove Nones 
param_sets = [[p for p in ps if p] for ps in param_sets]

param_sets = map(collections.OrderedDict, param_sets)
run.parser.set_defaults(label=LABEL)
#print len(param_sets)
run.main(param_sets)
