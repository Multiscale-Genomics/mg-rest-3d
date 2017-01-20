#!/usr/bin/python

import random
from rest.hdf5_coord_reader import hdf5_coord

h5 = hdf5_coord()

# Get the resolutions
print h5.get_resolutions('test', '')
for i in xrange(1000):
    x = h5.get_resolutions('test', '')

# Get the Chromosomes
#print h5.get_chromosomes('test', '', 2000)
#for i in xrange(1000):
#    x = h5.get_chromosomes('test', '', 2000)

# Get regions
#chr_list = h5.get_chromosomes('test', '', 2000)
#print h5.get_regions('test', '', 2000, random.choice(chr_list), 10000, 2000000)
#for i in xrange(1000):
#    x = h5.get_regions('test', '', 2000, random.choice(chr_list), 10000, 2000000)

# Get models
chr_list = h5.get_chromosomes('test', '', 2000)
regions = h5.get_regions('test', '', 2000, random.choice(chr_list), 10000, 2000000)
#region_id = random.randint(0, 249)
#models = h5.get_models('test', '', 2000, random.choice(regions))
#print models
#for i in xrange(1000):
#    #region_id = random.randint(0, 249)
#    x = h5.get_models('test', '', 2000, random.choice(regions))

"""
for i in xrange(100):
    region_id = random.randint(0, 249)
    ref  = random.randint(0, 999)
    
    # Get coordinates
    model = h5.get_model('test', '', 2000, region_id, ref)
    coord     = [str(x) for coords in model for x in coords]
    
    region = {
        "metadata" : {},
        "object"   : {
            'region_id' : region_id
        },
        "models"   : [
            {
                "ref"  : ref,
                "data" : coord[0:10]
            }
        ]
    }
    
    print region
"""
