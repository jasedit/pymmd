#!/usr/bin/env python
"""Interface to the MultiMarkdown parser."""

import os.path
import platform
import ctypes
import ctypes.util

from .download import SHLIB_EXT
from .defaults import DEFAULT_LIBRARY_DIR

_MMD_LIB = None
_LIB_LOCATION = None

class DString(ctypes.Structure):
    """Class mirroring DString buffer interface struct in MultiMarkdown."""
    _fields_ = [("str", ctypes.c_char_p),
                ("currentStringBufferSize", ctypes.c_ulong),
                ("currentStringLength", ctypes.c_ulong)]

def load_mmd():
    """Loads libMultiMarkdown for usage"""
    global _MMD_LIB
    global _LIB_LOCATION
    try:
        lib_file = 'libMultiMarkdown' + SHLIB_EXT[platform.system()]
        _LIB_LOCATION = os.path.abspath(os.path.join(DEFAULT_LIBRARY_DIR, lib_file))

        if not os.path.isfile(_LIB_LOCATION):
            _LIB_LOCATION = ctypes.util.find_library('MultiMarkdown')

        _MMD_LIB = ctypes.cdll.LoadLibrary(_LIB_LOCATION)
    except:
        _MMD_LIB = None

def define_interfaces():
    """Define arguments and return types for all used functions"""
    # d_string_new()
    _MMD_LIB.d_string_new.restype = ctypes.POINTER(DString)
    _MMD_LIB.d_string_new.argtypes = [ctypes.c_char_p]

    # transclude_source()
    _MMD_LIB.transclude_source.argtypes = [ctypes.POINTER(DString),
                        ctypes.c_char_p,
                        ctypes.c_char_p,
                        ctypes.c_short,
                        ctypes.POINTER(Stack),
                        ctypes.POINTER(Stack)]

    # mmd_string_has_metadata()
    _MMD_LIB.mmd_string_has_metadata.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_size_t)]
    _MMD_LIB.mmd_string_has_metadata.restype = ctypes.c_bool

    # mmd_convert_string()
    _MMD_LIB.mmd_convert_string.restype = ctypes.c_char_p
    _MMD_LIB.mmd_convert_string.argtypes = [ctypes.c_char_p, ctypes.c_ulong, ctypes.c_short, ctypes.c_short]

    # mmd_metadata_keys_string()
    _MMD_LIB.mmd_metadata_keys_string.restype = ctypes.c_char_p
    _MMD_LIB.mmd_metadata_keys_string.argtypes = [ctypes.c_char_p, ctypes.c_ulong, ctypes.c_short, ctypes.c_short]

    # metavalue_from_string()
    _MMD_LIB.metavalue_from_string.restype = ctypes.c_char_p
    _MMD_LIB.metavalue_from_string.argtypes = [ctypes.c_char_p, ctypes.c_char_p]

    # mmd_version()
    # _MMD_LIB.mmd_version.restype = ctypes.c_char_p

load_mmd()
define_interfaces()

# Extension options
COMPATIBILITY = 0
COMPLETE = 1 << 1
SNIPPET = 1 << 2
HEAD_CLOSED = 1 << 3
SMART = 1 << 4
NOTES = 1 << 5
NO_LABELS = 1 << 6
FILTER_STYLES = 1 << 7
FILTER_HTML = 1 << 8
PROCESS_HTML = 1 << 9
NO_METADATA = 1 << 10
OBFUSCATE = 1 << 11
CRITIC = 1 << 12
CRITIC_ACCEPT = 1 << 13
CRITIC_REJECT = 1 << 14
RANDOM_FOOT = 1 << 15
HEADINGSECTION = 1 << 16
ESCAPED_LINE_BREAKS = 1 << 17
NO_STRONG = 1 << 18
NO_EMPH = 1 << 19
TRANSCLUDE = 1 << 20

# Language options for MMD
ENGLISH = 0
DUTCH = 1
FRENCH = 2
GERMAN = 3
GERMANGUILL = 4
SWEDISH = 5

# Options for conversion formats for MMD
HTML = 0
EPUB = 1
LATEX = 2
BEAMER = 3
MEMOIR = 4
ODF = 5
MMD = 6

def _expand_source(source, dname, fmt):
    """Expands source text to include headers, footers, and expands Multimarkdown transclusion
    directives.

    Keyword arguments:
    source -- string containing the Multimarkdown text to expand
    dname -- directory name to use as the base directory for transclusion references
    fmt -- format flag indicating which format to use to convert transclusion statements
    """
    src = source.encode('utf-8')
    gstr = _MMD_LIB.d_string_new(src)

    manif = _MMD_LIB.d_string_new(b"")
    _MMD_LIB.transclude_source(gstr, dname.encode('utf-8'), None, fmt, manif)
    manifest_txt = manif.contents.str
    full_txt = gstr.contents.str
    _MMD_LIB.d_string_free(manif, True)
    _MMD_LIB.d_string_free(gstr, True)

    manifest_txt = [ii for ii in manifest_txt.decode('utf-8').split('\n') if ii]
    return full_txt.decode('utf-8'), manifest_txt

def has_metadata(source):
    """Returns a flag indicating if a given block of MultiMarkdown text contains metadata."""
    end = ctypes.c_size_t(0)
    return _MMD_LIB.mmd_string_has_metadata(source.encode('utf-8'), ctypes.byref(end))

def convert(source, ext=COMPLETE, fmt=HTML, language=ENGLISH, dname=None):
    """Converts a string of MultiMarkdown text to the requested format.
    Transclusion is performed if the COMPATIBILITY extension is not set, and dname is set to a
    valid directory

    Keyword arguments:
    source -- string containing MultiMarkdown text
    ext -- extension bitfield to pass to conversion process
    fmt -- flag indicating output format to use
    dname -- Path to use for transclusion - if None, transclusion functionality is bypassed
    """
    if dname and not ext & COMPATIBILITY:
        if os.path.isfile(dname):
            dname = os.path.abspath(os.path.dirname(dname))
        source, _ = _expand_source(source, dname, fmt)

    src = source.encode('utf-8')
    return _MMD_LIB.mmd_convert_string(src, ext, fmt, language).decode('utf-8') + '\n'

def convert_from(fname, ext=COMPLETE, fmt=HTML, language=ENGLISH):
    """
    Reads in a file and performs MultiMarkdown conversion, with transclusion ocurring based on the
    file directory. Returns the converted string.

    Keyword arguments:
    fname -- Filename of document to convert
    ext -- extension bitfield to pass to conversion process
    fmt -- flag indicating output format to use
    """
    dname = os.path.abspath(os.path.dirname(fname))
    with open(fname, 'r') as fp:
        src = fp.read()

    return convert(src, ext, fmt, language, dname)

def manifest(txt, dname):
    """Extracts file manifest for a body of text with the given directory."""
    _, files = _expand_source(txt, dname, HTML)
    return files

def keys(source, ext=COMPLETE, fmt=MMD, language=ENGLISH):
    """Extracts metadata keys from the provided MultiMarkdown text.

    Keyword arguments:
    source -- string containing MultiMarkdown text
    ext -- extension bitfield for extracting MultiMarkdown
    """
    src = source.encode('utf-8')
    all_keys = _MMD_LIB.mmd_metadata_keys_string(src, ext, fmt, language)
    all_keys = all_keys.decode('utf-8') if all_keys else ''
    key_list = [ii for ii in all_keys.split('\n') if ii]
    return key_list

def value(source, key, ext=COMPLETE):
    """Extracts value for the specified metadata key from the given extension set.

    Keyword arguments:
    source -- string containing MultiMarkdown text
    ext -- extension bitfield for processing text
    key -- key to extract
    """
    src = source.encode('utf-8')
    dkey = key.encode('utf-8')

    value = _MMD_LIB.metavalue_from_string(src, dkey)
    return value.decode('utf-8') if value else ''

def version():
    """Returns a string containing the MultiMarkdown library version in use."""
    return _MMD_LIB.mmd_version().decode('utf-8')

def valid_mmd():
    """Return flag indicating if the library was correctly loaded."""
    return bool(_MMD_LIB)
