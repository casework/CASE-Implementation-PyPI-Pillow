#!/usr/bin/env python3
# -*- coding: utf-8 -*

import PIL
import hashlib
import string
import argparse
from PIL import Image
from PIL.ExifTags import TAGS

parser = argparse.ArgumentParser()
parser.add_argument("file", help="file to extract exif from")
args = parser.parse_args()


def file_information(filepath):
    try:
        image = Image.open(filepath)
        md5sum = hashlib.md5(open(filepath, "rb").read())
        print(f'File_name:          {image.filename}')
        print(f'Size:               {image.size}')
        print(f'Width:              {image.width}')
        print(f'Height:             {image.height}')
        print(f'Format:             {image.format}')
        print(f'Format_description: {image.format_description}')
        print(f'Mode:               {image.mode}')
        print(f'MD5sum:             {md5sum.hexdigest()} \n')
    except IOError as io_e:
        print(io_e)
    except ValueError as v_e:
        print(v_e)


def get_exif(filename):
    image = Image.open(filename)
    image.verify()
    return image._getexif()


def get_labeled_exif(raw_exif):
    labeled = {}
    for (key, val) in raw_exif.items():
        labeled[TAGS.get(key)] = val
    return labeled


def print_to_errorlog(errors):
    """
    Write to a dedicated error log Currently writing to output but will be changed when reports and case being generated
    """
    print(errors)


def get_values(exif):
    makernote_string = "Makernote: "
    for values in exif:
        try:
            if values:
                if isinstance(exif[values], bytes):
                    try:
                        exif[values] = exif[values].decode()
                    except UnicodeDecodeError as e:
                        print_to_errorlog(f'{values} : {e}')
                        for byte in exif[values]:
                            try:
                                makernote_string += (chr(byte))
                                # not in use currently (for future expansion) Makernote is proprietary and
                                # mostly undocumented, outside of Manufacturer. some information can be gathered from
                                # the parsing of this information but may not be feasible due to it being vendor
                                # specific
                            except:
                                print_to_errorlog(f'{exif} : not a binary object')
                print(f'{values} : {exif[values]}')
        except AttributeError as a_e:
            print(a_e)


# def get_simple(exifdata):
"""
More future expansion for using PIL.TAGS functions in a more meaningful way.
"""
#     for tag_id in exifdata:
#         tag = TAGS.get(tag_id, tag_id)
#         data = exifdata.get(tag_id)
#         if isinstance(data, bytes):
#             data = data.decode()
#         print(f'{tag:25}: {data}')


def main():
    filepath = args.file
    print(f'Pillow version {PIL.__version__}\n')
    file_information(filepath)
    raw_exif = get_exif(filepath)
    exif = get_labeled_exif(raw_exif)
    get_values(exif)
    # print(labeled)


if __name__ == "__main__":
    main()

