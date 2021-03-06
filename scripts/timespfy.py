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
    def __init__(self, seeds, now):
        self.list_sizes = [len(l) for l in seeds]
        self.seeds = seeds
        self.subtasks = None
        self.data = []
        self.now = now
        self.pipelines = []

    def update(self, timing):
        '''Variable "timing" should be of shape {sample_size(str): list_subtask_times(list)}
        '''
        self.data.append(timing)

# Calling functions.

def _run_spfy(list_genomes, on='', resultcls=None, phylotyper=True):
    '''POSTs to Spfy's API.
    '''
    # Zip files if more than 1 genome.
    if isinstance(list_genomes, list):
        if len(list_genomes)>1:
            # Zip the files.
            name = _now() + '.zip'
            with ZipFile(name, 'w') as z:
                for f in list_genomes:
                    z.write(f, os.path.basename(f))
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
        'options.stx1': phylotyper,
        'options.stx2': phylotyper,
        'options.eae': phylotyper,
        'options.groupresults': True,
        'options.bulk': False,
        'options.pan': False
    }

    # POST.
    r = requests.post(API + 'upload', data=data, files=files)
    try:
        pipeline_id = r.json().keys()[0]
        if resultcls:
            resultcls.pipelines.append(pipeline_id)
    except:
        print('Could not find pipeline_id from response {0}'.format(r.text))
        sleep(20)
        return {}
    print("pipeline_id: {0}".format(pipeline_id))
    started = datetime.now()
    # Sleep at least 4 second.
    sleep(4)
    try:
        # Loop until complete.
        while requests.get(API + 'results/' + pipeline_id).json() == unicode('pending'):
            # The length we sleep doesn't matter, as timing is retrieved directly
            # from RQ.
            print "On {0}, sleeping. Elapsed: {1}".format(on, datetime.now()-started)
            sleep(20)
        # Request to timings for various sub-jobs.
        r = requests.get(API + 'timings/' + pipeline_id)
        try:
            timings = r.json()
            print("timings: {0}".format(timings))
        except:
            m = "FATAL: timings got something weird when retrieving timings. Got: {0}".format(r)
            print("\n{0}\n".format(m))
            timings = {len(list_genomes):m}
        return timings
    except:
        # Case connection broke.
        return {}

def _bap(list_genomes, on=''):
    # BAP throws an error without KmerFinder.
    r = subprocess.check_call("""docker run -ti --rm -w /workdir -v $(pwd):/workdir    cgetools BAP --dbdir /usr/src/cgepipeline/test/databases  --services KmerFinder,ResFinder,VirulenceFinder  --fa /usr/src/cgepipeline/test/test.fa""", shell=True)
    return True

def _timing(func, seeds, phylotyper=True):
    now = _now()
    r = BarResult(seeds, now)
    raws = []
    for list_genomes in seeds:
        on = '{0}/{1}'.format(len(list_genomes),len(seeds[-1]))
        print('\n{0} Spfy Batch with files: {1}\n'.format(on,list_genomes))
        d = func(list_genomes, on, r, phylotyper)
        r.update(d)
        raws.append(d)
    # Pickle file.
    pickle.dump(raws, open('{0}_spfy_raws_{1}.p'.format(now,len(seeds)), "wb" ))
    pickle.dump(r, open('{0}_spfy_class_{1}.p'.format(now,len(seeds)), "wb" ))
    return r

def singlerun(n=100, phylotyper=True):
    '''Times Spfy 1-by-1 for up to n genomes. Used to find average/module.
    '''
    l = []
    now = _now()
    seeds = _seed_genomes(n)
    for index, genome in enumerate(seeds):
        on = '{0}/{1}'.format(index+1,len(seeds))
        # Run Spfy with a single genome.
        print('{0} Running Spfy with file: {1}'.format(on,genome))
        r = _run_spfy(genome, on=on, phylotyper=phylotyper)
        l.append({genome:r})
    # Pickle file.
    p = '{0}_singlerun_{1}.p'.format(now,n)
    pickle.dump(l, open(p, "wb" ))
    return l

def main(spfy=True, bap=False, n=101, phylotyper=True):
    print('Starting timing run for {0} files\nFrom: {1}\nAgainst API: {2}'.format(n,GENOME_POOL,API))
    rn = range(0,n+1,10)
    rn[0]=1
    # Create groups of seed genomes.
    seeds = [_seed_genomes(i) for i in rn]
    # Run timings
    r = _timing(_run_spfy, seeds, phylotyper)
    return r

if __name__ == '__main__':
    main()
