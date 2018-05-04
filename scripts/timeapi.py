import requests
import time
import cPickle as pickle

from datetime import datetime

def _now():
    now = datetime.now()

    return now

def _get(api):
    start = time.time()
    r = requests.get(api)
    stop = time.time()
    j = r.json()
    assert isinstance(j, (list,dict))
    return stop - start

def main(c=1000):
    # Setup.
    core = (
        'https://lfz.corefacility.ca/superphy/spfyapi/api/v0/get_all_attribute_types',
        'https://lfz.corefacility.ca/superphy/spfyapi/api/v0/get_all_types',
        'https://lfz.corefacility.ca/superphy/spfyapi/api/v0/get_attribute_values/type/http://purl.obolibrary.org/obo/GENEPIO_0001077'
        'https://lfz.corefacility.ca/superphy/spfyapi/api/v0/get_attribute_values/type/http://purl.obolibrary.org/obo/GENEPIO_0001076'
    )
    l = []

    # Start.
    now = datetime.now()

    # Loop.
    for i, api in enumerate(core):
        for n in range(c):
            t = _get(api)
            l.append(t)
            print('API: {0}/{1}, Count: {2}/{3}; Time Reported {4}'.format(
                i,
                len(core),
                n+1,
                c,
                t
            ))

    # Stop.
    stop = datetime.now()
    print('Total runtime of this script: {0}'.format(stop-now))

    # Dump.
    now = now.strftime("%Y-%m-%d-%H-%M-%S-%f")
    f = 'api-' + now + '_list.p'
    print('Dumping file at: {0}'.format(f))
    pickle.dump(l, open(f, "wb" ))
