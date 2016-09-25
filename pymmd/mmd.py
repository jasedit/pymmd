#!/usr/bin/env python
"""Interface to the MultiMarkdown parser."""

import os.path
import platform
import ctypes
import ctypes.util

from .download import SHLIB_EXT
try:
    _LIB_FILE = 'libMultiMarkdown' + SHLIB_EXT[platform.system()]
    _LIB_LOCATION = os.path.abspath(os.path.join(os.path.dirname(__file__), 'files', _LIB_FILE))

    if not os.path.exists(_LIB_LOCATION):
        _LIB_LOCATION = ctypes.util.find_library('MultiMarkdown')

    _MMD_LIB = ctypes.cdll.LoadLibrary(_LIB_LOCATION)
except TypeError:
    _MMD_LIB = None

# Extension options
COMPATIBILITY = 0
COMPLETE = 1 << 1
SNIPPET = 1 << 2
HEAD_CLOSED = 1 << 3
SMART = 1 << 4
NOTES = 1 << 5
NO_LABELS = 1 << 6
FILTER_STYLES = 1 << 7
PROCESS_HTML = 1 << 8
NO_METADATA = 1 << 9
OBFUSCATE = 1 << 10
CRITIC = 1 << 11
CRITIC_ACCEPT = 1 << 12
CRITIC_REJECT = 1 << 13
RANDOM_FOOT = 1 << 14
HEADINGSECTION = 1 << 15
ESCAPED_LINE_BREAKS = 1 << 16
NO_STRONG = 1 << 17
NO_EMPH = 1 << 18

# Options for conversion formats for MMD
HTML = 1
TEXT = 2
LATEX = 3
MEMOIR = 4
BEAMER = 5
OPML = 6
ODF = 7
RTF = 8
CRITIC_ACCEPT = 9
CRITIC_REJECT = 10
CRITIC_HTML_HIGHLIGHT = 11
LYX = 12
TOC = 13

class GString(ctypes.Structure):
    """Class mirroring GString buffer interface struct in MultiMarkdown."""
    _fields_ = [("str", ctypes.c_char_p),
                ("currentStringBufferSize", ctypes.c_ulong),
                ("currentStringLength", ctypes.c_ulong)]

def valid_mmd():
    """Return flag indicating if the library was correctly loaded."""
    return bool(_MMD_LIB)

def _expand_source(source, dname, fmt):
    """Expands source text to include headers, footers, and expands Multimarkdown transclusion
    directives.

    Keyword arguments:
    source -- string containing the Multimarkdown text to expand
    dname -- directory name to use as the base directory for transclusion references
    fmt -- format flag indicating which format to use to convert transclusion statements
    """
    _MMD_LIB.g_string_new.restype = ctypes.POINTER(GString)
    _MMD_LIB.g_string_new.argtypes = [ctypes.c_char_p]
    src = source.encode('utf-8')
    gstr = _MMD_LIB.g_string_new(src)

    _MMD_LIB.prepend_mmd_header(gstr)
    _MMD_LIB.append_mmd_footer(gstr)

    manifest = _MMD_LIB.g_string_new(b"")
    _MMD_LIB.transclude_source.argtypes = [ctypes.POINTER(GString), ctypes.c_char_p,
                                           ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(GString)]
    _MMD_LIB.transclude_source(gstr, dname.encode('utf-8'), None, fmt, manifest)
    manifest_txt = manifest.contents.str
    full_txt = gstr.contents.str
    _MMD_LIB.g_string_free(manifest, True)
    _MMD_LIB.g_string_free(gstr, True)

    manifest_txt = [ii for ii in manifest_txt.decode('utf-8').split('\n') if ii]
    return full_txt.decode('utf-8'), manifest_txt

def has_metadata(source, ext):
    """Returns a flag indicating if a given block of MultiMarkdown text contains metadata."""
    _MMD_LIB.has_metadata.argtypes = [ctypes.c_char_p, ctypes.c_int]
    _MMD_LIB.has_metadata.restype = ctypes.c_bool
    return _MMD_LIB.has_metadata(source.encode('utf-8'), ext)

def has_metadata_from(fname, ext):
    with open(fname, 'r') as ifp:
        return has_metadata(ifp.read(), ext)

def convert(source, ext=COMPLETE, fmt=HTML, dname=None):
    """Converts a string of MultiMarkdown text to the requested format.
    Transclusion is performed if the COMPATIBILITY extension is not set, and dname is set to a
    valid directory

    Keyword arguments:
    source -- string containing MultiMarkdown text
    ext -- extension bitfield to pass to conversion process
    fmt -- flag indicating output format to use
    dname -- directory to use for transclusion - if None, transclusion functionality is bypassed
    """
    if dname and os.path.exists(dname) and not ext & COMPATIBILITY:
        source, _ = _expand_source(source, dname, fmt)
    _MMD_LIB.markdown_to_string.argtypes = [ctypes.c_char_p, ctypes.c_ulong, ctypes.c_int]
    _MMD_LIB.markdown_to_string.restype = ctypes.c_char_p
    src = source.encode('utf-8')
    return _MMD_LIB.markdown_to_string(src, ext, fmt).decode('utf-8')

def convert_from(fname, ext=COMPLETE, fmt=HTML, oname=None):
    """Converts a file containing MultiMarkdown text to the requested format.
    Transclusion is performed if the COMPATIBILITY extension is not set.

    Keyword arguments:
    fname -- string containing MultiMarkdown text
    ext -- extension bitfield to pass to conversion process
    fmt -- flag indicating output format to use
    oname -- optional filename to write MMD output to disk
    """
    source = open(fname, 'r').read()
    dname = os.path.dirname(fname) or '.'

    mmd = convert(source, ext, fmt, dname)

    if oname:
        with open(oname, 'w') as ofp:
            ofp.write(mmd)
    return mmd

def manifest(txt, dname):
    """Extracts file manifest for a body of text with the given directory."""
    _, files = _expand_source(txt, dname, HTML)
    return files

def manifest_from(fname):
    """Extracts the file manifest for a given document."""
    source = open(fname, 'r').read()
    dname = os.path.dirname(fname) or '.'
    return manifest(source, dname)

def extract_metadata_keys(source, ext=COMPLETE):
    """Extracts metadata keys from the provided MultiMarkdown text.

    Keyword arguments:
    source -- string containing MultiMarkdown text
    ext -- extension bitfield for extracting MultiMarkdown
    """
    _MMD_LIB.extract_metadata_keys.restype = ctypes.c_char_p
    _MMD_LIB.extract_metadata_keys.argtypes = [ctypes.c_char_p, ctypes.c_ulong]
    src = source.encode('utf-8')
    keys = _MMD_LIB.extract_metadata_keys(src, ext).decode('utf-8')
    keys = [ii for ii in keys.split('\n') if ii]
    return keys

def extract_metadata_keys_from(fname, ext=COMPLETE):
    """Extracts metadata keys from the provided file."""
    txt = open(fname, 'r').read()
    return extract_metadata_keys(txt, ext)

def extract_metadata_value(source, key, ext=COMPLETE):
    """ Extracts value for the specified metadata key from the given extension set.

    Keyword arguments:
    source -- string containing MultiMarkdown text
    ext -- extension bitfield for processing text
    key -- key to extract
    """
    _MMD_LIB.extract_metadata_value.restype = ctypes.c_char_p
    _MMD_LIB.extract_metadata_value.argtypes = [ctypes.c_char_p, ctypes.c_ulong, ctypes.c_char_p]

    src = source.encode('utf-8')
    dkey = key.encode('utf-8')

    return _MMD_LIB.extract_metadata_value(src, ext, dkey).decode('utf-8')

def extract_metadata_value_from(fname, key, ext=COMPLETE):
    with open(fname, 'r') as ifp:
        return extract_metadata_value(ifp.read(), key, ext)

def version():
    """Returns a string containing the MultiMarkdown library version in use."""
    _MMD_LIB.mmd_version.restype = ctypes.c_char_p
    return _MMD_LIB.mmd_version().decode('utf-8')
