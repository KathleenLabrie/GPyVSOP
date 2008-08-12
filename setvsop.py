#!/usr/bin/env python

# Import core Python modules
import optparse, os, os.path

# Import GPyVSOP modules
import GPyVSOP

VERSION = GPyVSOP.__version__

def main():

    # Parse input arguments
    usage = 'usage: %prog [options] targetname bias flat arc sci1..sciN'
    p = optparse.OptionParser(usage=usage, version='v'+VERSION)
    p.add_option('--obsnb', '-o', action='store', dest='obsnb', default='',
        help='Observation number')
    p.add_option('--nsrc', '-n', action='store', type='int', dest='nsrc',
        default=1, help='Number of sources to extract')
    p.add_option('--scripts-only', action='store_true',
        help='Overwrite the scripts, do not try to move data')
    p.add_option('--overwrite', action='store_true', help='Allow overwrite')
    p.add_option('--debug', action='store_true', help='Debug mode')
    p.add_option('--verbose', '-v', action='store_true', help='Verbose')
    
    (options, args) = p.parse_args()
    
    if options.debug:
        options.verbose = True
        print 'options: ', options
        print 'args: ', args
    
    targetname=args[0]
    bias=args[1]+'.fits'
    flat=args[2]+'.fits'
    arc=args[3]+'.fits'
    sciframes=map((lambda x: x+'.fits'), args[4:])
    
    if options.scripts_only:
        options.overwrite = True

    
    # Check if scripts exist already
    targetpath = os.path.join('.','Targets',targetname)
    try:
        errmsg = ''
        if os.path.exists(os.path.join(targetpath,'run'+options.obsnb)):
            errmsg = errmsg+'run'+options.obsnb+' exists.  '
        if os.path.exists(os.path.join(targetpath,'pub'+options.obsnb)):
            errmsg = errmsg+'pub'+options.obsnb+' exists.'
        if errmsg != '':
            raise IOError, errmsg
    except:
        if not options.overwrite:
            raise
        else:
            print 'Overwriting as requested.'
            
    
    # Set up directories and copy files over
    if not options.scripts_only:
        rootdir = os.getcwd()
        
        # Create directories
        reduxdir = os.path.join(targetpath, 'redux')
        wikidir = os.path.join(targetpath, 'wiki')
        if options.debug:
            print 'reduxdir: ',reduxdir
            print 'wikidir: ',wikidir
        os.system(' '.join(['mkdir -p',reduxdir]))
        os.system(' '.join(['mkdir -p',wikidir]))
        
        # Change to target's directory
        os.chdir(targetpath)
        
        # Set up links for biases
        biaspath = os.path.join('..','..','Calib','Biases',bias)
        os.system(' '.join(['ln -s',biaspath,'.']))
        
        # Move and uncompress flat
        flatpath = os.path.join('..','..','downloads',flat+'.gz')
        os.system(' '.join(['mv',flatpath, '.']))
        os.system(' '.join(['gunzip',flat+'.gz']))
        
        # Move and uncompress arc
        arcpath = os.path.join('..','..','downloads',arc+'.gz')
        os.system(' '.join(['mv',arcpath, '.']))
        os.system(' '.join(['gunzip',arc+'.gz']))
        
        # Move and uncompress science frames
        for sci in sciframes:
            scipath = os.path.join('..','..','downloads',sci+'.gz')
            os.system(' '.join(['mv',scipath, '.']))
            os.system(' '.join(['gunzip',sci+'.gz']))           

        # Return to original directory
        os.chdir(rootdir)
            
    # Create the scripts
    frun = open(os.path.join(targetpath,'run'+options.obsnb), mode='w')
    frun.write('#!/bin/sh\n')
    frun.write('\n')
    frun.write('sci=\''+' '.join(sciframes)+'\'\n')
    frun.write('flat=\''+flat+'\'\n')
    frun.write('arc=\''+arc+'\'\n')
    frun.write('bias=\''+bias+'\'\n')
    frun.write('logfile=\''+targetname+'.log\'\n')
    frun.write('\n')
    towrite = 'gmosLS ${sci} --flat=${flat} --arc=${arc} --bias=${bias} --rawdir=.. --wikidir=../wiki --logfile=${logfile} --keep2d'
    if options.nsrc > 1:
        towrite = '%s --nsrc=%d' % (towrite,options.nsrc)
    frun.write(towrite+'\n')
    frun.close()
    os.chmod(os.path.join(targetpath,'run'+options.obsnb), 0755)
    
    fpub = open(os.path.join(targetpath,'pub'+options.obsnb), mode='w')
    fpub.write('#!/bin/sh\n')
    fpub.write('\n')
    i = 0
    specidList=[]       # [ [(mef11,gem1s1),(mef12,gem2s2)], [...] ]
    for sci in sciframes:
        mefspec = 'mefspec%d' % (i+1)
        srcidList=[]
        if options.nsrc != 1:
            for j in range(options.nsrc):
                gem = 'es%dtgs%s' % ((j+1),sci)
                mef = '%s%d' % (mefspec, (j+1))
                srcidList.append((mef, gem))
        else:
            srcidList.append((mefspec, 'estgs'+sci))
        specidList.append(srcidList)
        i += 1
    
    for obs in specidList:
        j = 0
        for (srcmef, srcgem) in obs:
            fpub.write(srcmef+'=\''+srcgem+'\'\n')
    fpub.write('\n')
    
    publish = 'publish -v '
    commonopts = ' --getvsopname --mefdir=../redux --publish --keep2d'
    if options.debug:
        print specidList
    for obs in specidList:
        j = 0
        if options.debug:
            print obs
        for (srcmef, srcgem) in obs:
            if options.debug:
                print j, srcmef, srcgem  
            towrite = publish+'${'+srcmef+'}'+commonopts
            if j != 0:
                towrite = '%s --id=%d' % (towrite, (j+1))
            fpub.write(towrite+'\n') 
            j += 1        
    fpub.close()
    os.chmod(os.path.join(targetpath,'pub'+options.obsnb), 0755)
    

if __name__ == '__main__':
    main()
