# gmosLSutil.py
# Functions for gmosLS
#
#  In this module:
#       checkinputs(p, options, args)
#    

import os.path, re

from GPyVSOPutil import getvsopname

matchfits = re.compile(r"(\.fits)$")

def checkinputs(p, options, args):

    # Defaults
    validInterFlags = ('extract', 'skysub', 'wavecal', 'crrej')
    interFlags = {'extract': False,
                  'skysub': False,
                  'wavecal': False,
                  'crrej': False}
    
    if len(args) == 0:
        print '\nUSAGE ERROR: Specify at least one science frame'
        p.print_help()
        raise SystemExit
    
    # Remove .fits
    inlist = map((lambda s: matchfits.sub(r'',s)), args)
    if options.procbias != None: options.procbias = matchfits.sub(r'',options.procbias)
    if options.flatfile != None: options.flatfile = matchfits.sub(r'',options.flatfile)
    if options.arcfile  != None: options.arcfile  = matchfits.sub(r'',options.arcfile)
    
    if options.debug:
        print inlist
        print options.procbias
        print options.flatfile
        print options.arcfile
    
    
    # Check that directories exist
    if os.path.isdir(options.rawdir) == False:
        errmsg = 'Directory \''+options.rawdir+'\' does not exist'
        raise IOError, errmsg
    if not options.nofits:
        if os.path.isdir(options.wikidir) == False:
            errmsg = 'Directory \''+options.wikidir+'\' does not exist'
            raise IOError, errmsg    
    
    # Check that input files exist
    for filename in inlist:
        if os.path.exists(options.rawdir+'/'+filename+'.fits') == False:
            errmsg = 'File \''+filename+'\' not found'
            raise IOError, errmsg
    if options.procbias != None:
        if os.path.exists(options.rawdir+'/'+options.procbias+'.fits') == False:
            errmsg = 'File \''+options.procbias+'\' not found'
            raise IOError, errmsg
    if options.flatfile != None:
        if os.path.exists(options.rawdir+'/'+options.flatfile+'.fits') == False:
            errmsg = 'File \''+options.flatfile+'\' not found'
            raise IOError, errmsg    
    if options.arcfile != None:
        if os.path.exists(options.rawdir+'/'+options.arcfile+'.fits') == False:
            errmsg = 'File \''+options.arcfile+'\' not found'
            raise IOError, errmsg

    # Set interactive flags
    if (options.interproc != None):
        for proc in options.interproc.split(','):
            if proc in validInterFlags:
                interFlags[proc] = True
            else:
                errmsg = 'Invalid processes for --inter. Valid flags are: ', validInterFlags
                raise IOError, errmsg
    
    # Get vsopfile names
    vsopnames = []
    try:
        for i in range(len(inlist)):
            vsopname = getvsopname(inlist[i]+'.fits', options.instrument, options.rawdir)
            vsopnames.append(vsopname)
    except:
        raise
    #    try:
    #        vsopname = getvsopname(inlist[0]+'.fits', options.instrument, options.rawdir)
    #    except:
    #        raise

    return (inlist, vsopnames, interFlags)


    

