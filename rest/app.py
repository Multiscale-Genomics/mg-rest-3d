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

from flask import Flask, make_response, request
from flask_restful import Api, Resource

from hdf5_coord_reader import hdf5_coord

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
                '_chromosomes': request.url_root + 'api/3dcoord/getInteractions',
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
        
        h5 = hdf5_coord()
        
        resolutions = h5.get_resolutions(user_id, file_id)
        
        return {
            '_links': {
                '_self': request.base_url,
                '_parent': request.url_root + 'api/3dcoord'
            },
            'resolutions': resolutions,
        }


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
        
        h5 = hdf5_coord()
        
        chromosomes = h5.get_chromosomes(user_id, file_id, resolution)
        
        return {
            '_links': {
                '_self': request.base_url,
                '_parent': request.url_root + 'api/3dcoord'
            },
            'resolution'  : resolution,
            'chromosomes' : chromosomes
        }


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
                        'chr_id'  : ['Chromosome ID', 'str', 'REQUIRED'],
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
        
        h5 = hdf5_coord()
        
        regions = h5.get_regions(user_id, file_id, resolution, chr_id, start, end)
        
        return {
            '_links': {
                '_self': request.base_url,
                '_parent': request.url_root + 'api/3dcoord'
            },
            'resolution'  : resolution,
            'chromosomes' : chr_id,
            'regions'     : regions
        }


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
                        'user_id'   : ['User ID', 'str', 'REQUIRED'],
                        'file_id'   : ['File ID', 'str', 'REQUIRED'],
                        'region_id' : ['Regions ID', 'str', 'REQUIRED'],
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
        
        h5 = hdf5_coord()
        
        models = h5.get_models(user_id, file_id, region_id)
        
        return {
            '_links': {
                '_self': request.base_url,
                '_parent': request.url_root + 'api/3dcoord'
            },
            'region_id' : region_id,
            'models'    : models
        }


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
                        'user_id'   : ['User ID', 'str', 'REQUIRED'],
                        'file_id'   : ['File ID', 'str', 'REQUIRED'],
                        'region_id' : ['Regions ID', 'str', 'REQUIRED'],
                        'model_id'  : ['Model ID', 'str', 'REQUIRED'],
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
        
        params = [user_id, file_id, resolution, region_id, model_str]

        # Display the parameters available
        if sum([x is None for x in params]) == len(params):
            return self.usage(None, 200)
        
        # ERROR - one of the required parameters is NoneType
        if sum([x is not None for x in params]) != len(params):
            return self.usage('MissingParameters', 400, {'user_id' : user_id, 'file_id' : file_id, 'res' : resolution, 'region' : region_id, 'model' : model_str}), 400
        
        try:
            resolution = int(resolution)
        except Exception as e:
            # ERROR - one of the parameters is not of integer type
            return self.usage('IncorrectParameterType', 400, {'user_id' : user_id, 'file_id' : file_id, 'res' : resolution, 'region' : region_id, 'model' : model_str}), 400
        
        h5 = hdf5_coord()
        
        model_ids = model_str.split(',')
        models = h5.get_model(user_id, file_id, region_id, model_ids)
        
        return {
            '_links': {
                '_self': request.base_url,
                '_parent': request.url_root + 'api/3dcoord'
            },
            models
        }


class ping(Resource):
    """
    Class to handle the http requests to ping a service
    """
    
    def get(self):
        import release
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
api.add_resource(GetModels, "/api/3dcoord/model", endpoint='model')

#   Service ping
api.add_resource(ping, "/api/3dcoord/ping", endpoint='adjacency-ping')


"""
Initialise the server
"""
if __name__ == "__main__":
    app.run()
