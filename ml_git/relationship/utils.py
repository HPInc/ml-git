"""
© Copyright 2021 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import io
import os
import tempfile
import urllib

import pydot

from ml_git.constants import FileType, GraphEntityColors, DATASET_SPEC_KEY, LABELS_SPEC_KEY, MODEL_SPEC_KEY
from ml_git.utils import create_csv_file
from ml_git import log


def is_minio_storage(storage):
    """Returns True if the endpoint-url field is present and is not null."""
    return 'endpoint-url' in storage and storage['endpoint-url']


def format_storages(storages):
    """Augment existing storage information with server type, etc."""
    try:
        for bucket_type, buckets in storages.items():
            for bucket_name, bucket in buckets.items():
                bucket['name'] = bucket_name
                bucket['type'] = bucket_type
                bucket['subtype'] = ''
                if bucket_type in ('s3', 's3h'):
                    bucket['subtype'] = 'minio' if is_minio_storage(bucket) else 'aws'
    except Exception:
        log.info('Error augmenting storage information')
    return storages


def get_repo_name_from_url(repository_url: str) -> str:
    """Returns the Github repository full name from a git url or usual url format string."""
    if '://' in repository_url:
        return urllib.parse.urlparse(repository_url).path[1:].replace('.git', '')
    return repository_url.replace('.git', '').split(':')[-1]


def create_relationships_csv_file(csv_header, file_name, formatted_data, dir, export_path=False):
    file_path = os.path.join(dir, file_name)
    create_csv_file(file_path, csv_header, formatted_data)
    if export_path:
        log.info('A CSV file was created with the relationships information in {}'.format(file_path))
    with open(file_path) as csv_file:
        return io.StringIO(csv_file.read())


def __format_relationships_to_csv_data(name, type, relationships, formatted_data=None):
    for value in relationships[name]:
        from_entity_version = value.version
        from_entity_tag = value.tag
        for to_entity in value.relationships:
            formatted_data.append({
                'from_tag': from_entity_tag,
                'from_name': name,
                'from_version': from_entity_version,
                'from_type': type,
                'to_tag': to_entity.tag,
                'to_name': to_entity.name,
                'to_version': to_entity.version,
                'to_type': to_entity.type
            })
    return formatted_data


def __get_file_name(entities, type):
    file_name_prefix = 'project'
    if len(entities) == 1:
        file_name_prefix = entities[0].name
    return '{}_relationships.{}'.format(file_name_prefix, type)


def export_relationships_to_csv(entities, relationships, export_path):
    csv_header = ['from_tag', 'from_name', 'from_version', 'from_type', 'to_tag', 'to_name', 'to_version', 'to_type']
    formatted_data = []
    for entity in entities:
        formatted_data = __format_relationships_to_csv_data(entity.name, entity.type, relationships, formatted_data)

    file_name = __get_file_name(entities, FileType.CSV.value)

    if export_path is None:
        with tempfile.TemporaryDirectory() as tempdir:
            file_path = os.path.join(tempdir, file_name)
            create_csv_file(file_path, csv_header, formatted_data)
            with open(file_path) as csv_file:
                return io.StringIO(csv_file.read())
    else:
        file_path = os.path.join(export_path, file_name)
        create_csv_file(file_path, csv_header, formatted_data)
        log.info('A CSV file was created with the relationship information in {}'.format(file_path))
        with open(file_path) as csv_file:
            return io.StringIO(csv_file.read())


def __format_relationships_to_dot(entities, relationships):
    colors = {
        DATASET_SPEC_KEY: GraphEntityColors.DATASET_COLOR.value,
        LABELS_SPEC_KEY: GraphEntityColors.LABEL_COLOR.value,
        MODEL_SPEC_KEY: GraphEntityColors.MODEL_COLOR.value
    }
    graph = pydot.Dot('Entities Graph', graph_type='digraph')

    for entity in entities:
        for relationship in relationships[entity.name]:
            __add_relationships_to_dot_graph(graph, entity, relationship, colors)

    if not graph.get_nodes():
        return ''

    return graph.to_string()


def __add_relationships_to_dot_graph(graph, entity, relationship, colors):
    from_entity_version = relationship.version
    from_entity_formatted = '{} ({})'.format(entity.name, from_entity_version)
    if not relationship.relationships:
        graph.add_node(pydot.Node(from_entity_formatted, color=colors[entity.type]))
    for to_entity in relationship.relationships:
        to_entity_formatted = '{} ({})'.format(to_entity.name, to_entity.version)
        graph.add_node(pydot.Node(from_entity_formatted, color=colors[entity.type]))
        graph.add_node(pydot.Node(to_entity_formatted, color=colors[to_entity.type]))
        graph.add_edge(pydot.Edge(from_entity_formatted, to_entity_formatted))


def export_relationships_to_dot(entities, relationships, export_path):
    dot_data = __format_relationships_to_dot(entities, relationships)

    file_name = __get_file_name(entities, FileType.DOT.value)

    if export_path:
        file_path = os.path.join(export_path, file_name)
        with open(file_path, 'w') as out:
            out.write(dot_data)
            log.info('A DOT file was created with the relationship information in {}'.format(file_path))
        return
    return dot_data
