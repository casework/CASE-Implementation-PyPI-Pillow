#!/usr/bin/env python3
# -*- coding: utf-8 -*

import os
import json
import PIL
import rdflib
import datetime
import logging
import hashlib
from fractions import Fraction
import argparse
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


def get_exif(filename):
    try:
        with Image.open(filename) as image:
            exif_data_PIL = image._getexif()
            exif_data = {}
            for k, v in PIL.ExifTags.TAGS.items():
                if k in exif_data_PIL:
                    value = exif_data_PIL[k]
                    exif_data[v] = {"tag": k,
                                    "raw": value,
                                    "processed": value}
            exif_data = _process_exif_dict(exif_data)

            return exif_data


    except IOError:
        raise


def _derationalize(rational):
    return rational.numerator / rational.denominator


def _create_lookups():
    lookups = {}
    lookups["metering_modes"] = ("Undefined",
                                 "Average",
                                 "Center-weighted average",
                                 "Spot",
                                 "Multi-spot",
                                 "Multi-segment",
                                 "Partial")

    lookups["exposure_programs"] = ("Undefined",
                                    "Manual",
                                    "Program AE",
                                    "Aperture-priority AE",
                                    "Shutter speed priority AE",
                                    "Creative (Slow speed)",
                                    "Action (High speed)",
                                    "Portrait ",
                                    "Landscape",
                                    "Bulb")

    lookups["resolution_units"] = ("",
                                   "Undefined",
                                   "Inches",
                                   "Centimetres")

    lookups["orientations"] = ("",
                               "Horizontal",
                               "Mirror horizontal",
                               "Rotate 180",
                               "Mirror vertical",
                               "Mirror horizontal and rotate 270 CW",
                               "Rotate 90 CW",
                               "Mirror horizontal and rotate 90 CW",
                               "Rotate 270 CW")

    return lookups


def _process_exif_dict(exif_dict):

    date_format = "%Y:%m:%d %H:%M:%S"

    lookups = _create_lookups()
    if "DateTime" in exif_dict:
        exif_dict["DateTime"]["processed"] = \
            datetime.datetime.strptime(exif_dict["DateTime"]["raw"], date_format)

    if "DateTimeOriginal" in exif_dict:
        exif_dict["DateTimeOriginal"]["processed"] = \
            datetime.datetime.strptime(exif_dict["DateTimeOriginal"]["raw"], date_format)

    if "DateTimeDigitized" in exif_dict:
        exif_dict["DateTimeDigitized"]["processed"] = \
            datetime.datetime.strptime(exif_dict["DateTimeDigitized"]["raw"], date_format)

    if "FNumber" in exif_dict:
        exif_dict["FNumber"]["processed"] = \
            _derationalize(exif_dict["FNumber"]["raw"])
        exif_dict["FNumber"]["processed"] = \
            "f{}".format(exif_dict["FNumber"]["processed"])

    if "MaxApertureValue" in exif_dict:
        exif_dict["MaxApertureValue"]["processed"] = \
            _derationalize(exif_dict["MaxApertureValue"]["raw"])
        exif_dict["MaxApertureValue"]["processed"] = \
            "f{:2.1f}".format(exif_dict["MaxApertureValue"]["processed"])

    if "FocalLength" in exif_dict:
        exif_dict["FocalLength"]["processed"] = \
            _derationalize(exif_dict["FocalLength"]["raw"])
        exif_dict["FocalLength"]["processed"] = \
            "{}mm".format(exif_dict["FocalLength"]["processed"])

    if "FocalLengthIn35mmFilm" in exif_dict:
        exif_dict["FocalLengthIn35mmFilm"]["processed"] = \
            "{}mm".format(exif_dict["FocalLengthIn35mmFilm"]["raw"])

    if "Orientation" in exif_dict:
        exif_dict["Orientation"]["processed"] = \
            lookups["orientations"][exif_dict["Orientation"]["raw"]]

    if "Orientation" in exif_dict:
        exif_dict["ResolutionUnit"]["processed"] = \
            lookups["resolution_units"][exif_dict["ResolutionUnit"]["raw"]]

    if "ExposureProgram" in exif_dict:
        exif_dict["ExposureProgram"]["processed"] = \
            lookups["exposure_programs"][exif_dict["ExposureProgram"]["raw"]]

    if "MeteringMode" in exif_dict:
        exif_dict["MeteringMode"]["processed"] = \
            lookups["metering_modes"][exif_dict["MeteringMode"]["raw"]]

    if "MeteringMode" in exif_dict:
        exif_dict["XResolution"]["processed"] = \
            int(_derationalize(exif_dict["XResolution"]["raw"]))

    exif_dict["YResolution"]["processed"] = \
        int(_derationalize(exif_dict["YResolution"]["raw"]))

    exif_dict["ExposureTime"]["processed"] = \
        _derationalize(exif_dict["ExposureTime"]["raw"])
    exif_dict["ExposureTime"]["processed"] = \
        str(Fraction(exif_dict["ExposureTime"]["processed"]).limit_denominator(8000))

    exif_dict["ExposureBiasValue"]["processed"] = \
        _derationalize(exif_dict["ExposureBiasValue"]["raw"])
    exif_dict["ExposureBiasValue"]["processed"] = \
        "{} EV".format(exif_dict["ExposureBiasValue"]["processed"])

    return exif_dict


f = get_exif(filename="799987.jpg")
for ff, yy in f.items():
    print(ff, yy)

# for r in p:
#     print(f"{r}")

