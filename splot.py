#
# Look at VSOP spectra
#

# Import core Python modules
import optparse, os.path, os, re

# Import PyRAF and IRAF, the IRAF packages
import pyraf, iraf
from pyraf.iraf import onedspec

VERSION = '0.9'

matchfits = re.compile(r".*0_s1d\.fits$")

def getTargets (targets, targetList):

    if targetList != None:
        f = open (targetList, mode='r')
        for target in f:
            targets.append(target.strip('\n'))
        f.close()

    validTargets = []
    invalidTargets = []
    for target in targets:
        if os.path.isdir (target):
            validTargets.append(target)
        else:
            invalidTargets.append(target)

    return validTargets, invalidTargets

def getSpectra (targets):

    specdict = {}
    for target in targets:
        files = os.listdir(target+'/wiki/')
        sp =[]
        for f in files:
            if matchfits.match(f): sp.append(target+'/wiki/'+f)
        specdict[target] = sp

    return specdict


def main():

    # Parse input arguments
    usage = 'usage: %prog [options] targets'
    p = optparse.OptionParser(usage=usage, version='v'+VERSION)
    p.add_option('--debug', action='store_true', help='toggle debug messages')
    p.add_option('--verbose', '-v', action='store_true', help='toggle on verbose mode')
    p.add_option('--tlist', '-l', action='store', type='string', dest='tlist', help='Target list')
    
    (options, args) = p.parse_args()
    
    if options.debug:
        options.verbose = True
        print 'options: ', options
        print 'args: ', args
    
    (validTargets, invalidTarget) = getTargets(args, options.tlist)
    specdict = getSpectra(validTargets)
    
    onedspec()
    for target in validTargets:
        print target
        for spectrum in specdict[target]:
            onedspec.splot(spectrum)

if __name__ == '__main__':
    main()
    
