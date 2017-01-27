"""
Copyright 2017 EMBL-European Bioinformatics Institute

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

from flask import Flask, make_response, request
from flask_restful import Api, Resource

from .hdf5_coord_reader import hdf5_coord


app = Flask(__name__)
#app.config['DEBUG'] = False

api = Api(app)

class GetEndPoints(Resource):
    """
    Class to handle the http requests for returning information about the end
    points
    """
    
    def get(self):
        return {
            '_links': {
                '_self': request.base_url,
                '_resolutions': request.url_root + 'api/3dcoord/resolutions',
                '_chromosomes': request.url_root + 'api/3dcoord/chromosomes',
                '_regions': request.url_root + 'api/3dcoord/regions',
                '_models': request.url_root + 'api/3dcoord/models',
                '_model': request.url_root + 'api/3dcoord/model',
                '_ping': request.url_root + 'api/3dcoord/ping',
                '_parent': request.url_root + 'api'
            }
        }


class GetResolutions(Resource):
    """
    Class to handle the http requests for returning information about the
    resolutions that models have been generated for
    """
    
    def usage(self, error_message, status_code, parameters = {}):
        usage = {
                    '_links' : {
                        '_self' : request.base_url,
                        '_parent': request.url_root + 'api/3dcoord'
                    },
                    'parameters' : {
                        'user_id' : ['User ID', 'str', 'REQUIRED'],
                        'file_id' : ['File ID', 'str', 'REQUIRED'],
                    }
                }
        message = {
                      'usage' : usage,
                      'status_code' : status_code
                  }

        if len(parameters) > 0:
            message['provided_parameters'] = parameters
        
        if error_message != None:
            message['error'] = error_message

        return message
    
    def get(self):
        user_id = request.args.get('user_id')
        file_id = request.args.get('file_id')
        
        params = [user_id, file_id]

        # Display the parameters available
        if sum([x is None for x in params]) == len(params):
            return self.usage(None, 200)
        
        # ERROR - one of the required parameters is NoneType
        if sum([x is not None for x in params]) != len(params):
            return self.usage('MissingParameters', 400, {'user_id' : user_id, 'file_id' : file_id}), 400
        
        request_path = request.path
        rp = request_path.split("/")
        
        h5 = hdf5_coord(user_id, file_id)
        resolution_list = h5.get_resolutions()
        h5.close()
        
        data = {}
        
        resolutions = []
        for r in resolution_list:
            resolutions.append(
                {
                    'resolution' : r,
                    '_links' : {
                        '_chromosomes' : request.url_root + 'api/3dcoord/chromosomes?user_id=' + user_id + '&file_id=' + file_id + '&res=' + str(r)
                    }
                }
            )
        
        data['resolutions'] = resolutions
        
        data['_links'] = {
            '_self': request.base_url + '?user_id=' + user_id + '&file_id=' + file_id,
            '_parent': request.url_root + 'api/3dcoord'
        }
        
        return data


class GetChromosomes(Resource):
    """
    Class to handle the http requests for returning information about the
    chromosomes that the models have been generated across
    """
    
    def usage(self, error_message, status_code, parameters = {}):
        usage = {
                    '_links' : {
                        '_self' : request.base_url,
                        '_parent': request.url_root + 'api/3dcoord'
                    },
                    'parameters' : {
                        'user_id' : ['User ID', 'str', 'REQUIRED'],
                        'file_id' : ['File ID', 'str', 'REQUIRED'],
                        'res'     : ['Resolution', 'int', 'REQUIRED'],
                    }
                }
        message = {
                      'usage' : usage,
                      'status_code' : status_code
                  }

        if len(parameters) > 0:
            message['provided_parameters'] = parameters
        
        if error_message != None:
            message['error'] = error_message

        return message
    
    def get(self):
        user_id = request.args.get('user_id')
        file_id = request.args.get('file_id')
        resolution = request.args.get('res')
        
        params = [user_id, file_id, resolution]

        # Display the parameters available
        if sum([x is None for x in params]) == len(params):
            return self.usage(None, 200)
        
        # ERROR - one of the required parameters is NoneType
        if sum([x is not None for x in params]) != len(params):
            return self.usage('MissingParameters', 400, {'user_id' : user_id, 'file_id' : file_id}), 400
        
        try:
            resolution = int(resolution)
        except Exception as e:
            # ERROR - one of the parameters is not of integer type
            return self.usage('IncorrectParameterType', 400, {'user_id' : user_id, 'file_id' : file_id, 'res' : resolution}), 400
        
        h5 = hdf5_coord(user_id, file_id, resolution)
        chromosome_list = h5.get_chromosomes()
        h5.close()
        
        data = {}
        
        chromosomes = []
        for c in chromosome_list:
            chromosomes.append(
                {
                    'chromosome' : c,
                    '_links' : {
                        '_regions' : request.url_root + 'api/3dcoord/regions?user_id=' + user_id + '&file_id=' + file_id + '&res=' + str(resolution) + '&chr=' + str(c) + '&start=0&end=1000000000'
                    }
                }
            )
        
        data['resolution'] = resolution
        data['chromosomes'] = chromosomes
        
        data['_links'] = {
            '_self': request.base_url + '?user_id=' + user_id + '&file_id=' + file_id + '&res=' + str(resolution),
            '_parent': request.url_root + 'api/3dcoord',
            '_resolution' : request.url_root + 'api/3dcoord/resolutions?user_id=' + user_id + '&file_id=' + file_id
        }
        
        return data


class GetRegions(Resource):
    """
    Class to handle the http requests for returning information about the 
    regions that are available in a given region and level of resolution
    """
    
    def usage(self, error_message, status_code, parameters = {}):
        usage = {
                    '_links' : {
                        '_self' : request.base_url,
                        '_parent': request.url_root + 'api/3dcoord'
                    },
                    'parameters' : {
                        'user_id' : ['User ID', 'str', 'REQUIRED'],
                        'file_id' : ['File ID', 'str', 'REQUIRED'],
                        'res'     : ['Resolution', 'int', 'REQUIRED'],
                        'chr'     : ['Chromosome ID', 'str', 'REQUIRED'],
                        'start'   : ['Chromosome start position', 'int', 'REQUIRED'],
                        'end'     : ['Chromosome end position', 'int', 'REQUIRED'],
                    }
                }
        message = {
                      'usage' : usage,
                      'status_code' : status_code
                  }

        if len(parameters) > 0:
            message['provided_parameters'] = parameters
        
        if error_message != None:
            message['error'] = error_message

        return message
    
    def get(self):
        user_id = request.args.get('user_id')
        file_id = request.args.get('file_id')
        resolution = request.args.get('res')
        chr_id = request.args.get('chr')
        start = request.args.get('start')
        end = request.args.get('end')
        
        params = [user_id, file_id, resolution, chr_id, start, end]

        # Display the parameters available
        if sum([x is None for x in params]) == len(params):
            return self.usage(None, 200)
        
        # ERROR - one of the required parameters is NoneType
        if sum([x is not None for x in params]) != len(params):
            return self.usage('MissingParameters', 400, {'user_id' : user_id, 'file_id' : file_id, 'res' : resolution, 'chr_id' : chr_id, 'start' : start, 'end' : end}), 400
        
        try:
            start = int(start)
            end = int(end)
            resolution = int(resolution)
        except Exception as e:
            # ERROR - one of the parameters is not of integer type
            return self.usage('IncorrectParameterType', 400, {'user_id' : user_id, 'file_id' : file_id, 'res' : resolution, 'chr_id' : chr_id, 'start' : start, 'end' : end}), 400
        
        h5 = hdf5_coord(user_id, file_id, resolution)
        region_list = h5.get_regions(chr_id, start, end)
        h5.close()
        
        data = {}
        regions = []
        for r in region_list:
            regions.append(
                {
                    'region_id' : r,
                    '_links' : {
                        '_models' : request.url_root + 'api/3dcoord/models?user_id=' + user_id + '&file_id=' + file_id + '&res=' + str(resolution) + '&region=' + r
                    }
                }
            )
        
        data['resolution'] = resolution,
        data['chromosome'] = chr_id,
        data['regions'] = regions
        
        data['_links'] = {
            '_self': request.base_url + '?user_id=' + user_id + '&file_id=' + file_id + '&res=' + str(resolution) + '&chr=' + str(chr_id) + '&start=' + str(start) + '&end=' + str(end),
            '_parent': request.url_root + 'api/3dcoord',
            '_resolution' : request.url_root + 'api/3dcoord/resolutions?user_id=' + user_id + '&file_id=' + file_id,
            '_chromosomes' : request.url_root + 'api/3dcoord/chromosomes?user_id=' + user_id + '&file_id=' + file_id + '&res=' + str(resolution)
        }
        
        return data


class GetModels(Resource):
    """
    Class to handle the http requests for returning information about the models
    that are available within a given region.
    """
    
    def usage(self, error_message, status_code, parameters = {}):
        usage = {
                    '_links' : {
                        '_self' : request.base_url,
                        '_parent': request.url_root + 'api/3dcoord'
                    },
                    'parameters' : {
                        'user_id' : ['User ID', 'str', 'REQUIRED'],
                        'file_id' : ['File ID', 'str', 'REQUIRED'],
                        'res'     : ['Resolution', 'int', 'REQUIRED'],
                        'region'  : ['Regions ID', 'str', 'REQUIRED'],
                    }
                }
        message = {
                      'usage' : usage,
                      'status_code' : status_code
                  }

        if len(parameters) > 0:
            message['provided_parameters'] = parameters
        
        if error_message != None:
            message['error'] = error_message

        return message
    
    def get(self):
        user_id = request.args.get('user_id')
        file_id = request.args.get('file_id')
        resolution = request.args.get('res')
        region_id = request.args.get('region')
        
        params = [user_id, file_id, resolution, region_id]

        # Display the parameters available
        if sum([x is None for x in params]) == len(params):
            return self.usage(None, 200)
        
        # ERROR - one of the required parameters is NoneType
        if sum([x is not None for x in params]) != len(params):
            return self.usage('MissingParameters', 400, {'user_id' : user_id, 'file_id' : file_id, 'res' : resolution, 'region' : region_id}), 400
        
        try:
            resolution = int(resolution)
        except Exception as e:
            # ERROR - one of the parameters is not of integer type
            return self.usage('IncorrectParameterType', 400, {'user_id' : user_id, 'file_id' : file_id, 'res' : resolution, 'region' : region_id}), 400
        
        h5 = hdf5_coord(user_id, file_id, resolution)
        model_list = h5.get_models(region_id)
        region_list = h5.get_region_order(region=region_id)
        h5.close()
        
        models = {}
        models['model_list'] = [
            {
                'model' : str(m[0]),
                'cluster' : str(m[1]),
                '_links' : {
                    '_model' : request.url_root + 'api/3dcoord/model?user_id=' + user_id + '&file_id=' + file_id + '&res=' + str(resolution) + '&region=' + str(region_id) + '&model=' + str(m[0])
                }
            } for m in model_list
        ]
        
        models['_links'] = {
            '_self': request.base_url + '?user_id=' + user_id + '&file_id=' + file_id + '&res=' + str(resolution) + '&region=' + str(region_id),
            '_parent': request.url_root + 'api/3dcoord',
            '_models_all': request.url_root + 'api/3dcoord/model?user_id=' + user_id + '&file_id=' + file_id + '&res=' + str(resolution) + '&region=' + str(region_id) + '&model=all'
        }
        
        current_region = region_list.index(region_id)
        next_region = current_region+1
        previous_region = current_region-1
        
        if current_region<(len(region_list)-1):
            models['_links']['_next_region'] = request.url_root + 'api/3dcoord/models?user_id=' + user_id + '&file_id=' + file_id + '&res=' + str(resolution) + '&region=' + region_list[next_region]
        if current_region>0:
            models['_links']['_previous_region'] = request.url_root + 'api/3dcoord/models?user_id=' + user_id + '&file_id=' + file_id + '&res=' + str(resolution) + '&region=' + region_list[previous_region]
        
        return models


class GetModel(Resource):
    """
    Class to handle the http requests for returning the models from a given
    region. The list of models is a comma separated list that can return
    multiple models from the same region
    """
    
    def usage(self, error_message, status_code, parameters = {}):
        usage = {
                    '_links' : {
                        '_self' : request.base_url,
                        '_parent': request.url_root + 'api/3dcoord'
                    },
                    'parameters' : {
                        'user_id' : ['User ID', 'str', 'REQUIRED'],
                        'file_id' : ['File ID', 'str', 'REQUIRED'],
                        'region'  : ['Regions ID', 'str', 'REQUIRED'],
                        'model'   : ['Model ID', 'str', 'REQUIRED'],
                        'page'    : ['Page number (default: 0)', 'int', 'OPTIONAL'],
                        'mpp'     : ['Models per page (default: 10; max: 100)', 'int', 'OPTIONAL'],
                    }
                }
        message = {
                      'usage' : usage,
                      'status_code' : status_code
                  }

        if len(parameters) > 0:
            message['provided_parameters'] = parameters
        
        if error_message != None:
            message['error'] = error_message

        return message
    
    def get(self):
        user_id    = request.args.get('user_id')
        file_id    = request.args.get('file_id')
        resolution = request.args.get('res')
        region_id  = request.args.get('region')
        model_str  = request.args.get('model')
        page       = request.args.get('page')
        mpp        = request.args.get('mpp')
        
        params = [user_id, file_id, resolution, region_id, model_str]

        # Display the parameters available
        if sum([x is None for x in params]) == len(params):
            return self.usage(None, 200)
        
        # ERROR - one of the required parameters is NoneType
        if sum([x is not None for x in params]) != len(params):
            return self.usage('MissingParameters', 400, {'user_id' : user_id, 'file_id' : file_id, 'res' : resolution, 'region' : region_id, 'model' : model_str}), 400
        
        if page is None:
            page = 1
            
        if mpp is None:
            mpp = 10
        
        try:
            resolution = int(resolution)
            page = int(page)
            mpp = int(mpp)
        except Exception as e:
            # ERROR - one of the parameters is not of integer type
            return self.usage('IncorrectParameterType', 400, {'user_id' : user_id, 'file_id' : file_id, 'res' : resolution, 'region' : region_id, 'model' : model_str}), 400
        
        if page < 1:
            page = 1
        
        h5 = hdf5_coord(user_id, file_id, resolution)
        
        model_ids = model_str.split(',')
        models, model_meta = h5.get_model(region_id, model_ids, page-1, mpp)
        h5.close()
        
        models['_links'] = {
            '_self': request.base_url + '?user_id=' + user_id + '&file_id=' + file_id + '&res=' + str(resolution) + '&region=' + str(region_id) + '&model=' + str(model_str) + '&mpp=' + str(mpp) + '&page=' +str(page+1),
            '_parent': request.url_root + 'api/3dcoord',
        }
        
        models['query_data'] = {
            'model_count' : model_meta['model_count'],
            'page_count'  : model_meta['page_count'],
            'page'        : page,
            'mpp'         : mpp
        }
        
        if (page) < model_meta['page_count']:
             models['_links']['_next_page'] = request.url_root + 'api/3dcoord/model?user_id=' + user_id + '&file_id=' + file_id + '&res=' + str(resolution) + '&region=' + str(region_id) + '&model=' + str(model_str) + '&mpp=' + str(mpp) + '&page=' +str(page+1)
        if (page) > 1:
             models['_links']['_previous_page'] = request.url_root + 'api/3dcoord/model?user_id=' + user_id + '&file_id=' + file_id + '&res=' + str(resolution) + '&region=' + str(region_id) + '&model=' + str(model_str) + '&mpp=' + str(mpp) + '&page=' +str(page-1)
        
        return models


class ping(Resource):
    """
    Class to handle the http requests to ping a service
    """
    
    def get(self):
        from . import release
        res = {
            "status":  "ready",
            "version": release.__version__,
            "author":  release.__author__,
            "license": release.__license__,
            "name":    release.__rest_name__,
            "description": release.__description__,
            "_links" : {
                '_self' : request.url_root + 'api/3dcoord/ping',
                '_parent' : request.url_root + 'api/3dcoord'
            }
        }
        return res

"""
Define the URIs and their matching methods
"""
#   List the available end points for this service
api.add_resource(GetEndPoints, "/api/3dcoord", endpoint='3dcoord_root')

#   Show the available resolutions
#   Parameters:
#    - file_id - (string)
#    - user_id - (string)
api.add_resource(GetResolutions, "/api/3dcoord/resolutions", endpoint='resolutions')

#   Show the available chromosomes for a given resolution
#   Parameters:
#    - file_id - (string)
#    - user_id - (string)
#    - res     - resolution (int)
api.add_resource(GetChromosomes, "/api/3dcoord/chromosomes", endpoint='chromosomes')

#   Show the available regions for a given chromosome, start, end and resolution
#   Parameters:
#    - file_id - (string)
#    - user_id - (string)
#    - chr     - chromosome (string)
#    - res     - resolution (int)
#    - start   - chromosome start(int)
#    - end     - chromosome end (int)
api.add_resource(GetRegions, "/api/3dcoord/regions", endpoint='regions')

#   Show the available models for a given region_id
#   Parameters:
#    - file_id   - (string)
#    - user_id   - (string)
#    - region_id - region_id (int)
api.add_resource(GetModels, "/api/3dcoord/models", endpoint='models')

#   Show the 3D coordinates of a model for a given region_id
#   Parameters:
#    - file_id   - (string)
#    - user_id   - (string)
#    - region_id - region_id (int)
#    - model_id  - model_id (string)
api.add_resource(GetModel, "/api/3dcoord/model", endpoint='model')

#   Service ping
api.add_resource(ping, "/api/3dcoord/ping", endpoint='adjacency-ping')


"""
Initialise the server
"""
if __name__ == "__main__":
    app.run()
