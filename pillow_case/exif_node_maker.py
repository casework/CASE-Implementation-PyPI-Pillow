#!/usr/bin/env python3
# -*- coding: utf-8 -*

"""Pillow to Case rdflib node maker"""

import os
import rdflib
import logging

NS_RDF = rdflib.RDF
NS_RDFS = rdflib.RDFS
NS_UCO_CORE = rdflib.Namespace("https://unifiedcyberontology.org/ontology/uco/core#")
NS_UCO_LOCATION = rdflib.Namespace("https://unifiedcyberontology.org/ontology/uco/location#")
NS_UCO_OBSERVABLE = rdflib.Namespace("https://unifiedcyberontology.org/ontology/uco/observable#")
NS_UCO_TYPES = rdflib.Namespace("https://unifiedcyberontology.org/ontology/uco/types#")
NS_UCO_VOCABULARY = rdflib.Namespace("https://unifiedcyberontology.org/ontology/uco/vocabulary#")
NS_XSD = rdflib.namespace.XSD

_logger = logging.getLogger(os.path.basename(__file__))
_logger.setLevel(level=logging.INFO)


def n_cyber_object_to_node(graph):
    """
    Initial function to create the blank nodes for each of the file's facet nodes
    :param graph: rdflib graph object for adding nodes to
    :return: The four blank nodes for each fo the other functions to fill
    """
    cyber_object_facet = rdflib.BNode()
    n_raster_facets = rdflib.BNode()
    n_file_facets = rdflib.BNode()
    n_content_facets = rdflib.BNode()
    n_exif_facets = rdflib.BNode()
    graph.add((
        cyber_object_facet,
        NS_RDF.type,
        NS_UCO_OBSERVABLE.ObservableObject
    ))
    graph.add((
        cyber_object_facet,
        NS_UCO_CORE.hasFacet,
        n_exif_facets
    ))
    graph.add((
        cyber_object_facet,
        NS_UCO_CORE.hasFacet,
        n_raster_facets
    ))
    graph.add((
        cyber_object_facet,
        NS_UCO_CORE.hasFacet,
        n_file_facets
    ))
    return n_exif_facets, n_raster_facets, n_file_facets, n_content_facets


def filefacets_object_to_node(graph, n_file_facets, file_information):
    """
    Adding file facet object to the graph object
    :param graph: rdflib graph object for adding nodes to
    :param n_file_facets: file facet node to add facets of file to
    :param file_information: Dictionary containing information about file being analysed
    :return: None
    """
    file_name, ext = os.path.splitext(file_information['Filename'])
    file_ext = ext[1:]
    graph.add((
        n_file_facets,
        NS_RDF.type,
        NS_UCO_OBSERVABLE.FileFacet
    ))
    graph.add((
        n_file_facets,
        NS_UCO_OBSERVABLE.fileName,
        rdflib.Literal(os.path.basename(file_information["Filename"]))
    ))
    graph.add((
        n_file_facets,
        NS_UCO_OBSERVABLE.filePath,
        rdflib.Literal(os.path.abspath(file_information["Filename"]))
    ))
    graph.add((
        n_file_facets,
        NS_UCO_OBSERVABLE.extension,
        rdflib.Literal(file_ext)
    ))
    if 'size' in file_information.keys():
        graph.add((
            n_file_facets,
            NS_UCO_OBSERVABLE.sizeInBytes,
            rdflib.term.Literal(file_information["size"],
                                datatype=NS_XSD.integer)
        ))


def filecontent_object_to_node(graph, n_content_facets, file_information):
    """
    Unused: Create a node that will add the file content facet node to the graph
    :param graph: rdflib graph object for adding nodes to
    :param n_content_facets: Blank node to contain all of the content facet information
    :param file_information: Dictionary containing information about file being analysed
    :return: None
    """
    byte_order_facet = rdflib.BNode()
    file_hash_facet = rdflib.BNode()
    graph.add((
        n_content_facets,
        NS_RDF.type,
        NS_UCO_OBSERVABLE.ContentDataFacet
    ))
    graph.add((
        n_content_facets,
        NS_UCO_OBSERVABLE.byteOrder,
        byte_order_facet
    ))
    graph.add((
        byte_order_facet,
        NS_RDF.type,
        NS_UCO_VOCABULARY.EndiannessTypeVocab,
    ))
    graph.add((
        byte_order_facet,
        NS_UCO_VOCABULARY.value,
        rdflib.Literal("Big-endian")
    ))
    if 'mimetype' in file_information.keys():
        graph.add((
            n_content_facets,
            NS_UCO_OBSERVABLE.mimeType,
            rdflib.Literal(file_information["mimetype"])
        ))
    if 'size' in file_information.keys():
        graph.add((
            n_content_facets,
            NS_UCO_OBSERVABLE.sizeInBytes,
            rdflib.term.Literal(file_information["size"],
                                datatype=NS_XSD.integer)
        ))
    graph.add((
        n_content_facets,
        NS_UCO_OBSERVABLE.hash,
        file_hash_facet
    ))
    graph.add((
        file_hash_facet,
        NS_RDF.type,
        NS_UCO_TYPES.Hash
    ))


def raster_object_to_node(graph, controlled_dict, n_raster_facets, file_information):
    """
    Adding file's raster facet objects to the graph object
    :param graph: rdflib graph object for adding nodes to
    :param controlled_dict: Dictionary containing the EXIF information from image
    :param n_raster_facets: raster facet node to add raster facets of file to
    :param file_information: Dictionary containing information about file being analysed
    :return: None
    """
    file_name, ext = os.path.splitext(file_information['Filename'])
    file_ext = ext[1:]
    graph.add((
        n_raster_facets,
        NS_RDF.type,
        NS_UCO_OBSERVABLE.RasterPictureFacet
    ))
    graph.add((
        n_raster_facets,
        NS_UCO_OBSERVABLE.pictureType,
        rdflib.Literal(file_ext)
    ))
    if 'EXIF ExifImageLength' in controlled_dict.keys():
        graph.add((
            n_raster_facets,
            NS_UCO_OBSERVABLE.pictureHeight,
            rdflib.term.Literal(str(controlled_dict['EXIF ExifImageLength']),
                                datatype=NS_XSD.integer)
        ))
    elif 'ExifImageHeight' in controlled_dict.keys():
        graph.add((
            n_raster_facets,
            NS_UCO_OBSERVABLE.pictureHeight,
            rdflib.term.Literal(str(controlled_dict['ExifImageHeight']),
                                datatype=NS_XSD.integer)
        ))
    if 'EXIF ExifImageWidth' in controlled_dict.keys():
        graph.add((
            n_raster_facets,
            NS_UCO_OBSERVABLE.pictureWidth,
            rdflib.term.Literal(str(controlled_dict['EXIF ExifImageWidth']),
                                datatype=NS_XSD.integer)
        ))
    elif 'ExifImageWidth' in controlled_dict.keys():
        graph.add((
            n_raster_facets,
            NS_UCO_OBSERVABLE.pictureWidth,
            rdflib.term.Literal(str(controlled_dict['ExifImageWidth']),
                                datatype=NS_XSD.integer)
        ))
    if 'EXIF CompressedBitsPerPixel' in controlled_dict.keys():
        graph.add((
            n_raster_facets,
            NS_UCO_OBSERVABLE.bitsPerPixel,
            rdflib.term.Literal(str(controlled_dict['EXIF CompressedBitsPerPixel']),
                                datatype=NS_XSD.integer)
        ))
    elif 'CompressedBitsPerPixel' in controlled_dict.keys():
        graph.add((
            n_raster_facets,
            NS_UCO_OBSERVABLE.bitsPerPixel,
            rdflib.term.Literal(str(controlled_dict['CompressedBitsPerPixel']),
                                datatype=NS_XSD.integer)
        ))
    graph.add((
        n_raster_facets,
        NS_RDFS.comment,
        rdflib.Literal("Information represented here from exif information not from "
                       "file system stats except for extension, which uses os python lib")
    ))


def controlled_dictionary_object_to_node(graph, controlled_dict, n_exif_facet):
    """
    Add controlled dictionary object to accept all of the Values in the extracted exif
    :param graph: rdflib graph object for adding nodes to
    :param controlled_dict: Dictionary containing the EXIF information from image
    :param n_exif_facet:
    :return: None
    """
    n_controlled_dictionary = rdflib.BNode()
    graph.add((
        n_exif_facet,
        NS_RDF.type,
        NS_UCO_OBSERVABLE.EXIFFacet
    ))
    graph.add((
        n_exif_facet,
        NS_UCO_OBSERVABLE.exifData,
        n_controlled_dictionary
    ))
    for key in sorted(controlled_dict.keys()):
        v_value = controlled_dict[key]
        v_value = rdflib.Literal(v_value)
        try:
            assert isinstance(v_value, rdflib.Literal)
        except AssertionError:
            _logger.info("v_value = %r." % v_value)
            raise
        n_entry = rdflib.BNode()
        graph.add((
            n_controlled_dictionary,
            NS_UCO_TYPES.entry,
            n_entry
        ))
        graph.add((
            n_entry,
            NS_RDF.type,
            NS_UCO_TYPES.ControlledDictionaryEntry
        ))
        graph.add((
            n_entry,
            NS_UCO_TYPES.key,
            rdflib.Literal(key)
        ))
        graph.add((
            n_entry,
            NS_UCO_TYPES.value,
            v_value
        ))


def init(tag_dict, file_info):

    out_graph = rdflib.Graph()
    out_graph.namespace_manager.bind("uco-core", NS_UCO_CORE)
    out_graph.namespace_manager.bind("uco-location", NS_UCO_LOCATION)
    out_graph.namespace_manager.bind("uco-observable", NS_UCO_OBSERVABLE)
    out_graph.namespace_manager.bind("uco-types", NS_UCO_TYPES)
    out_graph.namespace_manager.bind("uco-vocabulary", NS_UCO_VOCABULARY)

    exif_facet_node, raster_facets_node, file_facets_node, content_facets = \
        n_cyber_object_to_node(out_graph)
    controlled_dictionary_object_to_node(out_graph, tag_dict, exif_facet_node)
    filefacets_object_to_node(out_graph, file_facets_node, file_info)
    raster_object_to_node(out_graph, tag_dict, raster_facets_node, file_info)
    return out_graph
