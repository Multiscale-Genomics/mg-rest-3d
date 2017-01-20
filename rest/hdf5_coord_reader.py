#!/usr/bin/python

import os, json, h5py
import numpy as np

from dmp import dmp

class hdf5_coord:
    """
    Class related to handling the functions for interacting directly with the
    HDF5 files. All required information should be passed to this class.
    """
    
    test_file = '../sample_coords.hdf5'
    
    def get_resolutions(self, user_id, file_id):
        """
        List resolutions that models have been generated for
        """
        
        # Open the hdf5 file
        if user_id == 'test':
            resource_package = __name__
            resource_path = os.path.join(os.path.dirname(__file__), self.test_file)
            f = h5py.File(resource_path, "r")
        else:
            cnf_loc=os.path.dirname(os.path.abspath(__file__)) + '/mongodb.cnf'
            da = dmp(cnf_loc)
            file_obj = da.get_file_by_id(user_id, file_id)
            f = h5py.File(file_obj["file_path"], "r")
        
        return f.keys()
    
    
    def get_chromosomes(self, user_id, file_id, resolution):
        """
        List of chromosomes that haver models at a given resolution
        """
        
        # Open the hdf5 file
        if user_id == 'test':
            resource_path = os.path.join(os.path.dirname(__file__), self.test_file)
            f = h5py.File(resource_path, "r")
        else:
            cnf_loc=os.path.dirname(os.path.abspath(__file__)) + '/mongodb.cnf'
            da = dmp(cnf_loc)
            file_obj = da.get_file_by_id(user_id, file_id)
            f = h5py.File(file_obj["file_path"], "r")
        
        grp = f[str(resolution)]
        meta = grp['meta']
        mpgrp = meta['model_params']
        
        return list(set([mpgrp[region_id].attrs['chromosome'] for region_id in mpgrp.keys()]))
    
    
    def get_regions(self, user_id, file_id, resolution, chr_id, start, end):
        """
        List regions that are within a given range on a chromosome
        """
        
        # Open the hdf5 file
        if user_id == 'test':
            resource_path = os.path.join(os.path.dirname(__file__), self.test_file)
            f = h5py.File(resource_path, "r")
        else:
            cnf_loc=os.path.dirname(os.path.abspath(__file__)) + '/mongodb.cnf'
            da = dmp(cnf_loc)
            file_obj = da.get_file_by_id(user_id, file_id)
            f = h5py.File(file_obj["file_path"], "r")
        
        grp = f[str(resolution)]
        meta = grp['meta']
        mpgrp = meta['model_params']
        
        region_ids = [region_id for region_id in mpgrp.keys() if mpgrp[region_id].attrs['start']<end and mpgrp[region_id].attrs['end']>start and mpgrp[region_id].attrs['chromosome']==chr_id]
        
        return region_ids
        
        
    def get_models(self, user_id, file_id, resolution, region_id):
        """
        List all models for a given region
        
        Returns
        -------
        List
            model_id   : int
            cluster_id : int
        """
        
        # Open the hdf5 file
        if user_id == 'test':
            resource_path = os.path.join(os.path.dirname(__file__), self.test_file)
            f = h5py.File(resource_path, "r")
        else:
            cnf_loc=os.path.dirname(os.path.abspath(__file__)) + '/mongodb.cnf'
            da = dmp(cnf_loc)
            file_obj = da.get_file_by_id(user_id, file_id)
            f = h5py.File(file_obj["file_path"], "r")
        
        grp = f[str(resolution)]
        meta = grp['meta']
        mpgrp = meta['model_params']
        
        model_param_ds = mpgrp[str(region_id)]
        
        return model_param_ds[:,:]
        
    
    def get_model(self, user_id, file_id, resolution, region_id, model_id = None):
        """
        Get the coordinates within a defined region on a specific chromosome.
        If the model_id is not returned the the consensus models for that region
        are returned
        """
        
        # Open the hdf5 file
        if user_id == 'test':
            resource_path = os.path.join(os.path.dirname(__file__), self.test_file)
            f = h5py.File(resource_path, "r")
        else:
            cnf_loc=os.path.dirname(os.path.abspath(__file__)) + '/mongodb.cnf'
            da = dmp(cnf_loc)
            file_obj = da.get_file_by_id(user_id, file_id)
            f = h5py.File(file_obj["file_path"], "r")
        
        grp = f[str(resolution)]
        dset = grp['data']
        meta = grp['meta']
        
        mpgrp = meta['model_params']
        mpds = mpgrp[str(region_id)]
        
        model_loc = [i for i in xrange(len(mpds)) if model_id in mpds[i]]
        
        # length x model_loc x coords
        model = dset[mpds.attrs['i']:mpds.attrs['j'], model_loc[0], :]
        
        return model
