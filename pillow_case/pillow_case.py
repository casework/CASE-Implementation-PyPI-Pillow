#!/usr/bin/env python3
# -*- coding: utf-8 -*

"""Pillow to Case implementation"""

import os
import json
import logging
import hashlib
import argparse
import exif_node_maker as node_maker
from PIL import Image
from PIL.ExifTags import TAGS

parser = argparse.ArgumentParser()
parser.add_argument("file", help="file to extract exif from")
parser.add_argument("outfile", help="file to write case json to", default="case.json")
args = parser.parse_args()

__version__ = "0.1.0"

_logger = logging.getLogger(os.path.basename(__file__))
_logger.setLevel(level=logging.DEBUG)


def get_file_info(filepath):
    """
    A function to get some basic information about the file application being run against
    :param filepath: The relative path to the image
    :return: A Dictionary with some information about the file
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
    :return: prints out the case file
    """
    local_file = args.file

    file_info = get_file_info(local_file)
    tags = get_exif_with_pillow(local_file)
    tag_dict = get_labeled_exif_from_pillow(tags)
    _logger.warning(f"Number of exif tags found in image '{local_file}' = {len(tag_dict)}")

    node_graph = node_maker.init(tag_dict, file_info)

    context = {"kb": "http://example.org/kb/",
               "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
               "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
               "uco-core": "https://unifiedcyberontology.org/ontology/uco/core#",
               "uco-location": "https://unifiedcyberontology.org/ontology/uco/location#",
               "uco-observable": "https://unifiedcyberontology.org/ontology/uco/observable#",
               "uco-types": "https://unifiedcyberontology.org/ontology/uco/types#",
               "xsd": "http://www.w3.org/2001/XMLSchema#"}

    graphed = node_graph.serialize(format='json-ld', context=context)

    graph = json.dumps(graphed, indent=4)
    case_json = json.loads(graph.encode('utf-8'))
    with open(args.outfile, 'w') as file:
        file.write(case_json)


if __name__ == "__main__":
    main()
