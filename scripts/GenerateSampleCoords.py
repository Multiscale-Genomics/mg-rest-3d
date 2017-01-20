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

import json, h5py, random
import numpy as np

resolution  = 2000
clusters    = [[0, 1, 2], [3, 4], [5], [6]]
centroids   = [1, 10, 100, 150, 200]
chromosomes = ['chr1', 'chr2', 'chr3', 'chr4', 'chr5', 'chr6', 'X']

for uuid in xrange(250):
    # Create the HDF5 file
    filename ="sample_coords.hdf5"
    f = h5py.File(filename, "a")
    
    if str(resolution) in f.keys():
        grp = f[str(resolution)]
        dset = grp['data']
        
        meta         = grp['meta']
        mpgrp        = meta['model_params']
        clustersgrp  = meta['clusters']
        centroidsgrp = meta['centroids']
    else:
        # Create the initial dataset with minimum values
        grp  = f.create_group(str(resolution))
        meta = grp.create_group('meta')
        
        mpgrp        = meta.create_group('model_params')
        clustersgrp  = meta.create_group('clusters')
        centroidsgrp = meta.create_group('centroids')
        
        dset = grp.create_dataset('data', (1, 1000, 3), maxshape=(None, 1000, 3), dtype='int32', chunks=True, compression="gzip")
        
        dset.attrs['title']          = 'title'
        dset.attrs['experimentType'] = 'experimentType'
        dset.attrs['species']        = 'species'
        dset.attrs['project']        = 'project'
        dset.attrs['identifier']     = 'identifier'
        dset.attrs['assembly']       = 'assembly'
        dset.attrs['cellType']       = 'cellType'
        dset.attrs['resolution']     = 'resolution'
        dset.attrs['datatype']       = 'datatype'
        dset.attrs['components']     = 'components'
        dset.attrs['source']         = 'source'
    
    clustergrps = clustersgrp.create_group(str(uuid))
    for c in xrange(len(clusters)):
        clustersds = clustergrps.create_dataset(str(c), data=clusters[c], chunks=True, compression="gzip")
    centroidsds = centroidsgrp.create_dataset(str(uuid), centroids, chunks=True, compression="gzip")
    
    current_size = len(dset)
    if current_size == 1:
        current_size = 0
    
    model_size = random.randint(500, 2000)
    
    dset.resize((current_size+model_size, 1000, 3))
    
    dnp = np.zeros([model_size, 1000, 3], dtype='int32')
    
    model_param = []
    for ref in xrange(1000):
        cluster_id = random.choice(clusters)
        model_param.append([ref, cluster_id])
        
        for p in xrange(model_size):
            x = random.randint(-1000,1000)
            y = random.randint(-1000,1000)
            z = random.randint(-1000,1000)
            
            dnp[p][ref] = [x, y, z]
    
    start = random.randint(1,30000000)
    end = start + random.randint(5000, 100000)
    
    model_param_ds = mpgrp.create_dataset(str(uuid), data=model_param)
    
    model_param_ds.attrs['i'] = current_size
    model_param_ds.attrs['j'] = current_size+model_size
    model_param_ds.attrs['chromosome'] = random.choice(chromosomes)
    model_param_ds.attrs['start'] = start
    model_param_ds.attrs['end'] = end
    model_param_ds.attrs['dependencies'] = json.dumps({'test' : 'test'})
    
    dset[current_size:current_size+model_size, 0:1000, 0:3] += dnp
        
    f.close()
    
    if (uuid+1) % 50 == 0:
        print uuid+1
    
    
        
        
