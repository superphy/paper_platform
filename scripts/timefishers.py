import os
import requests
import numpy as np
import cPickle as pickle

from time import sleep
from datetime import datetime
from random import shuffle

ROOT = os.getenv(
    'SPFY_API',
    'http://localhost:8000/'
)
API = ROOT + 'api/v0/'

# Utility functions.

def _now():
    now = datetime.now()
    now = now.strftime("%Y-%m-%d-%H-%M-%S-%f")
    return now

# Result class.

class Result:
    def __init__(self):
        self.x_values = []
        self.y_values = []

    def update(self, x, y):
        self.x_values.append(x)
        self.y_values.append(y)

    def as_np(self):
        return np.array([self.x_values, self.y_values])

# Calling functions.

def _find_rl(attr):
    if attr[0] == 'O':
        return 'http://purl.obolibrary.org/obo/GENEPIO_0001076'
    elif attr[0] == 'H':
        return 'http://purl.obolibrary.org/obo/GENEPIO_0001077'
    else:
        raise Exception('_find_rl() couldnt find relation for {0}'.format(attr))

def _run_gc(attr_a, attr_b, target):
    """
    POSTs the comparison and retrieves its runtime.
    """
    rl_a = _find_rl(attr_a)
    rl_b = _find_rl(attr_b)

    groups = [
        [
            {
                'negated': False,
                'relation': rl_a,
                'attribute': attr_a,
                'logical': None
            }
        ],
        [
            {
                'negated': False,
                'relation': rl_b,
                'attribute': attr_b,
                'logical': None
            }
        ]
    ]
    data = {
        'groups': groups,
        'target': target
    }
    print(data)
    # POST and get the jobid from Spfy.
    jobid = requests.post(API + 'newgroupcomparison', json=data).text
    print("jobid", jobid)
    # Sleep at least 1 second.
    sleep(1)
    try:
        # Loop until complete.
        while requests.get(API + 'results/' + jobid).json() == unicode('pending'):
            # The length we sleep doesn't matter, as timing is retrieved directly
            # from RQ.
            print "sleeping"
            sleep(4)
        # Grab the result.
        r = requests.get(API + 'results/' + jobid).json()
        print(r)
        # Tell me how many rows (ie. how many found targets) there were.
        size_targets = len(r['index'])
        # Find the number of genoems for a given attribute.
        row = r['data'][0]
        size_attr_a = row[3] + row[4]
        size_attr_b = row[5] + row[6]
        # Request the time it took to run, in seconds.
        sec = requests.get(API + 'timings/' + jobid).text
    except:
        # Either:
        # 1) data is empty. This can be due to a small db.
        # 2) some other error. Likely something timed out.
        size_targets = 0
        size_attr_a = 0
        size_attr_b = 0
        sec = 0
    ret = (size_attr_a, size_attr_b, size_targets, sec)
    print(ret)
    return ret

def _attr_gc():
    """
    analysis run-time / throughput with different levels of parallelization
    particularly for statistical tests
    should do a 1 genome = X number VFs, Y number of genomes for Y*X retrieval/analysis
    """
    # Get all H-Types in the database.
    h_types = requests.get(API + 'get_attribute_values/type/http://purl.obolibrary.org/obo/GENEPIO_0001077').json()
    # This is a weird json format due to the Human-Readable conversion, convert it to a simple list.
    h_types = h_types.values()
    # Get all O-Types in the database.
    o_types = requests.get(API + 'get_attribute_values/type/http://purl.obolibrary.org/obo/GENEPIO_0001076').json()
    o_types = o_types.values()

    l = h_types + o_types
    # Rm unsuitable attributes.
    l = [s for s in l if s[0] in ('O', 'H')]
    print(l)
    return l

def time_gc(c=None):
    attributes = _attr_gc()
    r = Result()
    raws = []
    targets = ('https://www.github.com/superphy#AntimicrobialResistanceGene', 'https://www.github.com/superphy#VirulenceFactor')

    # Shuffle elements if a count is specified.
    if c:
        shuffle(attributes)

    # Loop.
    for target in targets:
        p = 0
        q = 1
        while p <= len(attributes) - 2:
            while q <= len(attributes) - 1:
                st = _run_gc(attributes[p], attributes[q], target)
                attr_x_targets = (st[0] + st[1]) * st[2]
                # Update our main Result instance with the values.
                r.update(attr_x_targets, st[3])
                # Also saves the raws for writing out.
                raws.append(st + (attributes[p], attributes[q], target))
                q += 1
                # break condition if only running a certain number of comparisons.
                if c:
                    c -= 1
                    if c == 0:
                        return raws, r.as_np()
            p += 1
            q = p + 1
    return raws, r.as_np()

def main(c=None):
    now = _now()
    raws, array = time_gc(c)
    pickle.dump(raws, open(now + '_raws.p', "wb" ))
    pickle.dump(array, open(now + '_array.p', "wb" ))

if __name__ == '__main__':
    main()
