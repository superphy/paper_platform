import os
import time
import random
import subprocess
import numpy as np

from bokeh.plotting import figure, show, output_file

GENOME_POOL = os.getenv(
    'GENOME_POOL',
    'data/'
)

def _plot(x):
    pass

def _spfy(list_genomes):
    pass

def _spfy_gc():
    # analysis run-time / throughput with different levels of parallelization
    # particularly for statistical tests
    # should do a 1 genome = X number VFs, Y number of genomes for Y*X retrieval/analysis
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
