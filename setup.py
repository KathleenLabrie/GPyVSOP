#!/usr/bin/env python

"""
Setup script for GPyVSOP

GPyVSOP is the Gemini VSOP data reduction package.

Usage:
  python setup.py install --prefix=<somewhere>
  python setup.py sdist  (to make the tar file)
"""

from distutils.core import setup
import sys
import os, os.path
import optparse

def parse_args(setup_args):
    p = optparse.OptionParser()
    p.add_option('--prefix', action='store')
    
    return p.parse_args()

# PACKAGES
PACKAGES = ['GPyVSOP']
PACKAGE_DIRS={'GPyVSOP' : '.'}

# PACKAGE_DATA
GPYVSOP_DATA_FILES = {'GPyVSOP': ['Changes']}
PACKAGE_DATA = GPYVSOP_DATA_FILES

# DATA_DIR and DATA_FILES
#GPYVSOP_DATA_FILES = [('', ['Changes'])]
#DATA_FILES = GPYVSOP_DATA_FILES

# SCRIPTS
#GPYVSOP_SCRIPTS = [ 'gmosLS',
#                    'publish',
#                    'setvsop',
#                    'splot' ]
#SCRIPTS = GPYVSOP_SCRIPTS
SCRIPTS = None

# SYMLINK
GPYVSOP_BIN_LINKS = [   'gmosLS',
                        'publish',
                        'setvsop',
                        'splot' ]
# links created after setup()

# EXTENSIONS
EXTENSIONS = None

setup ( name='GPyVSOP',
        version='1.0.4',
        description='Gemini VSOP Data Reduction Package',
        author='Kathleen Labrie',
        author_email='klabrie@gemini.edu',
        url='http://www.gemini.edu',
        maintainer='Kathleen Labrie',
        maintainer_email='klabrie@gemini.edu',
        packages=PACKAGES,
        package_dir=PACKAGE_DIRS,
        package_data=PACKAGE_DATA,
        #data_files=DATA_FILES,
        scripts=SCRIPTS,
        ext_modules=EXTENSIONS,
        provides=['GPyVSOP'],
        classifiers=[
            'Development Status :: QA',
            'Intended Audience :: VSOP',
            'Operating System :: Linux :: Fedora',
            'Programming Language :: Python',
            'Programming Language :: IRAF',
            'Topic :: VSOP',
            'Topic :: GMOS',
            'Topic :: Data Reduction',
            'Topic :: Longslit',
        ],
     )

# Create links to executable scripts
#  Note: eventually what I need to do is the re-write the scripts
#  such that I don't need the links anymore.

(options, args) = parse_args(sys.argv[1:])
if args[0] == 'install':
    if options.prefix != None:
        prefix = options.prefix
    else:
        prefix = sys.prefix
        
    bindir = os.path.join(prefix, 'bin')
    version_info = sys.version_info
    version = str(version_info[0])+'.'+str(version_info[1])
    ppath = os.path.join('lib','python'+version, 'site-packages')
    gpyvsoppath = os.path.join(prefix, ppath, 'GPyVSOP')

    os.chdir(bindir)
    for bin in GPYVSOP_BIN_LINKS:
        os.remove(bin)
        os.symlink(os.path.join(gpyvsoppath, bin+'.py'), bin)
        os.chmod(os.path.join(gpyvsoppath, bin+'.py'), 0755)

