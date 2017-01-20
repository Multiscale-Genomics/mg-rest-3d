#!/usr/bin/python

"""
Copyright 2016 EMBL-European Bioinformatics Institute

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import random
from rest.hdf5_coord_reader import hdf5_coord

h5 = hdf5_coord('test', '', 2000)

# Get the resolutions
print h5.get_resolutions()
for i in xrange(1000):
    x = h5.get_resolutions()

# Get the Chromosomes
#print h5.get_chromosomes()
#for i in xrange(1000):
#    x = h5.get_chromosomes()

# Get regions
#chr_list = h5.get_chromosomes()
#print h5.get_regions(random.choice(chr_list), 10000, 2000000)
#for i in xrange(1000):
#    x = h5.get_regions(random.choice(chr_list), 10000, 2000000)

# Get models
chr_list = h5.get_chromosomes()
regions = h5.get_regions(random.choice(chr_list), 10000, 2000000)
#region_id = random.randint(0, 249)
#models = h5.get_models(random.choice(regions))
#print models
#for i in xrange(1000):
#    #region_id = random.randint(0, 249)
#    x = h5.get_models(random.choice(regions))

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
