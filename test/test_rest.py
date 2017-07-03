"""
.. Copyright 2017 EMBL-European Bioinformatics Institute

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

import os
import tempfile
import json
import pytest

from context import app

@pytest.fixture
def client(request):
    """
    Definges the client object to make requests against
    """
    db_fd, app.APP.config['DATABASE'] = tempfile.mkstemp()
    app.APP.config['TESTING'] = True
    client = app.APP.test_client()

    def teardown():
        """
        Close the client once testing has completed
        """
        os.close(db_fd)
        os.unlink(app.APP.config['DATABASE'])
    request.addfinalizer(teardown)

    return client

def test_endpoints(client):
    """
    Test that the root endpoint is returning the expected keys
    """
    rest_value = client.get('/mug/api/3dcoord')
    details = json.loads(rest_value.data)
    print(details)
    assert '_links' in details

def test_ping(client):
    """
    Test that the ping function is returning the status key
    """
    rest_value = client.get('/mug/api/3dcoord/ping')
    details = json.loads(rest_value.data)
    print(details)
    assert 'status' in details

def test_resolutions(client):
    """
    Test that the endpoint returns the usage for resolution
    """
    rest_value = client.get('/mug/api/3dcoord/resolutions')
    details = json.loads(rest_value.data)
    print(details)
    assert 'usage' in details

def test_resolutions_00(client):
    """
    Test retrieving of available resolutions with test credentials
    """
    rest_value = client.get('/mug/api/3dcoord/resolutions?user_id=test&file_id=test')
    details = json.loads(rest_value.data)
    print(details)
    assert 'resolutions' in details

def test_chromosomes(client):
    """
    Test that the endpoint returns the usage for chromosomes
    """
    rest_value = client.get('/mug/api/3dcoord/chromosomes')
    details = json.loads(rest_value.data)
    print(details)
    assert 'usage' in details

def test_chromosomes_00(client):
    """
    Test retrieving of available chromosomes with test credentials
    """
    rest_value = client.get('/mug/api/3dcoord/resolutions?user_id=test&file_id=test')
    resolutions = json.loads(rest_value.data)
    resolution = str(resolutions['resolutions'][0]['resolution'])

    rest_value = client.get('/mug/api/3dcoord/chromosomes?user_id=test&file_id=test&res=' + resolution)
    details = json.loads(rest_value.data)
    print(details)
    assert 'resolution' in details
    assert details['resolution'] == int(resolution)
    assert 'chromosomes' in details

def test_regions(client):
    """
    Test that the endpoint returns the usage for regions
    """
    rest_value = client.get('/mug/api/3dcoord/regions')
    details = json.loads(rest_value.data)
    print(details)
    assert 'usage' in details

def test_regions_00(client):
    """
    Test retrieving of available regions with test credentials
    """
    rest_value = client.get('/mug/api/3dcoord/resolutions?user_id=test&file_id=test')
    resolutions = json.loads(rest_value.data)
    resolution = str(resolutions['resolutions'][0]['resolution'])

    rest_value = client.get('/mug/api/3dcoord/chromosomes?user_id=test&file_id=test&res=' + resolution)
    chr_details = json.loads(rest_value.data)

    chromosome = chr_details['chromosomes'][0]['chromosome']
    start = 1
    end = 30000000

    rest_value = client.get('/mug/api/3dcoord/regions?user_id=test&file_id=test&res=' + resolution + '&start=' + str(start) + '&end=' + str(end) + '&chrom=' + str(chromosome))
    details = json.loads(rest_value.data)

    print(details)
    assert 'regions' in details
    assert 'chromosome' in details
    assert details['chromosome'][0] == chromosome

def test_models(client):
    """
    Test that the endpoint returns the usage for models
    """
    rest_value = client.get('/mug/api/3dcoord/models')
    details = json.loads(rest_value.data)
    print(details)
    assert 'usage' in details

def test_models_00(client):
    """
    Test retrieving of available models with test credentials
    """
    rest_value = client.get('/mug/api/3dcoord/resolutions?user_id=test&file_id=test')
    resolutions = json.loads(rest_value.data)
    resolution = str(resolutions['resolutions'][0]['resolution'])

    rest_value = client.get('/mug/api/3dcoord/chromosomes?user_id=test&file_id=test&res=' + resolution)
    chr_details = json.loads(rest_value.data)

    chromosome = chr_details['chromosomes'][0]['chromosome']
    start = 1
    end = 30000000

    rest_value = client.get('/mug/api/3dcoord/regions?user_id=test&file_id=test&res=' + resolution + '&start=' + str(start) + '&end=' + str(end) + '&chrom=' + str(chromosome))
    regions = json.loads(rest_value.data)

    region_id = regions['regions'][0]['region_id']

    rest_value = client.get('/mug/api/3dcoord/models?user_id=test&file_id=test&res=' + resolution + '&region=' + region_id)
    details = json.loads(rest_value.data)

    print(details.keys())

    assert 'model_list' in details

def test_model(client):
    """
    Test that the endpoint returns the usage for model
    """
    rest_value = client.get('/mug/api/3dcoord/model')
    details = json.loads(rest_value.data)
    print(details)
    assert 'usage' in details

def test_model_00(client):
    """
    Test retrieving of an available an with test credentials
    """
    rest_value = client.get('/mug/api/3dcoord/resolutions?user_id=test&file_id=test')
    resolutions = json.loads(rest_value.data)
    resolution = str(resolutions['resolutions'][0]['resolution'])

    rest_value = client.get('/mug/api/3dcoord/chromosomes?user_id=test&file_id=test&res=' + resolution)
    chr_details = json.loads(rest_value.data)

    chromosome = chr_details['chromosomes'][0]['chromosome']
    start = 1
    end = 30000000

    rest_value = client.get('/mug/api/3dcoord/regions?user_id=test&file_id=test&res=' + resolution + '&start=' + str(start) + '&end=' + str(end) + '&chrom=' + str(chromosome))
    regions = json.loads(rest_value.data)

    region_id = regions['regions'][0]['region_id']

    rest_value = client.get('/mug/api/3dcoord/models?user_id=test&file_id=test&res=' + resolution + '&region=' + region_id)
    models = json.loads(rest_value.data)

    model_id = models['model_list'][0]['model']

    rest_value = client.get('/mug/api/3dcoord/model?user_id=test&file_id=test&res=' + resolution + '&region=' + region_id + '&model=' + model_id)
    details = json.loads(rest_value.data)

    print(details.keys())

    assert 'metadata' in details
