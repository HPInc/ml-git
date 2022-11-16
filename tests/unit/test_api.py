"""
© Copyright 2021 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""
import base64
import csv
import json
import os
import unittest

import pydot
import pytest

from ml_git.constants import EntityType, STORAGE_CONFIG_KEY, StorageType, MutabilityType, FileType
from ml_git.spec import get_spec_key
from ml_git.utils import yaml_save

dummy_api_github_url = 'https://api.github.com:443'
dummy_git_repo = 'https://github.com/dummy/dummy_{}_repo.git'

dummy_config = {
    EntityType.DATASETS.value: {'git': dummy_git_repo.format(EntityType.DATASETS.value)},
    EntityType.MODELS.value: {'git': dummy_git_repo.format(EntityType.MODELS.value)},
    EntityType.LABELS.value: {'git': dummy_git_repo.format(EntityType.LABELS.value)},

    STORAGE_CONFIG_KEY: {
        StorageType.S3.value: {
            'mlgit-bucket': {
                'region': 'us-east-1',
                'aws-credentials': {'profile': 'default'}
            }
        }
    },
}

search_repo_url = '{}/repos/dummy/dummy_{}_repo'  # dummy_api_github_url
search_code_url = '{}/search/code?q=repo%3Adummy_{}+extension%3A.spec'  # dummy_api_github_url
entity_content_url = '{}/repos/dummy_{}_repo/contents/{}-ex/{}-ex.spec'
get_repo_url = '{}/dummy_{}_repo'  # dummy_api_github_url.replace("api.","")
get_tags_from_repo_url = '{}/repos/dummy_{}_repo/tags'
get_spec_content_url = '{}/repos/dummy/dummy_{}_repo/contents/{}-ex/{}-ex.spec?ref=test__{}-ex__1'

dummy_config_remote_url = f'{dummy_api_github_url}/repos/dummy/dummy_config'
dummy_config_content_url = f'{dummy_api_github_url}/repos/dummy/dummy_config/contents//.ml-git/config.yaml'

rate_limit_url = '{}/rate_limit'  # dummy_rate_limit_github_url


def get_search_repo_response(type):
    return {
            'id': 310705171,
            'name': 'dummy_{}'.format(type),
            'full_name': 'dummy_{}'.format(type),
            'private': False,
            'owner': {
                'login': 'dummy',
                'id': 24386872,
                'url': 'https://github.com/dummy_{}_repo'.format(type),
                'html_url': 'https://github.com/dummy_{}_repo'.format(type),
                'type': 'User',
                'site_admin': False
            },
            'html_url': 'https://github.com/dummy_{}_repo'.format(type),
            'url': 'https://api.github.com/repos/dummy_{}_repo'.format(type),
            'git_url': 'git://github.com/dummy_{}.git'.format(type),
            'ssh_url': 'git@github.com:dummy/dummy_{}.git'.format(type),
        }


def get_search_code_response(type):
    return {
        'total_count': 1,
        'incomplete_results': False,
        'items': [
            {
                'name': '{}-ex.spec'.format(type),
                'path': '{}-ex/{}-ex.spec'.format(type, type),
            }
        ]
    }


def encode_content(content):
    return base64.b64encode(json.dumps(content).encode('ascii')).decode('utf-8')


def get_sample_spec(type):
    spec_test = {
        get_spec_key(type): {
            'categories': ['test'],
            'manifest': {
                'amount': 2,
                'files': 'MANIFEST.yaml',
                'size': '7.2 kB',
                'storage': 's3h://mlgit-bucket'
            },
            'mutability': 'mutable',
            'name': '{}-ex'.format(type),
            'version': 1
        }
    }

    if type == EntityType.MODELS.value:
        spec_test[get_spec_key(type)][get_spec_key(EntityType.DATASETS.value)] = {'tag': 'test__datasets-ex__1'}
        spec_test[get_spec_key(type)][get_spec_key(EntityType.LABELS.value)] = {'tag': 'test__labels-ex__1'}
    elif type == EntityType.LABELS.value:
        spec_test[get_spec_key(type)][get_spec_key(EntityType.DATASETS.value)] = {'tag': 'test__datasets-ex__1'}
    return spec_test


def get_spec_entity_content(type):
    return {
        'name': '{}-ex.spec'.format(type),
        'path': '{}-ex/{}-ex.spec'.format(type, type),
        'sha': '4997e46c183cbbe23bbeecbb9a336555e24a16e8',
        'size': 191,
        'type': 'file',
        'content': encode_content(get_sample_spec(type)),
        'encoding': 'base64',
    }


repo = {
    'login': 'dummy',
    'id': 24386872,
    'type': 'User',
    'site_admin': False,
    'name': 'dummy',
}


def get_repo_tags(type):
    return [
        {
            'name': 'test__{}-ex__1'.format(type),
        }
    ]


def get_content_from_tag(type):
    return {
        'name': '{}-ex.spec'.format(type),
        'path': '{}-ex/{}-ex.spec'.format(type, type),
        'sha': '73c20aceff15b737b37b674e84e321b6d4a461e5',
        'size': 203,
        'type': 'file',
        'content': encode_content(get_sample_spec(type)),
        'encoding': 'base64',
    }


config_repo_response = {
    'id': 310705171,
    'name': 'dummy_config',
    'full_name': 'dummy_config',
    'private': False,
    'owner': {
        'login': 'dummy',
        'id': 24386872,
        'url': 'https://github.com/dummy/dummy_config',
        'html_url': 'https://github.com/dummy/dummy_config',
        'type': 'User',
        'site_admin': False
    },
    'html_url': 'https://github.com/dummy/dummy_config',
    'url': 'https://api.github.com/repos/dummy/dummy_config',
    'git_url': 'git://github.com/dummy/dummy_config.git',
    'ssh_url': 'git@github.com:dummy/dummy/dummy_config.git',
}

config_content_response = {
    'name': 'config.yaml',
    'path': '.ml-git/config.yaml',
    'sha': 'ebd3e03e034e3bde8799083e7ab76e058581c4a7',
    'size': 379,
    'type': 'file',
    'content': encode_content(dummy_config),
    'encoding': 'base64',
}

rate_limit_response = {
    'resources': {
        'core': {
          'limit': 10,
          'remaining': 4999,
          'reset': 1372700873,
          'used': 1
        },
        'search': {
          'limit': 10,
          'remaining': 18,
          'reset': 1372697452,
          'used': 12
        },
        'graphql': {
          'limit': 5000,
          'remaining': 4993,
          'reset': 1372700389,
          'used': 7
        },
        'integration_manifest': {
          'limit': 5000,
          'remaining': 4999,
          'reset': 1551806725,
          'used': 1
        },
        'code_scanning_upload': {
          'limit': 500,
          'remaining': 499,
          'reset': 1551806725,
          'used': 1
        }
    },
    'rate': {
        'limit': 5000,
        'remaining': 4999,
        'reset': 1372700873,
        'used': 1
    }
}

HEADERS = {
    'date': 'Fri, 12 Oct 2012 23:33:14 GMT',
    'access-control-allow-origin': '*',
    'access-control-expose-headers': 'ETag, Link, Location, Retry-After, X-GitHub-OTP, X-RateLimit-Limit,'
                                     ' X-RateLimit-Remaining, X-RateLimit-Used, X-RateLimit-Reset, X-OAuth-Scopes,'
                                     ' X-Accepted-OAuth-Scopes, X-Poll-Interval, X-GitHub-Media-Type,'
                                     ' Deprecation, Sunset',
    'cache-control': 'private, max-age=60, s-maxage=60',
    'content-security-policy': 'default-src \'none\'',
    'content-type': 'application/json; charset=utf-8',
    'vary': 'Accept, Authorization, Cookie, X-GitHub-OTP, Accept-Encoding, Accept, X-Requested-With',
    'x-github-media-type': 'github.v3; format=json',
    'x-oauth-scopes': 'public_repo, repo:status, repo_deployment',
    'transfer-encoding': 'chunked'
}


@pytest.mark.usefixtures('tmp_dir')
class ApiTestCases(unittest.TestCase):

    @pytest.fixture(autouse=True)
    def requests_mock(self, requests_mock):
        self.requests_mock = requests_mock

    def setUp_mock(self, type):
        self.requests_mock.get(search_repo_url.format(dummy_api_github_url, type), status_code=200,
                               headers=HEADERS, json=get_search_repo_response(type))
        self.requests_mock.get(search_code_url.format(dummy_api_github_url, type), status_code=200,
                               headers=HEADERS, json=get_search_code_response(type))
        self.requests_mock.get(
            entity_content_url.format(dummy_api_github_url, type, type, type, type),
            status_code=200, headers=HEADERS, json=get_spec_entity_content(type))
        self.requests_mock.get(get_repo_url.format(dummy_api_github_url.replace('api.', ''), type),
                               status_code=200, headers=HEADERS, json=repo)
        self.requests_mock.get(get_tags_from_repo_url.format(dummy_api_github_url, type), status_code=200,
                               headers=HEADERS, json=get_repo_tags(type))
        self.requests_mock.get(
            get_spec_content_url.format(dummy_api_github_url, type, type, type, type),
            status_code=200, headers=HEADERS, json=get_content_from_tag(type))
        self.requests_mock.get(rate_limit_url.format(dummy_api_github_url), status_code=200,
                               headers=HEADERS, json=rate_limit_response)

    def setUp(self):
        from ml_git import api
        self.manager = api.init_entity_manager('github_token', 'https://api.github.com')
        self.config_path = os.path.join(self.tmp_dir, 'config.yaml')
        yaml_save(dummy_config, self.config_path)
        self.setUp_mock(EntityType.DATASETS.value)
        self.setUp_mock(EntityType.LABELS.value)
        self.setUp_mock(EntityType.MODELS.value)

    def test_init_entity_manager(self):
        self.assertIsNotNone(self.manager)

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_get_entities_from_config_path(self):
        entities = self.manager.get_entities(config_path=self.config_path)
        self.assertEqual(3, len(entities))
        self.assertEqual(entities[0].name, 'datasets-ex')
        self.assertEqual(entities[1].name, 'labels-ex')
        self.assertEqual(entities[2].name, 'models-ex')

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_get_entities_from_repo_name(self):
        self.requests_mock.get(dummy_config_remote_url, status_code=200, headers=HEADERS, json=config_repo_response)
        self.requests_mock.get(dummy_config_content_url, status_code=200, headers=HEADERS, json=config_content_response)
        entities = self.manager.get_entities(config_repo_name='dummy/dummy_config')
        self.assertEqual(3, len(entities))
        self.assertEqual(entities[0].name, 'datasets-ex')
        self.assertEqual(entities[1].name, 'labels-ex')
        self.assertEqual(entities[2].name, 'models-ex')

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_get_entity_spec_path(self):
        self.requests_mock.get(dummy_config_remote_url, status_code=200, headers=HEADERS, json=config_repo_response)
        repository = self.manager._manager.find_repository('dummy/dummy_datasets_repo')
        spec_path = self.manager._get_entity_spec_path(repository, 'datasets-ex')
        self.assertEqual('datasets-ex/datasets-ex.spec', spec_path)
        with self.assertRaises(Exception):
            self.manager._get_entity_spec_path(repository, 'worng-dataset-name')

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_get_entity_versions(self):
        self.requests_mock.get(dummy_config_remote_url, status_code=200, headers=HEADERS, json=config_repo_response)
        entity_versions = self.manager.get_entity_versions('datasets-ex', 'dummy/dummy_datasets_repo')
        self.assertTrue(len(entity_versions) == 1)
        self.assertEqual(entity_versions[0].version, 1)
        self.assertEqual(entity_versions[0].tag, 'test__datasets-ex__1')
        self.assertEqual(entity_versions[0].mutability, MutabilityType.MUTABLE.value)
        self.assertEqual(entity_versions[0].categories, ['test'])
        self.assertEqual(entity_versions[0].storage.type, StorageType.S3H.value)
        self.assertEqual(entity_versions[0].storage.bucket, 'mlgit-bucket')
        self.assertEqual(entity_versions[0].total_versioned_files, 2)
        self.assertEqual(entity_versions[0].size, '7.2 kB')

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_get_linked_entities(self):
        self.requests_mock.get(dummy_config_remote_url, status_code=200, headers=HEADERS, json=config_repo_response)
        self.requests_mock.get(dummy_config_content_url, status_code=200, headers=HEADERS, json=config_content_response)
        related_entities = self.manager.get_linked_entities('models-ex', 1, 'dummy/dummy_models_repo')
        self.assertEqual(2, len(related_entities))
        self.assertEqual(related_entities[0].tag, 'test__datasets-ex__1')
        self.assertEqual(related_entities[1].tag, 'test__labels-ex__1')

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_get_entity_relationships(self):
        entity_name = 'models-ex'
        output = self.manager.get_entity_relationships(entity_name, 'dummy/dummy_models_repo')
        self.assertEqual('test__models-ex__1', output[entity_name][0].tag)
        self.assertEqual(1, output[entity_name][0].version)
        entity_relationships = output[entity_name][0].relationships
        self.assertEqual(2, len(entity_relationships))
        self.assertEqual('test__datasets-ex__1', entity_relationships[0].tag)
        self.assertEqual('test__labels-ex__1', entity_relationships[1].tag)

        with self.assertRaises(Exception):
            self.manager.get_entity_relationships('worng-model-name', 'dummy/dummy_models_repo')

        unlinked_entity = self.manager.get_entity_relationships('datasets-ex', 'dummy/dummy_datasets_repo')
        self.assertEqual([], unlinked_entity['datasets-ex'][0].relationships)

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_get_entity_relationships_export_to_csv(self):
        self.manager.get_entity_relationships('models-ex', 'dummy/dummy_models_repo', export_type=FileType.CSV.value, export_path='.')
        file_path = os.path.join(self.tmp_dir, 'models-ex_relationships.csv')
        self.assertTrue(os.path.exists(file_path))
        with open(file_path) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    expected_data = 'from_tag,from_name,from_version,from_type,to_tag,to_name,to_version,to_type'
                elif line_count == 1:
                    expected_data = 'test__models-ex__1,models-ex,1,model,test__datasets-ex__1,datasets-ex,1,dataset'
                else:
                    expected_data = 'test__models-ex__1,models-ex,1,model,test__labels-ex__1,labels-ex,1,labels'
                line_count += 1
                self.assertEqual(expected_data, ','.join(row))

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_get_entity_relationships_export_to_dot(self):
        self.manager.get_entity_relationships('models-ex', 'dummy/dummy_models_repo', export_type=FileType.DOT.value, export_path='.')
        file_path = os.path.join(self.tmp_dir, 'models-ex_relationships.dot')
        self.assertTrue(os.path.exists(file_path))

        with open(file_path) as dot_file:
            graph = pydot.graph_from_dot_data(dot_file.read())[0]
            self.assertEqual(graph.get_graph_type(), 'digraph')
            models = graph.get_node('"models-ex (1)"')
            datasets = graph.get_node('"datasets-ex (1)"')
            labels = graph.get_node('"labels-ex (1)"')
            self.assertIsNotNone(models)
            self.assertIsNotNone(datasets)
            self.assertIsNotNone(labels)
            self.assertEqual(graph.get_edges()[0].get_source(), models[0].get_name())
            self.assertEqual(graph.get_edges()[0].get_destination(), datasets[0].get_name())
            self.assertEqual(graph.get_edges()[1].get_source(), models[0].get_name())
            self.assertEqual(graph.get_edges()[1].get_destination(), labels[0].get_name())

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_get_project_entities_relationships(self):
        self.requests_mock.get(dummy_config_remote_url, status_code=200, headers=HEADERS, json=config_repo_response)
        self.requests_mock.get(dummy_config_content_url, status_code=200, headers=HEADERS, json=config_content_response)
        entities_relationships = self.manager.get_project_entities_relationships('dummy/dummy_config')
        self.assertEqual(3, len(entities_relationships))
        entity_name = 'models-ex'
        self.assertEqual('test__models-ex__1', entities_relationships['models'][entity_name][0].tag)
        self.assertEqual(1, entities_relationships['models'][entity_name][0].version)
        entity_relationships = entities_relationships['models'][entity_name][0].relationships
        self.assertEqual(2, len(entity_relationships))
        self.assertEqual('test__datasets-ex__1', entity_relationships[0].tag)
        self.assertEqual('test__labels-ex__1', entity_relationships[1].tag)

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_get_project_entities_relationships_export_to_csv(self):
        self.requests_mock.get(dummy_config_remote_url, status_code=200, headers=HEADERS, json=config_repo_response)
        self.requests_mock.get(dummy_config_content_url, status_code=200, headers=HEADERS, json=config_content_response)
        self.manager.get_project_entities_relationships('dummy/dummy_config', export_type=FileType.CSV.value, export_path='.')
        file_path = os.path.join(self.tmp_dir, 'project_relationships.csv')
        self.assertTrue(os.path.exists(file_path))
        with open(file_path) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    expected_data = 'from_tag,from_name,from_version,from_type,to_tag,to_name,to_version,to_type'
                elif line_count == 1:
                    expected_data = 'test__labels-ex__1,labels-ex,1,labels,test__datasets-ex__1,datasets-ex,1,dataset'
                elif line_count == 2:
                    expected_data = 'test__models-ex__1,models-ex,1,model,test__datasets-ex__1,datasets-ex,1,dataset'
                else:
                    expected_data = 'test__models-ex__1,models-ex,1,model,test__labels-ex__1,labels-ex,1,labels'
                line_count += 1
                self.assertEqual(expected_data, ','.join(row))

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_get_project_entities_relationships_export_to_dot(self):
        self.requests_mock.get(dummy_config_remote_url, status_code=200, headers=HEADERS, json=config_repo_response)
        self.requests_mock.get(dummy_config_content_url, status_code=200, headers=HEADERS, json=config_content_response)
        self.manager.get_project_entities_relationships('dummy/dummy_config', export_type=FileType.DOT.value, export_path='.')
        file_path = os.path.join(self.tmp_dir, 'project_relationships.dot')
        self.assertTrue(os.path.exists(file_path))

        with open(file_path) as dot_file:
            graph = pydot.graph_from_dot_data(dot_file.read())[0]
            self.assertEqual(graph.get_graph_type(), 'digraph')
            models = graph.get_node('"models-ex (1)"')
            datasets = graph.get_node('"datasets-ex (1)"')
            labels = graph.get_node('"labels-ex (1)"')
            self.assertIsNotNone(models)
            self.assertIsNotNone(datasets)
            self.assertIsNotNone(labels)
            self.assertEqual(graph.get_edges()[0].get_source(), labels[0].get_name())
            self.assertEqual(graph.get_edges()[0].get_destination(), datasets[0].get_name())
            self.assertEqual(graph.get_edges()[1].get_source(), models[0].get_name())
            self.assertEqual(graph.get_edges()[1].get_destination(), datasets[0].get_name())
            self.assertEqual(graph.get_edges()[2].get_source(), models[0].get_name())
            self.assertEqual(graph.get_edges()[2].get_destination(), labels[0].get_name())
