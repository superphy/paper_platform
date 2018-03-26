import os
import time
import random
import subprocess
import requests
import numpy as np

from time import sleep
from bokeh.plotting import figure, show, output_file

GENOME_POOL = os.getenv(
    'GENOME_POOL',
    'data/'
)

ROOT = os.getenv(
    'SPFY_API',
    'https://localhost:9000/'
)
API = ROOT + 'api/v0/'

def _plot(x):
    pass

def _spfy(list_genomes):
    pass

def _run_gc(rl_a, attr_a, rl_b, attr_b, target):
    """
    POSTs the comparison and retrieves its runtime.
    """
    groups = [
        [
            {
                'negated': 'false',
                'relation': rl_a,
                'attribute': attr_a,
                'logical': 'null'
            }
        ],
        [
            {
                'negated': 'false',
                'relation': rl_b,
                'attribute': attr_b,
                'logical': 'null'
            }
        ]
    ]
    data = {
        'groups': groups,
        'target': target
    }
    # POST and get the jobid from Spfy.
    jobid = requests.post(API + 'newgroupcomparison')

    # Loop until complete.
    while requests.get(API + 'results/' + jobid) == 'pending':
        # The length we sleep doesn't matter, as timing is retrieved directly
        # from RQ.
        sleep(4)
    # Grab the result.
    r = requests.get(API + 'results/' + jobid)
    # Tell me how many rows (ie. how many found targets) there were.
    size_targets = len(r['index'])
    # Find the number of genoems for a given attribute.
    row = r['data'][0]
    size_attr_a = row[3] + row[4]
    size_attr_b = row[5] + row[6]

    # Request the time it took to run, in seconds.
    sec = requests.get(API + 'timings/' + jobid)
    return (size_attr_a, size_attr_b, size_targets, sec)

def _spfy_gc():
    """
    analysis run-time / throughput with different levels of parallelization
    particularly for statistical tests
    should do a 1 genome = X number VFs, Y number of genomes for Y*X retrieval/analysis
    """
    # Get all H-Types in the database.
    h_types = requests.get(API + 'get_attribute_values/type/http://purl.obolibrary.org/obo/GENEPIO_0001077')
    # This is a weird json format due to the Human-Readable conversion, convert it to a simple list.
    h_types = h_types.values()
    # Get all O-Types in the database.
    o_types = requests.get(API + 'get_attribute_values/type/http://purl.obolibrary.org/obo/GENEPIO_0001076')
    o_types = o_types.values()

    pass

def _bap(list_genomes):
    # BAP throws an error without KmerFinder.
    r = subprocess.check_call("""docker run -ti --rm -w /workdir -v $(pwd):/workdir    cgetools BAP --dbdir /usr/src/cgepipeline/test/databases  --services KmerFinder,ResFinder,VirulenceFinder  --fa /usr/src/cgepipeline/test/test.fa""", shell=True)
    return True

def _time(func, list_genomes):
    '''func provided should block until complete.
    '''
    start_time = time.time()
    func(list_genomes)
    stop_time = time.time()
    elapsed_time = stop_time - start_time
    return elapsed_time

def _seed_genomes(size):
    st = set()
    pick = ''
    for i in range(size):
        while pick in st:
            pick = random.choice(os.listdir(GENOME_POOL))
        st.add(pick)
    return list(st)

class Result:
    def __init__(self):
        self.x_values = []
        self.y_values = []

    def update(self, x, y):
        self.x_values.append(x)
        self.y_values.append(y)

    def as_np(self):
        return np.array([self.x_values, self.y_values])

def _timing(func, seeds):
    r = Result()
    for list_genomes in seeds:
        # x-axis is the number of files.
        x = len(list_genomes)
        # y-axis is the execution time.
        y = _time(func, list_genomes)
        r.update(x,y)
    return r.as_np()

def main(start=1, stop=22, step=5):
    # Create groups of seed genomes.
    seeds = [_seed_genomes(i) for i in range(start,stop,step)]
    # Run timings
    r_spfy = _timing(_spfy, seeds)
    r_bap = _timing(_bap, seeds)

if __name__ == '__main__':
    main()
