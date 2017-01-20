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

import os, json, h5py
import numpy as np

from dmp import dmp

class hdf5_coord:
    """
    Class related to handling the functions for interacting directly with the
    HDF5 files. All required information should be passed to this class.
    """
    
    test_file = '../sample_coords.hdf5'
    
    
    def __init__(self, user_id = 'test', file_id = '', resolution = None):
        """
        Initialise the module and 
        """
        
        self.test_file = '../sample_coords.hdf5'
        
        # Open the hdf5 file
        if user_id == 'test':
            resource_path = os.path.join(os.path.dirname(__file__), self.test_file)
            self.f = h5py.File(resource_path, "r")
        else:
            cnf_loc=os.path.dirname(os.path.abspath(__file__)) + '/mongodb.cnf'
            da = dmp(cnf_loc)
            file_obj = da.get_file_by_id(user_id, file_id)
            self.f = h5py.File(file_obj["file_path"], "r")
        
        self.resolution = resolution
        
        if self.resolution != None:
            self.grp       = self.f[str(self.resolution)]
            self.meta      = self.grp['meta']
            self.mpgrp     = self.meta['model_params']
            self.clusters  = self.meta['clusters']
            self.centroids = self.meta['centroids']
    
    
    def set_resolution(self, resolution):
        """
        
        """
        
        self.resolution = resolution
        
        self.grp       = self.f[str(resolution)]
        self.meta      = grp['meta']
        self.mpgrp     = meta['model_params']
        self.clusters  = meta['clusters']
        self.centroids = meta['centroids']
    
    
    def get_resolution(self):
        """
        
        """
        
        return self.resolution
    
    
    def get_object_data(self, region_id):
        """
        
        """
        
        if self.resolution == None:
            return {}
        
        mpds = self.mpgrp[str(region_id)]
        dset = self.grp['data']
        
        return {
            'title' : dset.attrs['title'],
            'experimentType' : dset.attrs['experimentType'],
            'species' : dset.attrs['species'],
            'project' : dset.attrs['project'],
            'identifier' : dset.attrs['identifier'],
            'assembly' : dset.attrs['assembly'],
            'cellType' : dset.attrs['cellType'],
            'resolution' : dset.attrs['resolution'],
            'datatype' : dset.attrs['datatype'],
            'components' : dset.attrs['components'],
            'source' : dset.attrs['source'],
            'chromEnd' : [mpds.attrs['end']],
            'end' : mpds.attrs['end'],
            'chromStart' : [mpds.attrs['start']],
            'start' : mpds.attrs['start'],
            'chrom' : mpds.attrs['chromosome'],
            'dependencies' : json.loads(mpds.attrs['dependencies']),
            'uuid' : region_id,
        }
    
    
    def get_clusters(self, region_id):
        """
        
        """
        
        if self.resolution == None:
            return {}
        
        clustergrps = self.clusters[str(region_id)]
    
    
    def get_resolutions(self):
        """
        List resolutions that models have been generated for
        """
        
        return self.f.keys()
    
    
    def get_chromosomes(self):
        """
        List of chromosomes that haver models at a given resolution
        """
        
        if self.resolution == None:
            return {}
        
        return list(set([self.mpgrp[region_id].attrs['chromosome'] for region_id in self.mpgrp.keys()]))
    
    
    def get_regions(self, chr_id, start, end):
        """
        List regions that are within a given range on a chromosome
        """
        
        if self.resolution == None:
            return {}
        
        return [region_id for region_id in self.mpgrp.keys() if self.mpgrp[region_id].attrs['start']<end and self.mpgrp[region_id].attrs['end']>start and self.mpgrp[region_id].attrs['chromosome']==chr_id]
        
        
    def get_models(self, region_id):
        """
        List all models for a given region
        
        Returns
        -------
        List
            model_id   : int
            cluster_id : int
        """
        
        if self.resolution == None:
            return {}
        
        model_param_ds = self.mpgrp[str(region_id)]
        
        return model_param_ds[:,:]
        
    
    def get_model(self, region_id, model_ids = None):
        """
        Get the coordinates within a defined region on a specific chromosome.
        If the model_id is not returned the the consensus models for that region
        are returned
        """
        
        if self.resolution == None:
            return {}
        
        mpds = self.mpgrp[str(region_id)]
        dset = self.grp['data']
        
        models = []
        for mid in model_ids:
            model_loc = list(mpds[:,0]).index(mid)
            
            # length x model_loc x coords
            model = dset[mpds.attrs['i']:mpds.attrs['j'], model_loc, :]
            
            models.append(
                {
                    "ref" : mid,
                    "data" : [str(x) for coords in model for x in coords]
                }
            )
        
        meta_data   = json.loads(dset.attrs['TADbit_meta'])
        
        if 'hic_data' in mpds.attrs:
            hic_data    = json.loads(mpds.attrs['hic_data'])
        
        restraints  = json.loads(mpds.attrs['restraints'])
        
        object_data = get_object_data(resolution, region_id)
        
        clusters  = []
        centroids = self.centroids[str(region_id)]
        
        return {
            "metadata"   : meta_data,
            "object"     : object_data,
            "models"     : models,
            "clusters"   : clusters,
            "centroids"  : centroids,
            "restrainst" : retraints,
            "hic_data"   : hic_data
        }
