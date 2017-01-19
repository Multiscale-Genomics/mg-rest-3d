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

from hdf5_reader import hdf5

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
                '_self' : request.url_root + 'api/adjacency/ping',
                '_parent' : request.url_root + 'api/adjacency'
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
