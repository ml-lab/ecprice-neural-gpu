import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import collections
#from kube import run_openai_cluster as run
import generic_run as run
#from kube import run

LABEL = 'August-32-expr'

#run.parser.set_defaults(session='August-31-expr6')

param_sets = [[('random_seed', seed),
               ('max_steps', 200000),
               ('forward_max', 201),
               ('nmaps', nm),
               ('task', task),
               ('time_till_eval', 4),
               ('progressive_curriculum', pc),
               ]
              for seed in range(2)
              for task in ['bexprp,bexpr', 'bexprp,qexprp,exprp',
                           'bexprs', 'bexprp,bexprps', 'bexprs,qexprs,exprs',
                           #'mul2,mul3,mul4,mul5,mul6,mul7,mul8,mul9,mul10'
              ]
              for nm in [128,256]
              for pc in [5]
              ]

print "Running", len(param_sets), "jobs"
# Remove Nones 
param_sets = [[p for p in ps if p] for ps in param_sets]

param_sets = map(collections.OrderedDict, param_sets)
run.parser.set_defaults(label=LABEL)
#print len(param_sets)
run.main(param_sets)
