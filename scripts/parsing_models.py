#!/usr/bin/python

import json, h5py
import numpy as np

json_files = [
    '<dir_to_json>/chrx_1_N.json',
    ...
]


"""
Need to work in the import of the parameters for each of the models and each of
the regions. This should also be the place to include the meta data about the
source for the information that have been computed.

This should include all that is in the all info from the metadata and object.
The majority of this should only require importing the once. Elements that might
change include:
 - uuid
 - start
 - chromStart
 - end
 - chromEnd
 - resolution
 - dependencies
"""

for jf in json_files:
    models = json.loads(open(jf).read())
    
    metadata = models['metadata']
    objectdata = models['object']
    clusters = models['clusters']
    file_name = jf.split("/")
    
    resolution = objectdata['resolution']
    
    uuid = objectdata['uuid']
    
    # Create the HDF5 file
    filename ="test02.hdf5"
    f = h5py.File(filename, "a")
    
    print file_name[-1] + ' - ' + file_name[-3] + "\t" + objectdata['chrom'][0] + ' : ' + str(objectdata['chromStart'][0]) + ' - ' + str(objectdata['chromEnd'][0]) + " | " + str(int(objectdata['chromEnd'][0]-objectdata['chromStart'][0])) + " - " + str(len(models['models'][0]['data']))
    
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
        
        dset.attrs['title']          = objectdata['title']
        dset.attrs['experimentType'] = objectdata['experimentType']
        dset.attrs['species']        = objectdata['species']
        dset.attrs['project']        = objectdata['project']
        dset.attrs['identifier']     = objectdata['identifier']
        dset.attrs['assembly']       = objectdata['assembly']
        dset.attrs['cellType']       = objectdata['cellType']
        dset.attrs['resolution']     = objectdata['resolution']
        dset.attrs['datatype']       = objectdata['datatype']
        dset.attrs['components']     = objectdata['components']
        dset.attrs['source']         = objectdata['source']
    
    clustergrps = clustersgrp.create_group(str(uuid))
    for c in xrange(len(clusters)):
        clustersds = clustergrps.create_dataset(str(c), data=clusters[c], chunks=True, compression="gzip")
    
    centroidsds = centroidsgrp.create_dataset(str(uuid), data=models['centroids'], chunks=True, compression="gzip")
    
    current_size = len(dset)
    if current_size == 1:
        current_size = 0
    dset.resize((current_size+(len(models['models'][0]['data'])/3), 1000, 3))
    
    dnp = np.zeros([len(models['models'][0]['data'])/3, 1000, 3], dtype='int32')
    
    model_param = []
    
    model_id = 0
    for model in models['models']:
        ref = model['ref']
        d = model['data']
        
        cid = [ind for ind in xrange(len(clusters)) if ref in clusters[ind]]
        if len(cid) == 0:
            cluster_id = len(clusters)
        else:
            cluster_id = cid[0]
        
        model_param.append([int(ref), int(cluster_id)])
        
        j = 0
        for i in xrange(0, len(d), 3):
            xyz = d[i:i + 3]
            dnp[j][model_id] = xyz
            j += 1
        
        model_id += 1
    
    model_param_ds = mpgrp.create_dataset(str(uuid), data=model_param, chunks=True, compression="gzip")
    
    model_param_ds.attrs['i'] = current_size
    model_param_ds.attrs['j'] = current_size+(len(models['models'][0]['data'])/3)
    model_param_ds.attrs['chromosome'] = objectdata['chrom'][0]
    model_param_ds.attrs['start'] = int(objectdata['chromStart'][0])
    model_param_ds.attrs['end'] = int(objectdata['chromEnd'][0])
    model_param_ds.attrs['dependencies'] = json.dumps(objectdata['dependencies'])
    
    dset[current_size:current_size+(len(models['models'][0]['data'])/3), 0:1000, 0:3] += dnp
    
    f.close()

