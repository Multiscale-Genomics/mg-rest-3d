#!/usr/bin/python

"""
.. See the NOTICE file distributed with this work for additional information
   regarding copyright ownership.

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

from __future__ import print_function

import json
import h5py
import numpy as np

json_files = open('json_files.txt', 'r')

for jf in json_files:
    jf = jf.strip()
    models = json.loads(open(jf).read())

    metadata = models['metadata']
    objectdata = models['object']
    clusters = models['clusters']
    file_name = jf.split("/")

    resolution = objectdata['resolution']

    uuid = objectdata['uuid']

    # Create the HDF5 file
    filename = "test_02.hdf5"
    f = h5py.File(filename, "a")

    print(
        file_name[-1] + ' - ' + file_name[-3] + "\t" + objectdata['chrom'][0] +
        ' : ' + str(objectdata['chromStart'][0]) + ' - ' + str(objectdata['chromEnd'][0]) +
        " | " + str(int(objectdata['chromEnd'][0]-objectdata['chromStart'][0])) + " - " +
        str(len(models['models'][0]['data']))
    )

    if str(resolution) in f:
        grp = f[str(resolution)]
        dset = grp['data']

        meta = grp['meta']
        mpgrp = meta['model_params']
        clustersgrp = meta['clusters']
        centroidsgrp = meta['centroids']
    else:
        # Create the initial dataset with minimum values
        grp = f.create_group(str(resolution))
        meta = grp.create_group('meta')

        mpgrp = meta.create_group('model_params')
        clustersgrp = meta.create_group('clusters')
        centroidsgrp = meta.create_group('centroids')

        dset = grp.create_dataset(
            'data', (1, 1000, 3), maxshape=(None, 1000, 3),
            dtype='int32', chunks=True, compression="gzip")

        dset.attrs['title'] = objectdata['title']
        dset.attrs['experimentType'] = objectdata['experimentType']
        dset.attrs['species'] = objectdata['species']
        dset.attrs['project'] = objectdata['project']
        dset.attrs['identifier'] = objectdata['identifier']
        dset.attrs['assembly'] = objectdata['assembly']
        dset.attrs['cellType'] = objectdata['cellType']
        dset.attrs['resolution'] = objectdata['resolution']
        dset.attrs['datatype'] = objectdata['datatype']
        dset.attrs['components'] = objectdata['components']
        dset.attrs['source'] = objectdata['source']
        dset.attrs['TADbit_meta'] = json.dumps(metadata)
        dset.attrs['dependencies'] = json.dumps(objectdata['dependencies'])
        dset.attrs['restraints'] = json.dumps(models['restraints'])
        if 'hic_data' in models:
            dset.attrs['hic_data'] = json.dumps(models['hic_data'])

    clustergrps = clustersgrp.create_group(str(uuid))
    cluster_count = len(clusters)
    for c in range(cluster_count):
        clustersds = clustergrps.create_dataset(
            str(c), data=clusters[c], chunks=True, compression="gzip")

    centroidsds = centroidsgrp.create_dataset(
        str(uuid), data=models['centroids'], chunks=True, compression="gzip")

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

    model_param_ds = mpgrp.create_dataset(
        str(uuid), data=model_param, chunks=True, compression="gzip")

    model_param_ds.attrs['i'] = current_size
    model_param_ds.attrs['j'] = current_size+(len(models['models'][0]['data'])/3)
    model_param_ds.attrs['chromosome'] = objectdata['chrom'][0]
    model_param_ds.attrs['start'] = int(objectdata['chromStart'][0])
    model_param_ds.attrs['end'] = int(objectdata['chromEnd'][0])

    dset[current_size:current_size+(len(models['models'][0]['data'])/3), 0:1000, 0:3] += dnp

    f.close()
