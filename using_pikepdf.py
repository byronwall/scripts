#!/usr/bin/env python3

import logging
import os.path
import sys

import pikepdf


UNDESIRED_NAMES = [
    # From the infodict
    '/AcroForm',
    '/Author',
    '/Creator',
    '/Keywords',
    '/OpenAction',
    '/Producer',
    '/Subject',
    '/ViewerPreferences',
    '/Lang',
    '/Info',
    '/PageLayout',
    '/PageMode',
    '/Version',

    # '/OCProperties',  # FIXME: Optional Content (sometimes, hidden, sometimes not)

    # Date stuff
    '/CreationDate',
    '/LastModified',
    '/ModDate',

    # pdftex stuff
    '/PTEX.Fullbanner',
    '/PTEX.FileName',
    '/PTEX.InfoDict',
    '/PTEX.PageNumber',

    # Generic
    '/Metadata',

    # From images
    '/PieceInfo',
    '/ImageName',

    # From pages
    '/Thumb',

    # From other software
    '/ITXT',
    '/Lambkin',

    # Embedded files
    '/EmbeddedFiles',

    # From annotations.
    '/NM',  # FIXME: Test; maybe should not be removed
    # '/RC',  # FIXME: idem

    # FIXME: remove /SWF files (and other names) from a /Navigator entry
    # (adobe extensions level 3).
    '/RichMediaExecute',
    '/ProcSet',  # "Acrobat 5.0 and later ignores procedure sets." (page 126)
]


def delete_javascript(obj, num):
    if ('/JS' in obj) and ('/S' in obj):
        del obj['/JS']
        del obj['/S']
        logging.info('    **** Removed Javascript from obj %d.', num)


def delete_annotations_moddate(obj, num):
    if ('/Type' in obj) and (obj.Type == '/Annot') and '/M' in obj:
        del obj['/M']
        logging.info('    **** Removed /M from obj %d.', num)


def delete_annotations_rc(obj, num):
    if ('/Subtype' in obj) and (obj.Subtype == '/FreeText') and '/RC' in obj:
        del obj['/RC']
        logging.info('    **** Removed /RC from obj %d.', num)


def delete_annotations_t(obj, num):
    if ('/Subtype' in obj) and (obj.Subtype == '/FreeText') and '/T' in obj:
        del obj['/T']
        logging.info('    **** Removed /T from obj %d.', num)


def delete_annotations_c(obj, num):
    if ('/Subtype' in obj) and (obj.Subtype == '/FreeText') and '/C' in obj:
        del obj['/C']
        logging.info('    **** Removed /C from obj %d.', num)


def delete_name(obj, name, num=None):
    if name in obj:
        del obj[name]
        logging.info('    **** Removed name: %s from obj %d.', name, num)


def delete_metadata(filename):
    logging.info('Processing %s', filename)

    original_size = os.path.getsize(filename)
    my_pdf = pikepdf.open(filename)

    num_of_objects = my_pdf.trailer['/Size']  # this includes the object 0

    # FIXME: somehow, using enumerate seems slower, when profiling with a
    # large file:
    #
    # perf stat --repeat=10 using_pikepdf.py \
    # katz-lindell-introduction-to-modern-cryptography.pso.pdfa.unc.pso.pso.pdf

    # Traverse all the objects
    # for i, cur_obj in enumerate(my_pdf.objects):
    for i in range(1, num_of_objects):

        cur_obj = my_pdf.get_object(i, 0)

        # Stuff that doesn't contain keys
        if isinstance(cur_obj, (pikepdf.String, pikepdf.Array, pikepdf.Name)):
            continue
        if not isinstance(cur_obj, (pikepdf.objects.Object, pikepdf.Stream)):
            continue

        for name in UNDESIRED_NAMES:
            delete_name(cur_obj, name, i)

        delete_javascript(cur_obj, i)
        delete_annotations_moddate(cur_obj, i)

        # Not working right now
        # delete_annotations_rc(cur_obj, i)
        # delete_annotations_t(cur_obj, i)
        delete_annotations_c(cur_obj, i)

    # Remove from the document root
    for name in UNDESIRED_NAMES:
        delete_name(my_pdf.root, name)

    # FIXME: The following may be useless with the deletions above
    # Remove the only /Title that we want
    delete_name(my_pdf.docinfo, '/Title', -1)
    delete_name(my_pdf.docinfo, '/OpenAction', -1)

    # Remove any other stuff from the docinfo dictionary
    for key in my_pdf.docinfo.keys():
        delete_name(my_pdf.docinfo, key, -1)

    # FIXME: This doesn't seem to work
    delete_name(my_pdf.root, '/Info')
    # FIXME: This does
    delete_name(my_pdf.trailer, '/Info', -2)

    # FIXME: Perhaps use pdfsizeopt instead?
    my_pdf.remove_unreferenced_resources()

    final_filename = os.path.splitext(filename)[0] + '.clean.pdf'
    my_pdf.save(final_filename, fix_metadata_version=False)

    final_size = os.path.getsize(final_filename)
    total_savings = original_size - final_size

    logging.info('Saved %d bytes to create %s', total_savings, final_filename)


if __name__ == '__main__':
    for filename in sys.argv[1:]:
        delete_metadata(filename)
