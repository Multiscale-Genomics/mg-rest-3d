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
#print h5.get_resolutions()
#for i in xrange(1000):
#    x = h5.get_resolutions()

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
#print chr_list
chr_id = random.choice(chr_list)
chr_id = 'chr2R'
#print chr_id
regions = h5.get_regions(chr_id, 10000, 2000000)
#print regions
#region_id = random.choice(regions)
#print region_id
#model_ids = h5.get_models(region_id)
#print model_ids
#models = h5.get_model(region_id, [random.randint(0, 999)])
#print models
#for i in xrange(1000):
#    #region_id = random.randint(0, 249)
#    x = h5.get_models(random.choice(regions))


for i in xrange(100):
    #region_id = random.choice(regions)
    region_id = 87
    model_id  = [random.randint(0, 999), random.randint(0, 999), random.randint(0, 999), random.randint(0, 999), random.randint(0, 999)]
    #model_id  = [0]
    
    # Get coordinates
    models = h5.get_model(region_id, model_id)
    
    print models

h5.close()
