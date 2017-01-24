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
        
        Parameters
        ----------
        user_id : str
            Identifier to uniquely locate the users files. Can be set to 
            "common" if the files can be shared between users
        file_id : str
            Location of the file in the file system
        resolution : int (Optional)
            Level of resolution. This is optional, but only the functions
            get_resolutions() and set_resolutions() can be called. Once the
            resolution has been set then all functions are callable.
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
            
            dset = self.grp['data']
            
            if 'dependencies' in dset.attrs:
                self.dependencies = json.loads(dset.attrs['dependencies'])
            else:
                self.dependencies = []
            
            if 'TADbit_meta' in dset.attrs:
                self.meta_data   = json.loads(dset.attrs['TADbit_meta'])
            else:
                self.meta_data   = {}
            
            if 'hic_data' in dset.attrs:
                self.hic_data    = json.loads(dset.attrs['hic_data'])
            else:
                self.hic_data    = {}
            
            if 'restraints' in dset.attrs:
                self.restraints  = json.loads(dset.attrs['restraints'])
            else:
                self.restraints  = {}
    
    
    def close(self):
        """
        Tidy function to close file handles
        """
        self.f.close()
    
    
    def get_resolutions(self):
        """
        List resolutions that models have been generated for
        
        Returns
        -------
        list : str
            Available levels of resolution that can be set
        """
        
        return self.f.keys()
    
    
    def set_resolution(self, resolution):
        """
        Set, or change, the resolution level
        
        Parameters
        ----------
        resolution : int
            Level of resolution
        """
        
        self.resolution = resolution
        
        self.grp       = self.f[str(resolution)]
        self.meta      = grp['meta']
        self.mpgrp     = meta['model_params']
        self.clusters  = meta['clusters']
        self.centroids = meta['centroids']
    
    
    def get_resolution(self):
        """
        List the current level of rseolution
        
        Returns
        -------
        resolution : int
            Current level of resolution
        """
        
        return self.resolution
    
    
    def get_object_data(self, region_id):
        """
        Prepare the object header data structure ready for printing
        
        Parameters
        ----------
        region_id : int
            Region that is getting downloaded
        
        Returns
        -------
        objectdata : dict
            All headers and values required for the JSON output
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
            'dependencies' : self.dependencies,
            'uuid' : region_id,
        }
    
    
    def get_clusters(self, region_id):
        """
        List all clusters of models
        
        Returns
        -------
        clusters : list
            List of models in each cluster
        """
        
        if self.resolution == None:
            return {}
        
        # Need to loop through structure
        clustersgrp = self.clusters[region_id]
        
        clusters = []
        for cluster in clustersgrp:
            clusters.append(list(cluster[:]))
        return clusters
    
    
    def get_centroids(self, region_id):
        """
        List the centroid models for each cluster
        
        Returns
        -------
        centroids : list
            List of the centroid models for each cluster
        """
        
        if self.resolution == None:
            return {}
        
        return self.centroids[region_id]
    
    
    def get_chromosomes(self):
        """
        List of chromosomes that have models at a given resolution
        
        Returns
        -------
        chromosomes : list
            List of chromosomes at the set resolution
        """
        
        if self.resolution == None:
            return {}
        
        return list(set([self.mpgrp[region_id].attrs['chromosome'] for region_id in self.mpgrp.keys()]))
    
    
    def get_regions(self, chr_id, start, end):
        """
        List regions that are within a given range on a chromosome
        
        Parameters
        ----------
        chr_id : str
            Chromosome ID
        start : int
            Start position
        end : int
            Stop position
        
        Returns
        -------
        regions : list
            List of region IDs whose parameters match those provided
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
        
        Parameters
        ----------
        region_id : str
            Region ID
        model_ids : list
            List of model IDs for the models that are required
        
        Returns
        -------
        dict
            metadata : dict
                Relevant extra meta data added by TADbit
            object : dict
                Key value pair of information about the region
            models : list
                List of dictionaries for each model
            clusters : list
                List of models for each cluster
            centroids : list
                List of all centroid models
            restraints : list
                List of retraints for each position
            hic_data : dict
        """
        
        if self.resolution == None:
            return {}
        
        mpds = self.mpgrp[str(region_id)]
        dset = self.grp['data']
        
        models = []
        model_ds = dset[mpds.attrs['i']:mpds.attrs['j'], :, :]
        for mid in model_ids:
            model_loc = list(mpds[:,0]).index(int(mid))
            
            # length x model_loc x coords
            # Using model_ds by pre-cutting then taking slices from that array
            # is much quicker as the majority of the effort is in the initial
            # slice. It is also slightly quicker for getting a single model
            #model = dset[mpds.attrs['i']:mpds.attrs['j'], model_loc, :]
            model = model_ds[:, model_loc, :]
            
            models.append(
                {
                    "ref" : mid,
                    "data" : [str(x) for coords in model for x in coords]
                }
            )
        
        object_data = self.get_object_data(region_id)
        
        clusters  = []
        centroids = self.centroids[str(region_id)]
        
        return {
            "metadata"   : self.meta_data,
            "object"     : object_data,
            "models"     : models,
            "clusters"   : clusters,
            "centroids"  : list(centroids[:]),
            "restrainst" : self.restraints,
            "hic_data"   : self.hic_data
        }
