#!/usr/bin/env python

import os.path

import ctypes
import ctypes.util

MMDLibraryLocation = ctypes.util.find_library('MultiMarkdown')

MMDLibrary = ctypes.cdll.LoadLibrary(MMDLibraryLocation)

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
  _fields_ = [("str", ctypes.c_char_p),
              ("currentStringBufferSize", ctypes.c_ulong),
              ("currentStringLength", ctypes.c_ulong)]

def _expand_source(source, dname, fmt):
  """Expands source text to include headers, footers, and expands Multimarkdown transclusion directives.

  Keyword arguments:
  source -- string containing the Multimarkdown text to expand
  dname -- directory name to use as the base directory for transclusion references
  fmt -- format flag indicating which format to use to convert transclusion statements
  """
  MMDLibrary.g_string_new.restype = ctypes.POINTER(GString)
  MMDLibrary.g_string_new.argtypes = [ctypes.c_char_p]
  src = source.encode('utf-8')
  gstr = MMDLibrary.g_string_new(src)

  MMDLibrary.prepend_mmd_header(gstr)
  MMDLibrary.append_mmd_footer(gstr)

  manifest = MMDLibrary.g_string_new(b"")
  MMDLibrary.transclude_source.argtypes = [ctypes.POINTER(GString), ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(GString)]
  MMDLibrary.transclude_source(gstr, dname.encode('utf-8'), None, fmt, manifest)
  MMDLibrary.g_string_free(manifest, True)
  full_txt = gstr.contents.str
  MMDLibrary.g_string_free(gstr, True)

  return full_txt.decode('ascii')

def has_metadata(source, ext):
  """Returns a flag indicating if a given block of MultiMarkdown text contains metadata."""
  fn = MMDLibrary.has_metadata
  fn.restype = ctypes.c_bool
  return fn(source, ext)

def convert(source, ext=COMPLETE, fmt=HTML, dname=None):
  """Converts a string of MultiMarkdown text to the requested format.
  Transclusion is performed if the COMPATIBILITY extension is not set, and dname is set to a valid directory

  Keyword arguments:
  source -- string containing MultiMarkdown text
  ext -- extension bitfield to pass to conversion process
  fmt -- flag indicating output format to use
  dname -- directory to use for transclusion - if None, transclusion functionality is bypassed
  """
  if dname and os.path.exists(dname) and not (ext & COMPATIBILITY):
    source = _expand_source(source, dname, fmt)
  MMDLibrary.markdown_to_string.argtypes = [ctypes.c_char_p, ctypes.c_ulong, ctypes.c_int]
  MMDLibrary.markdown_to_string.restype = ctypes.c_char_p
  src = source.encode('utf-8')
  return MMDLibrary.markdown_to_string(src, ext, fmt).decode('ascii')

def convert_from(fname, ext=COMPLETE, fmt=HTML):
  """Converts a file containing MultiMarkdown text to the requested format.
  Transclusion is performed if the COMPATIBILITY extension is not set.

  Keyword arguments:
  fname -- string containing MultiMarkdown text
  ext -- extension bitfield to pass to conversion process
  fmt -- flag indicating output format to use
  """
  source = open(fname, 'r').read()
  dname = os.path.dirname(fname)

  return convert(source, ext, fmt, dname)

def extract_metadata_keys(source, ext=COMPLETE):
  """Extracts metadata keys from the provided MultiMarkdown text.

  Keyword arguments:
  source -- string containing MultiMarkdown text
  ext -- extension bitfield for extracting MultiMarkdown
  """
  MMDLibrary.extract_metadata_keys.restype = ctypes.c_char_p
  MMDLibrary.extract_metadata_keys.argtypes = [ctypes.c_char_p, ctypes.c_ulong]
  src = source.encode('utf-8')
  return MMDLibrary.extract_metadata_keys(src, ext).decode('ascii')

def extract_metadata_value(source, ext, key):
  """ Extracts value for the specified metadata key from the given extension set.

  Keyword arguments:
  source -- string containing MultiMarkdown text
  ext -- extension bitfield for processing text
  key -- key to extract
  """
  MMDLibrary.extract_metadata_value.restype = ctypes.c_char_p
  MMDLibrary.extract_metadata_value.argtypes = [ctypes.c_char_p, ctypes.c_ulong, ctypes.c_char_p]

  src = source.decode('utf-8')
  dkey = key.decode('utf-8')

  return MMDLibrary.extract_metadata_value(src, ext, dkey).decode('ascii')

def version():
  """Returns a string containing the MultiMarkdown library version in use."""
  MMDLibrary.mmd_version.restype = ctypes.c_char_p
  return MMDLibrary.mmd_version()