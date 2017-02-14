#!python
"""Provides tool to download, build, and install the MultiMarkdown shared library"""

import subprocess
import platform
import tempfile
import shutil
import os

from .defaults import DEFAULT_LIBRARY_DIR

SHLIB_PREFIX = {
    'Linux': '.',
    'Darwin': '.',
    'Windows': 'Release'
}

SHLIB_EXT = {
    'Linux': '.so',
    'Darwin': '.dylib',
    'Windows': '.dll'
}

def build_posix():
    """Invoke build command on POSIX style systems."""
    return subprocess.call(['make', 'libMultiMarkdownShared'])

def build_ms():
    """Invoke build command on Windows."""
    return subprocess.call(['msbuild', 'libMultiMarkdownShared.vcxproj',
                            '/p:Configuration=Release'])

PLATFORM_BUILDS = {
    'Linux': build_posix,
    'Darwin': build_posix,
    'Windows': build_ms
}

def link_modules():
    """Link git submodules in MultiMarkdown for building."""
    subprocess.call(['git', 'submodule', 'init'])
    subprocess.call(['git', 'submodule', 'update'])
    subprocess.call(['git', 'submodule', 'foreach',
                     'git branch --set-upstream master origin/master'])
    subprocess.call(['git', 'submodule', 'foreach', 'git checkout master'])
    subprocess.call(['git', 'submodule', 'foreach', 'git pull origin'])

def build_mmd(target_folder=DEFAULT_LIBRARY_DIR):
    """Build and install the MultiMarkdown shared library."""
    mmd_dir = tempfile.mkdtemp()
    subprocess.call(['git', 'clone', 'https://github.com/jasedit/MultiMarkdown-5',
                     '-b', 'fix_windows', mmd_dir])
    build_dir = os.path.join(mmd_dir, 'build')
    old_pwd = os.getcwd()
    os.chdir(mmd_dir)
    link_modules()
    os.chdir(build_dir)

    cmake_cmd = ['cmake', '-DCMAKE_BUILD_TYPE=Release', '-DSHAREDBUILD=1', '..']
    if platform.system() == 'Windows':
        is_64bit = platform.architecture()[0] == '64bit'
        generator = 'Visual Studio 14 2015{0}'.format(' Win64' if is_64bit else '')
        cmake_cmd.insert(-1, '-G')
        cmake_cmd.insert(-1, '{0}'.format(generator))
    subprocess.call(cmake_cmd)
    PLATFORM_BUILDS[platform.system()]()

    lib_file = 'libMultiMarkdown' + SHLIB_EXT[platform.system()]
    if not os.path.exists(target_folder):
        os.mkdir(target_folder)
    src = os.path.join(build_dir, SHLIB_PREFIX[platform.system()], lib_file)
    dest = os.path.join(target_folder, lib_file)
    shutil.copyfile(src, dest)
    os.chdir(old_pwd)
    shutil.rmtree(mmd_dir, ignore_errors=True)
