import os
import time
import random
import subprocess
import requests
import numpy as np
import cPickle as pickle

from time import sleep
from datetime import datetime
from zipfile import ZipFile

GENOME_POOL = os.getenv(
    'GENOME_POOL',
    'data/'
)

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

def _seed_genomes(size):
    def _pick():
        f = os.path.join(GENOME_POOL, random.choice(os.listdir(GENOME_POOL)))
        return f
    st = set()
    pick = _pick()
    for i in range(size):
        while pick in st:
            pick = _pick()
        st.add(pick)
    return list(st)

# Result classes.

class Result:
    def __init__(self):
        self.x_values = []
        self.y_values = []

    def update(self, x, y):
        self.x_values.append(x)
        self.y_values.append(y)

    def as_np(self):
        return np.array([self.x_values, self.y_values])

class BarResult:
    def __init__(self, list_sizes):
        self.list_sizes = list_sizes
        self.subtasks = None
        self.data = {
            'size_increments': list_sizes
        }

    def update(self, timing):
        '''Variable "timing" should be of shape {sample_size(str): list_subtask_times(list)}
        '''
        assert isinstance(timing, dict)
        self.data.update(timing)

# Calling functions.

def _run_spfy(list_genomes):
    '''POSTs to Spfy's API.
    '''
    # Zip files if more than 1 genome.
    if isinstance(list_genomes, list):
        if len(list_genomes)>1:
            # Zip the files.
            name = _now() + '.zip'
            with ZipFile(name, 'w') as z:
                for f in list_genomes:
                    z.write(f)
            # File payload.
            files = {'file': open(name, 'rb')}
        else:
            files = {'file': open(list_genomes[0], 'rb')}
    else:
        files = {'file': open(list_genomes, 'rb')}

    # Options payload.
    data = {
        'options.pi': 90,
        'options.amr': True,
        'options.serotype': True,
        'options.vf': True,
        'options.stx1': True,
        'options.stx2': True,
        'options.eae': True,
        'options.groupresults': True,
        'options.bulk': False,
        'options.pan': True
    }

    # POST.
    r = requests.post(API + 'upload', data=data, files=files)
    pipeline_id = r.json().keys()[0]
    print("pipeline_id: {0}".format(pipeline_id))
    # Sleep at least 4 second.
    sleep(4)
    try:
        # Loop until complete.
        while requests.get(API + 'results/' + pipeline_id).json() == unicode('pending'):
            # The length we sleep doesn't matter, as timing is retrieved directly
            # from RQ.
            print "sleeping"
            sleep(4)
        # Request to timings for various sub-jobs.
        timings = requests.get(API + 'timings/' + pipeline_id).json()
        print("timings: {0}".format(timings))
        return timings
    except:
        # Case connection broke.
        return {}

def _bap(list_genomes):
    # BAP throws an error without KmerFinder.
    r = subprocess.check_call("""docker run -ti --rm -w /workdir -v $(pwd):/workdir    cgetools BAP --dbdir /usr/src/cgepipeline/test/databases  --services KmerFinder,ResFinder,VirulenceFinder  --fa /usr/src/cgepipeline/test/test.fa""", shell=True)
    return True

def _timing(func, seeds):
    list_sizes = [len(l) for l in seeds]
    r = BarResult(list_sizes)
    for list_genomes in seeds:
        d = func(list_genomes)
        r.update(d)
    return r

def main(spfy=True, bap=False, rn=None):
    if not rn:
        rn = range(1,22,5)
    # Create groups of seed genomes.
    seeds = [_seed_genomes(i) for i in rn]
    # Run timings
    if spfy:
        r_spfy = _timing(_run_spfy, seeds)
    if bap:
        r_bap = _timing(_bap, seeds)
    return r_spfy, r_bap

def singlerun(n=100):
    '''Times Spfy 1-by-1 for up to n genomes. Used to find average/module.
    '''
    l = []
    now = _now()
    seeds = _seed_genomes(n)
    for index, genome in enumerate(seeds):
        # Run Spfy with a single genome.
        print('{0}/{1} Running Spfy with file: {2}'.format(index+1,len(seeds),genome))
        r = _run_spfy(genome)
        l.append(r)
    # Pickle file.
    p = '{0}_singlerun_{1}.p'.format(now,n)
    pickle.dump(l, open(p, "wb" ))
    return l

if __name__ == '__main__':
    rn = range(1,22,5)
    main(rn=rn)
