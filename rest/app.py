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

from flask import Flask, request
from flask_restful import Api, Resource

from reader.hdf5_coord import coord

from rest.mg_auth import authorized


APP = Flask(__name__)
#app.config['DEBUG'] = False

def help_usage(error_message, status_code,
               parameters_required, parameters_provided):
    """
    Usage Help

    Description of the basic usage patterns for GET functions for the app,
    including any parameters that were provided byt he user along with the
    available parameters that are required/optional.

    Parameters
    ----------
    error_message : str | None
        Error message detailing what has gone wrong. If there are no errors then
        None should be passed.
    status_code : int
        HTTP status code.
    parameters_required : list
        List of the text names for each paramter required by the end point. An
        empty list should be provided if there are no parameters required
    parameters_provided : dict
        Dictionary of the parameters and the matching values provided by the
        user. An empyt dictionary should be passed if there were no parameters
        provided by the user.

    Returns
    -------
    str
        JSON formated status message to display to the user
    """
    parameters = {
        'user_id': ['User ID', 'str', 'REQUIRED'],
        'file_id': ['File ID', 'str', 'REQUIRED'],
        'chrom': ['Chromosome', 'str', 'REQUIRED'],
        'start': ['Start', 'int', 'REQUIRED'],
        'end': ['End', 'int', 'REQUIRED'],
        'res': ['Resolution', 'int', 'REQUIRED'],
        'region': ['Region ID', 'int', 'REQUIRED'],
        'model': ['Model ID', 'str', 'REQUIRED'],
        'page': ['Page number (default: 0)', 'int', 'OPTIONAL'],
        'mpp': ['Models per page (default: 10; max: 100)', 'int', 'OPTIONAL'],
    }

    used_param = {k: parameters[k] for k in parameters_required if k in parameters}

    usage = {
        '_links': {
            '_self': request.base_url,
            '_parent': request.url_root + 'mug/api/dmp'
        },
        'parameters': used_param
    }
    message = {
        'usage': usage,
        'status_code': status_code
    }

    if parameters_provided:
        message['provided_parameters'] = parameters_provided

    if error_message != None:
        message['error'] = error_message

    return message

class GetEndPoints(Resource):
    """
    Class to handle the http requests for returning information about the end
    points
    """

    @staticmethod
    def get():
        """
        GET list all end points

        List of all of the end points for the current service.

        Example
        -------
        .. code-block:: none
           :linenos:

           curl -X GET http://localhost:5001/mug/api/3dcoord

        """

        return {
            '_links': {
                '_self': request.base_url,
                '_resolutions': request.url_root + 'mug/api/3dcoord/resolutions',
                '_chromosomes': request.url_root + 'mug/api/3dcoord/chromosomes',
                '_regions': request.url_root + 'mug/api/3dcoord/regions',
                '_models': request.url_root + 'mug/api/3dcoord/models',
                '_model': request.url_root + 'mug/api/3dcoord/model',
                '_ping': request.url_root + 'mug/api/3dcoord/ping',
                '_parent': request.url_root + 'mug/api'
            }
        }


class GetResolutions(Resource):
    """
    Class to handle the http requests for returning information about the
    resolutions that models have been generated for
    """

    @authorized
    def get(self, user_id):
        """
        GET List available resolutions from dataset

        Parameters
        ----------
        user_id : str
            User ID
        file_id : str
            Identifier of the file to retrieve data from

        Returns
        -------
        file : json
            JSON file listing the available resolutions within the dataset

        Examples
        --------
        .. code-block:: none
           :linenos:

           curl -X GET http://localhost:5001/mug/api/3dcoord/resolutions?user_id=test&file_id=test_file

        """
        if user_id is not None:
            file_id = request.args.get('file_id')

            params_required = ['user_id', 'file_id']
            params = [user_id, file_id]

            # Display the parameters available
            if sum([x is None for x in params]) == len(params):
                return help_usage(None, 200, params_required, {})

            # ERROR - one of the required parameters is NoneType
            if sum([x is not None for x in params]) != len(params):
                return help_usage(
                    'MissingParameters',
                    400,
                    params_required,
                    {'user_id': user_id, 'file_id': file_id}
                )

            hdf5_handle = coord(user_id, file_id)
            resolution_list = hdf5_handle.get_resolutions()
            hdf5_handle.close()

            data = {}

            resolutions = []
            for res in resolution_list:
                chr_url = request.url_root
                chr_url += 'mug/api/3dcoord/chromosomes?user_id=' + user_id
                chr_url += '&file_id=' + file_id
                chr_url += '&res=' + str(res)
                resolutions.append(
                    {
                        'resolution': res,
                        '_links': {
                            '_chromosomes': chr_url
                        }
                    }
                )

            data['resolutions'] = resolutions

            data['_links'] = {
                '_self': request.base_url + '?user_id=' + user_id + '&file_id=' + file_id,
                '_parent': request.url_root + 'mug/api/3dcoord'
            }

            return data

        return help_usage('Forbidden', 403, ['file_id'], {})


class GetChromosomes(Resource):
    """
    Class to handle the http requests for returning information about the
    chromosomes that the models have been generated across
    """

    @authorized
    def get(self, user_id):
        """
        GET List available chromosomes from dataset

        Parameters
        ----------
        user_id : str
            User ID
        file_id : str
            Identifier of the file to retrieve data from
        res : int
            Resolution

        Returns
        -------
        file : json
            JSON file listing the available chromosomes within a dataset at a
            given resolution

        Examples
        --------
        .. code-block:: none
           :linenos:

           curl -X GET http://localhost:5001/mug/api/3dcoord/chromosomes?user_id=test&file_id=test_file

        """
        if user_id is None:
            file_id = request.args.get('file_id')
            resolution = request.args.get('res')

            params_required = ['user_id', 'file_id', 'res']
            params = [user_id, file_id, resolution]

            # Display the parameters available
            if sum([x is None for x in params]) == len(params):
                return help_usage(None, 200, params_required, {})

            # ERROR - one of the required parameters is NoneType
            if sum([x is not None for x in params]) != len(params):
                return help_usage(
                    'MissingParameters',
                    400,
                    params_required,
                    {'user_id': user_id, 'file_id': file_id}
                )

            try:
                resolution = int(resolution)
            except ValueError:
                # ERROR - one of the parameters is not of integer type
                return help_usage(
                    'IncorrectParameterType',
                    400,
                    params_required,
                    {'user_id': user_id, 'file_id': file_id, 'res': resolution}
                )

            hdf5_handle = coord(user_id, file_id, resolution)
            chromosome_list = hdf5_handle.get_chromosomes()
            hdf5_handle.close()

            data = {}

            chromosomes = []
            for chrom in chromosome_list:
                region_url = request.url_root
                region_url += 'mug/api/3dcoord/regions?user_id=' + user_id
                region_url += '&file_id=' + file_id
                region_url += '&res=' + str(resolution)
                region_url += '&chrom=' + str(chrom)
                region_url += '&start=0&end=1000000000'
                chromosomes.append(
                    {
                        'chromosome': chrom,
                        '_links': {
                            '_regions': region_url
                        }
                    }
                )

            data['resolution'] = resolution
            data['chromosomes'] = chromosomes

            self_url = request.base_url + '?user_id=' + user_id + '&file_id=' + file_id + '&res=' + str(resolution),
            res_url = request.url_root + 'mug/api/3dcoord/resolutions?user_id=' + user_id + '&file_id=' + file_id
            data['_links'] = {
                '_self': self_url,
                '_parent': request.url_root + 'mug/api/3dcoord',
                '_resolution': res_url
            }

            return data

        return help_usage('Forbidden', 403, ['file_id', 'res'], {})


class GetRegions(Resource):
    """
    Class to handle the http requests for returning information about the
    regions that are available in a given region and level of resolution
    """

    @authorized
    def get(self, user_id):
        """
        GET List available models from dataset

        Parameters
        ----------
        user_id : str
            User ID
        file_id : str
            Identifier of the file to retrieve data from
        res : int
            Resolution
        chrom : str
            Chromosome identifier (1, 2, 3, chr1, chr2, chr3, I, II, III, etc)
            for the chromosome of interest
        start : int
            Start position for a selected region
        end : int
            End position for a selected region

        Returns
        -------
        file : json
            JSON file listing the available models within a dataset at a
            given resolution and chromosomal region

        Examples
        --------
        .. code-block:: none
           :linenos:

           curl -X GET http://localhost:5001/mug/api/3dcoord/regions?user_id=test&file_id=test_file&res=1000000&chrom=1&start=1&end=1000000

        """
        if user_id is not None:
            file_id = request.args.get('file_id')
            resolution = request.args.get('res')
            chr_id = request.args.get('chrom')
            start = request.args.get('start')
            end = request.args.get('end')

            params_required = ['user_id', 'file_id', 'res', 'chrom', 'start', 'end']
            params = [user_id, file_id, resolution, chr_id, start, end]

            # Display the parameters available
            if sum([x is None for x in params]) == len(params):
                return help_usage(None, 200, params_required, {})

            # ERROR - one of the required parameters is NoneType
            if sum([x is not None for x in params]) != len(params):
                return help_usage(
                    'MissingParameters',
                    400,
                    params_required,
                    {
                        'user_id': user_id,
                        'file_id': file_id,
                        'res': resolution,
                        'chrom': chr_id,
                        'start': start,
                        'end': end
                    }
                )

            try:
                start = int(start)
                end = int(end)
                resolution = int(resolution)
            except ValueError:
                # ERROR - one of the parameters is not of integer type
                return help_usage(
                    'IncorrectParameterType',
                    400,
                    params_required,
                    {
                        'user_id': user_id,
                        'file_id': file_id,
                        'res': resolution,
                        'chrom': chr_id,
                        'start': start,
                        'end': end
                    }
                )

            hdf5_handle = coord(user_id, file_id, resolution)
            region_list = hdf5_handle.get_regions(chr_id, start, end)
            hdf5_handle.close()

            data = {}
            regions = []
            for reg in region_list:
                model_url = request.url_root + 'mug/api/3dcoord/models?user_id=' + user_id
                model_url += '&file_id=' + file_id
                model_url += '&res=' + str(resolution)
                model_url += '&region=' + reg
                regions.append(
                    {
                        'region_id': reg,
                        '_links': {
                            '_models': model_url
                        }
                    }
                )

            data['resolution'] = resolution,
            data['chromosome'] = chr_id,
            data['regions'] = regions

            data['_links'] = {
                '_self': request.base_url + '?user_id=' + user_id + '&file_id=' + file_id + '&res=' + str(resolution) + '&chrom=' + str(chr_id) + '&start=' + str(start) + '&end=' + str(end),
                '_parent': request.url_root + 'mug/api/3dcoord',
                '_resolution': request.url_root + 'mug/api/3dcoord/resolutions?user_id=' + user_id + '&file_id=' + file_id,
                '_chromosomes': request.url_root + 'mug/api/3dcoord/chromosomes?user_id=' + user_id + '&file_id=' + file_id + '&res=' + str(resolution)
            }

            return data

        return help_usage('Forbidden', 403, ['file_id', 'res', 'chrom', 'start', 'end'], {})


class GetModels(Resource):
    """
    Class to handle the http requests for returning information about the models
    that are available within a given region.
    """

    @authorized
    def get(self, user_id):
        """
        GET List available models from dataset

        Parameters
        ----------
        user_id : str
            User ID
        file_id : str
            Identifier of the file to retrieve data from
        res : int
            Resolution
        region : str
            Region ID

        Returns
        -------
        file : json
            JSON file listing the available models within a dataset at a
            given resolution and chromosomal region

        Examples
        --------
        .. code-block:: none
           :linenos:

           curl -X GET http://localhost:5001/mug/api/3dcoord/models?user_id=test&file_id=test_file&res=1000000&region=1

        """
        if user_id is not None:
            file_id = request.args.get('file_id')
            resolution = request.args.get('res')
            region_id = request.args.get('region')

            params_required = ['user_id', 'file_id', 'res', 'region']
            params = [user_id, file_id, resolution, region_id]

            # Display the parameters available
            if sum([x is None for x in params]) == len(params):
                return help_usage(None, 200, params_required, {})

            # ERROR - one of the required parameters is NoneType
            if sum([x is not None for x in params]) != len(params):
                return help_usage(
                    'MissingParameters',
                    400,
                    params_required,
                    {
                        'user_id': user_id,
                        'file_id': file_id,
                        'res': resolution,
                        'region': region_id
                    }
                )

            try:
                resolution = int(resolution)
            except ValueError:
                # ERROR - one of the parameters is not of integer type
                return help_usage(
                    'IncorrectParameterType',
                    400,
                    params_required,
                    {
                        'user_id': user_id,
                        'file_id': file_id,
                        'res': resolution,
                        'region': region_id
                    }
                )

            hdf5_handle = coord(user_id, file_id, resolution)
            model_list = hdf5_handle.get_models(region_id)
            region_list = hdf5_handle.get_region_order(region=region_id)
            hdf5_handle.close()

            models = {}
            models['model_list'] = [
                {
                    'model': str(m[0]),
                    'cluster': str(m[1]),
                    '_links': {
                        '_model': request.url_root + 'mug/api/3dcoord/model?user_id=' + user_id + '&file_id=' + file_id + '&res=' + str(resolution) + '&region=' + str(region_id) + '&model=' + str(m[0])
                    }
                } for m in model_list
            ]

            models['_links'] = {
                '_self': request.base_url + '?user_id=' + user_id + '&file_id=' + file_id + '&res=' + str(resolution) + '&region=' + str(region_id),
                '_parent': request.url_root + 'mug/api/3dcoord',
                '_models_all': request.url_root + 'mug/api/3dcoord/model?user_id=' + user_id + '&file_id=' + file_id + '&res=' + str(resolution) + '&region=' + str(region_id) + '&model=all'
            }

            current_region = region_list.index(region_id)
            next_region = current_region+1
            previous_region = current_region-1

            if current_region < (len(region_list)-1):
                models['_links']['_next_region'] = request.url_root + 'mug/api/3dcoord/models?user_id=' + user_id + '&file_id=' + file_id + '&res=' + str(resolution) + '&region=' + region_list[next_region]
            if current_region > 0:
                models['_links']['_previous_region'] = request.url_root + 'mug/api/3dcoord/models?user_id=' + user_id + '&file_id=' + file_id + '&res=' + str(resolution) + '&region=' + region_list[previous_region]

            return models

        return help_usage('Forbidden', 403, ['file_id', 'res', 'region'], {})


class GetModel(Resource):
    """
    Class to handle the http requests for returning the models from a given
    region. The list of models is a comma separated list that can return
    multiple models from the same region
    """

    @authorized
    def get(self, user_id):
        """
        GET List available model from dataset

        Parameters
        ----------
        user_id : str
            User ID
        file_id : str
            Identifier of the file to retrieve data from
        res : int
            Resolution
        region : str
            Region ID
        model : str
            model ID

        Returns
        -------
        file : json
            JSON file listing the available models within a dataset at a
            given resolution and chromosomal region

        Examples
        --------
        .. code-block:: none
           :linenos:

           curl -X GET http://localhost:5001/mug/api/3dcoord/model?user_id=test&file_id=test_file&region=1&model=model1

        """
        if user_id is not None:
            file_id = request.args.get('file_id')
            resolution = request.args.get('res')
            region_id = request.args.get('region')
            model_str = request.args.get('model')
            page = request.args.get('page')
            mpp = request.args.get('mpp')

            params_required = ['user_id', 'file_id', 'res', 'region', 'model']
            params = [user_id, file_id, resolution, region_id, model_str]

            # Display the parameters available
            if sum([x is None for x in params]) == len(params):
                return help_usage(None, 200, params_required, {})

            # ERROR - one of the required parameters is NoneType
            if sum([x is not None for x in params]) != len(params):
                return help_usage(
                    'MissingParameters',
                    400,
                    params_required,
                    {
                        'user_id': user_id,
                        'file_id': file_id,
                        'res': resolution,
                        'region': region_id,
                        'model': model_str
                    }
                )

            if page is None:
                page = 1

            if mpp is None:
                mpp = 10

            try:
                resolution = int(resolution)
                page = int(page)
                mpp = int(mpp)
            except ValueError:
                # ERROR - one of the parameters is not of integer type
                return help_usage(
                    'IncorrectParameterType',
                    400,
                    params_required,
                    {
                        'user_id': user_id,
                        'file_id': file_id,
                        'res': resolution,
                        'region': region_id,
                        'model': model_str
                    }
                )

            if page < 1:
                page = 1

            hdf5_handle = coord(user_id, file_id, resolution)

            model_ids = model_str.split(',')
            models, model_meta = hdf5_handle.get_model(region_id, model_ids, page-1, mpp)
            hdf5_handle.close()

            models['_links'] = {
                '_self': request.base_url + '?user_id=' + user_id + '&file_id=' + file_id + '&res=' + str(resolution) + '&region=' + str(region_id) + '&model=' + str(model_str) + '&mpp=' + str(mpp) + '&page=' +str(page),
                '_parent': request.url_root + 'mug/api/3dcoord',
            }

            models['query_data'] = {
                'model_count': model_meta['model_count'],
                'page_count': model_meta['page_count'],
                'page': page,
                'mpp': mpp
            }

            if (page) < model_meta['page_count']:
                models['_links']['_next_page'] = request.url_root + 'mug/api/3dcoord/model?user_id=' + user_id + '&file_id=' + file_id + '&res=' + str(resolution) + '&region=' + str(region_id) + '&model=' + str(model_str) + '&mpp=' + str(mpp) + '&page=' +str(page+1)
            if (page) > 1:
                models['_links']['_previous_page'] = request.url_root + 'mug/api/3dcoord/model?user_id=' + user_id + '&file_id=' + file_id + '&res=' + str(resolution) + '&region=' + str(region_id) + '&model=' + str(model_str) + '&mpp=' + str(mpp) + '&page=' +str(page-1)

            return models

        return help_usage('Forbidden', 403, ['file_id', 'res', 'region', 'model'], {})


class Ping(Resource):
    """
    Class to handle the http requests to ping a service
    """

    @staticmethod
    def get():
        """
        GET Status

        List the current status of the service along with the relevant
        information about the version.

        Example
        -------
        .. code-block:: none
           :linenos:

           curl -X GET http://localhost:5001/mug/api/3dcoord/ping

        """
        from . import release
        res = {
            "status":  "ready",
            "version": release.__version__,
            "author":  release.__author__,
            "license": release.__license__,
            "name":    release.__rest_name__,
            "description": release.__description__,
            "_links": {
                '_self': request.url_root + 'mug/api/3dcoord/ping',
                '_parent': request.url_root + 'mug/api/3dcoord'
            }
        }
        return res

################################################################################

API = Api(APP)

"""
Define the URIs and their matching methods
"""
#   List the available end points for this service
API.add_resource(GetEndPoints, "/mug/api/3dcoord", endpoint='3dcoord_root')

#   Show the available resolutions
API.add_resource(GetResolutions, "/mug/api/3dcoord/resolutions", endpoint='resolutions')

#   Show the available chromosomes for a given resolution
API.add_resource(GetChromosomes, "/mug/api/3dcoord/chromosomes", endpoint='chromosomes')

#   Show the available regions for a given chromosome, start, end and resolution
API.add_resource(GetRegions, "/mug/api/3dcoord/regions", endpoint='regions')

#   Show the available models for a given region_id
API.add_resource(GetModels, "/mug/api/3dcoord/models", endpoint='models')

#   Show the 3D coordinates of a model for a given region_id
API.add_resource(GetModel, "/mug/api/3dcoord/model", endpoint='model')

#   Service ping
API.add_resource(Ping, "/mug/api/3dcoord/ping", endpoint='adjacency-ping')


# Initialise the server
if __name__ == "__main__":
    APP.run()
