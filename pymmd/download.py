#!python

import subprocess
import platform
import tempfile
import shutil
import os

try:
    from urllib.request import urlopen
except ImportError:
    from urllib import urlopen

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
  return subprocess.call(['make'])

def build_ms():
  return subprocess.call(['msbuild', 'ALL_BUILD.vcxproj', '/p:Configuration=Release'])

PLATFORM_BUILDS = {
  'Linux': build_posix,
  'Darwin': build_posix,
  'Windows': build_ms
}

def link_modules():
  subprocess.call(['git', 'submodule', 'init'])
  subprocess.call(['git', 'submodule', 'update'])
  subprocess.call(['git', 'submodule', 'foreach', 'git branch --set-upstream master origin/master'])
  subprocess.call(['git', 'submodule', 'foreach', 'git checkout master'])
  subprocess.call(['git', 'submodule', 'foreach', 'git pull origin'])

def build_mmd(target_folder):
    mmd_dir = tempfile.mkdtemp()
    subprocess.call(['git', 'clone', 'https://github.com/jasedit/MultiMarkdown-5', '-b', 'fix_windows', mmd_dir])
    build_dir = os.path.join(mmd_dir, 'build')
    old_pwd = os.getcwd()
    os.chdir(mmd_dir)
    link_modules()
    os.chdir(build_dir)

    subprocess.call(['cmake', '-DCMAKE_BUILD_TYPE=Release', '-DSHAREDBUILD=1', '..'])
    PLATFORM_BUILDS[platform.system()]()

    lib_file = 'libMultiMarkdown' + SHLIB_EXT[platform.system()]
    if not os.path.exists(target_folder):
      os.mkdir(target_folder)
    shutil.copyfile(os.path.join(build_dir, SHLIB_PREFIX[platform.system()], lib_file), os.path.join(target_folder, lib_file))
    os.chdir(old_pwd)
    try:
      shutil.rmtree(mmd_dir)
    except:
      pass
