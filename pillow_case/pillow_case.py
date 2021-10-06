#!/usr/bin/env python3
# -*- coding: utf-8 -*

import os
import rdflib
import json
import logging
import hashlib
import argparse
import exif_node_maker as case_maker
from PIL import Image
from PIL.ExifTags import TAGS

parser = argparse.ArgumentParser()
parser.add_argument("file", help="file to extract exif from")
args = parser.parse_args()

__version__ = "0.1.0"

_logger = logging.getLogger(os.path.basename(__file__))

parser = argparse.ArgumentParser()
parser.add_argument("file", help="file to extract exif data from")
args = parser.parse_args()


NS_RDF = rdflib.RDF
NS_RDFS = rdflib.RDFS
NS_UCO_CORE = rdflib.Namespace("https://unifiedcyberontology.org/ontology/uco/core#")
NS_UCO_LOCATION = rdflib.Namespace("https://unifiedcyberontology.org/ontology/uco/location#")
NS_UCO_OBSERVABLE = rdflib.Namespace("https://unifiedcyberontology.org/ontology/uco/observable#")
NS_UCO_TYPES = rdflib.Namespace("https://unifiedcyberontology.org/ontology/uco/types#")
NS_UCO_VOCABULARY = rdflib.Namespace("https://unifiedcyberontology.org/ontology/uco/vocabulary#")
NS_XSD = rdflib.namespace.XSD


def get_file_info(filepath):
    """
    A function to get some basic information about the file application being run against
    :param filepath: The relative path to the image
    :return: A Dictinary with some information about the file
    """
    file_information = {}
    try:
        sha256 = hashlib.sha256(open(filepath, "rb").read())
        file_stats = os.stat(filepath)
        file_information['Filename'] = filepath
        file_information['size'] = file_stats.st_size
        file_information['SHA256'] = sha256.hexdigest()
    except IOError as io_e:
        print(io_e)
    except ValueError as v_e:
        print(v_e)
    return file_information


def print_to_errorlog(errors):
    """
    Write to a dedicated error log Currently writing to output but will be changed when reports and case being generated
    """
    print(errors)


def get_exif_with_pillow(filename):
    image = Image.open(filename)
    image.verify()
    return image._getexif()


def get_labeled_exif_from_pillow(raw_exif):
    labeled = {}
    for (key, val) in raw_exif.items():
        labeled[TAGS.get(key)] = val
    return labeled


def main():
    """
    Main function to run the application
    :return: prints out the case file - TODO: write to file instead
    """
    local_file = args.file
    file_info = get_file_info(local_file)
    tags = get_exif_with_pillow(local_file)
    tag_dict = get_labeled_exif_from_pillow(tags)
    out_graph = rdflib.Graph()
    out_graph.namespace_manager.bind("uco-core", NS_UCO_CORE)
    out_graph.namespace_manager.bind("uco-location", NS_UCO_LOCATION)
    out_graph.namespace_manager.bind("uco-observable", NS_UCO_OBSERVABLE)
    out_graph.namespace_manager.bind("uco-types", NS_UCO_TYPES)
    out_graph.namespace_manager.bind("uco-vocabulary", NS_UCO_VOCABULARY)
    exif_facet_node, raster_facets_node, file_facets_node, content_facets =\
        case_maker.n_cyber_object_to_node(out_graph)
    case_maker.controlled_dictionary_object_to_node(out_graph, tag_dict, exif_facet_node)
    case_maker.filefacets_object_to_node(out_graph, file_facets_node, file_info)
    case_maker.raster_object_to_node(out_graph, tag_dict, raster_facets_node, file_info)

    context = {"kb": "http://example.org/kb/",
               "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
               "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
               "uco-core": "https://unifiedcyberontology.org/ontology/uco/core#",
               "uco-location": "https://unifiedcyberontology.org/ontology/uco/location#",
               "uco-observable": "https://unifiedcyberontology.org/ontology/uco/observable#",
               "uco-types": "https://unifiedcyberontology.org/ontology/uco/types#",
               "xsd": "http://www.w3.org/2001/XMLSchema#"}

    graphed = out_graph.serialize(format='json-ld', context=context)

    graph = json.dumps(graphed, indent=4)
    case_json = json.loads(graph.encode('utf-8'))
    print(case_json)


if __name__ == "__main__":
    main()


