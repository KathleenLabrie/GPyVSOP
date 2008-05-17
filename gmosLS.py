#
#
# Import core Python modules
import optparse, re, shutil, os.path

# Import GUI modules

# Import scientific modules
import pyfits

# Import PyRAF and IRAF, then the IRAF packages
import pyraf, iraf
from pyraf.iraf import gemini

# Import GPyVSOP modules
import gmosLSutil, GPyVSOPutil

VERSION = '1.0.2'
matchfits = re.compile(r'(\.fits)$')
matchvsopname = re.compile(r'\.(\d\d\d)_s1d')

def tagversion(fname):
    if matchfits.search(fname) == None:
        fname = fname + '.fits'
    hdulist = pyfits.open(fname, mode='update')
    hdulist[0].header.update('VSOPPIPE', 'v'+VERSION, 'Version of VSOP pipeline')
    hdulist[0].header.add_history('Processed with GPyVSOP gmosLS v'+VERSION)
    hdulist.flush()
    hdulist.close()


def main():

    # Parse input arguments
    usage = 'usage: %prog [options] scifiles'
    p = optparse.OptionParser(usage=usage, version='v'+VERSION)
    p.add_option('--debug', action='store_true', help='toggle debug messages')
    p.add_option('--verbose', '-v', action='store_true', help="toggle on verbose mode")
    p.add_option('--bias', action='store', type='string', dest='procbias', help='name of the processed bias file')
    p.add_option('--arc', action='store', type='string', dest='arcfile', help='name of the arc file')
    p.add_option('--flat', action='store', type='string', dest='flatfile', help='name of the flat file')
    p.add_option('--inter', action='store', type='string', dest='interproc', help='Processes to run interactively (extract,skysub,wavecal)')    
    p.add_option('--logfile', action='store', type='string', dest='logfile', help='name of the logfile')
    p.add_option('--rawdir', action='store', type='string', dest='rawdir', default='./', help='path to the raw data')
    p.add_option('--wikidir', action='store', type='string', dest='wikidir', default='./', help='path to upload directory')
    p.add_option('--instrument', action='store', type='string', dest='instrument', help='GMOSN or GMOSS')
    p.add_option('--nofits', action='store_true', help='do not generate the VSOP FITS file')
    p.add_option('--combine', action='store_true', help='combine science spectra')
    p.add_option('--nsrc', action='store', default=1, help='number of sources to extract (0 if undetermined)')
    p.add_option('--keep2d', action='store_true', help='keep 2d spectrum and assign VSOP name')

    (options, args) = p.parse_args()
    
    if options.debug:
        options.verbose = True
        print 'options: ', options
        print 'args: ', args

    # Set defaults
    extname = 'SCI'
    extver = 1

    if options.combine:
        print 'SPECTRUM COMBINATION NOT IMPLEMENTED YET'
        print 'Exiting'
        return

    try:
        (inlist, vsopnames, interFlags) = gmosLSutil.checkinputs(p, options, args)
    except:
        raise
       
    if int(options.nsrc) != 1:
        if int(options.nsrc) == 0: print 'Undetermined number of sources to extract'
        else:                 print options.nsrc, ' sources to extract'
        print 'Interactive sky subtraction toggled on'
        print 'Interactive extraction toggled on'
        interFlags['extract'] = True
        interFlags['skysub'] = True
        
    if options.debug:
        print 'inlist: ', inlist
        print 'vsopnames: ', vsopnames
        print 'interFlags: ', interFlags


    #######################################################################
    ###### Start Reduction ######
    
    # Load gemini IRAF
    gemini.gmos()

    # Make flat field
    if options.flatfile != None:
        fl_flat = 'yes'
        #procflat = matchfits.sub(r'_flat\1', options.flatfile)
        procflat = options.flatfile+'_flat.fits'
        try:
            gemini.gsflat(options.flatfile, procflat, order=29, 
                rawpath=options.rawdir+'/', 
                bias=options.rawdir+'/'+options.procbias,
                logfile=options.logfile)
        except:
            print 'Problem in GSFLAT'
            
        # Add keyword with gmosLS version number
        tagversion(procflat)
        
    else:
        fl_flat = 'no'

    
    # Reduce the science spectrum
    inputstr = ','.join(inlist)
    try:
        gemini.gsreduce(inputstr, rawpath=options.rawdir+'/',
            bias=options.rawdir+'/'+options.procbias, fl_gscrrej='yes',
            fl_inter=interFlags['crrej'], fl_flat=fl_flat, flat=procflat,
            logfile=options.logfile)
    except:
        print 'Problem in GSREDUCE (science frames)'
        return
    
    # Add keyword with gmosLS version number
    for f in inlist:
        tagversion('gs'+f)

    if options.arcfile != None:
        # Reduce the arc
        try:
            gemini.gsreduce(options.arcfile, rawpath=options.rawdir+'/',
                fl_flat='no', fl_fixpix='no',
                bias=options.rawdir+'/'+options.procbias,
                logfile=options.logfile)
        except:
            print 'Problem in GSREDUCE (arc frame)'
            return
        
        # Add keyword with gmosLS version number
        tagversion('gs'+options.arcfile)
    
        # Establish the wavelength calibration
        try:
            gemini.gswavelength('gs'+options.arcfile,
                coordlist="linelists$cuar.dat", fwidth=10, cradius=12,
                minsep=5., logfile=options.logfile)
        except:
            print 'Problem in GSWAVELENGTH'
            return

        # Apply the wavelength calibration
        try:
            gemini.gstransform('gs'+options.arcfile,
                wavtran='gs'+options.arcfile, logfile=options.logfile)
            inputstr = ','.join(map((lambda s: 'gs' + s), inlist))
            gemini.gstransform(inputstr, wavtran='gs'+options.arcfile,
                logfile=options.logfile)
        except:
            print 'Problem in GSTRANSFORM'
            return


    notdone = True
    srcID = 0
    while notdone:
        # Subtract sky emission
        inputstr = ','.join(map((lambda s: 'tgs' + s), inlist))
        if int(options.nsrc) == 1:  IDstr = ''
        else:                       IDstr = str(srcID+1)
        outpref = 's'+IDstr
        gemini.gsskysub(inputstr, outpref=outpref,
            long_sample="50:200,325:475", logfile=options.logfile,
            fl_inter=interFlags['skysub'], function='chebyshev',order=3)

        ##### Probably should combine multiple spectra here
        # Combine spectra
        if options.combine and len(inlist) > 1:
            print 'Multiple spectra.  They need to combine.'
            print 'SPECTRUM COMBINATION NOT IMPLEMENTED YET'
            print 'Exiting'
            return
        
        # Extract 1-D spectrum
        inputstr = ','.join(map((lambda s: 's'+IDstr+'tgs' + s), inlist))
        gemini.gsextract(inputstr, logfile=options.logfile,
            fl_inter=interFlags['extract'])


        ####################################################################
        ####### Convert to VSOP format #######

        # Create single fits from mef phu and first sci extension
        dsetlist = []
        if options.combine:
            dsetlist.append(inlist[0])
        else:
            dsetlist.extend(inlist)
        for i in range(len(dsetlist)):
            newhdulist = GPyVSOPutil.mef2fits('es'+IDstr+'tgs'+dsetlist[i]+'.fits', extname, extver)
            if options.debug:
                print newhdulist.info()
                print newhdulist[0].header    
            # Write to wikidir
            if not options.nofits:
                tmpnb = matchvsopname.findall(vsopnames[i])
                substr = '.%03d' % (int(tmpnb[0])+srcID)
                thissrcvsopname = matchvsopname.sub(substr+'_s1d', vsopnames[i])
                print 'Writing to VSOP FITS: ',thissrcvsopname
                GPyVSOPutil.writefits(newhdulist, thissrcvsopname, options.wikidir)
            newhdulist.close()
            
            if options.keep2d and (not options.nofits):
                shutil.copy('es'+IDstr+'tgs'+dsetlist[i]+'.fits', os.path.join(options.wikidir, thissrcvsopname))

        if srcID+1 == int(options.nsrc):
            notdone = False     # we are done
        elif int(options.nsrc) == 0:
            notvalid = True
            while notvalid:
                answer = raw_input('Extract another source? (y/n): ')
                if answer == 'y': 
                    srcID += 1
                    notvalid = False
                elif answer == 'n':
                    notdone = False     # we are done
                    notvalid = False
                else:
                    print "Invalid answer.  Type 'y' or 'n'."
                
                
        else:
            srcID += 1      # next source



if __name__ == '__main__':
    main()
