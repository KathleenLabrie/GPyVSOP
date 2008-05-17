# Import core Python modules
import optparse, os.path, re# string, datetime, tempfile

# Import scientific modules
import pyfits

# Import GPyVSOP modules
import GPyVSOPutil

VERSION = '1.0.2'

matchfits = re.compile(r"(\.fits)$")
matchvsopname = re.compile(r'\.(\d\d\d)_s1d')


def checkinputs(p, options, args):

    if options.keep2d and (not options.getvsopname):
        errmsg = '--keep2d works only with --getvsopname'
        raise IOError, errmsg

    if len(args) != 1:
        print '\nUSAGE ERROR: Specify the name of one FITS file'
        p.print_help()
        raise SystemExit
    else:
        filename = matchfits.sub(r'',args[0])

    if options.getvsopname:
        if os.path.isdir(options.mefdir) == False:
            errmsg = 'Directory \''+options.mefdir+'\' does not exist'
            raise IOError, errmsg
    
    if os.path.exists(options.mefdir+'/'+filename+'.fits') == False:
        errmsg = 'File \''+filename+'.fits\' not found'
        raise IOError, errmsg
                       
    return filename


def main():

    # Parse input arguments
    usage = 'usage: %prog [options] specfile'
    p = optparse.OptionParser(usage=usage, version='v'+VERSION)
    p.add_option('--debug', action='store_true', help='toggle debug messages')
    p.add_option('--verbose', '-v', action='store_true', help='toggle on verbose')
    p.add_option('--flag', action='store_true', help='publish the flag file')
    p.add_option('--getvsopname', action='store_true', help='get VSOP name from MEF file')
    p.add_option('--mefdir', action='store', type='string', dest='mefdir', default='./', help='location of the MEF file')
    p.add_option('--publish', action='store_true', help='publish on the wiki')
    p.add_option('--instrument', action='store', type='string', dest='instrument', help='GMOSN or GMOSS')
    p.add_option('--id', action='store', type='string', default=1, dest='id', help='source ID')
    p.add_option('--keep2d', action='store_true', help='upload 2d spectrum')

    (options, args) = p.parse_args()
    
    if options.debug:
        options.verbose = True
        print 'options: ', options
        print 'args: ', args

    
    # Check inputs
    try:
        fname = checkinputs(p, options, args)
    except:
        raise

        
    if options.getvsopname:
        try:
            srcID = int(options.id) - 1
            vsopname = GPyVSOPutil.getvsopname(fname+'.fits',options.instrument,options.mefdir)
            tmpnb = matchvsopname.findall(vsopname)
            substr = '.%03d' % (int(tmpnb[0])+srcID)
            vsopfile = matchvsopname.sub(substr+'_s1d', vsopname)
            vsop2dfile = matchvsopname.sub(substr+'_s2d', vsopname)
            if os.path.exists(vsopfile) == False:
                errmsg = 'File \''+vsopfile+'\' not found'
                raise IOError, errmsg
        except:
            raise
    else:
        vsopfile = fname+'.fits'


    if options.debug:
        print vsopfile
    
    # Get header data
    phu = pyfits.getheader(vsopfile, 0)
    instrument = phu['INSTRUME']
    dateobs = phu['DATE-OBS']
    gemprgid = phu['GEMPRGID']
    obsid = phu['OBSID']
    objectname = phu['OBJECT']
    pipeline_ver = phu['VSOPPIPE']
    
    instrument = instrument.replace('-','',1)
    
    if options.debug:
        print objectname, gemprgid, obsid
        print dateobs, instrument   # needed to set the remote site directory

    # Create FLAG file
    flagfile = '.'.join((instrument,dateobs))
    notify = 'klabrie@gemini.edu,tdall@gemini.edu'
    f = open (flagfile, mode='w')
    f.write('INST '+instrument+'\n')
    f.write('DATE '+dateobs+'\n')
    f.write('DIR '+dateobs+'\n')
    f.write('EMNOTE '+notify+'\n')
    f.close()
    
    
    # Publish
    #   ncftpput -u vsop -R ftp.eso.org <instrument> <vsopfile>
    #   ncftpput -u vsop -R ftp.eso.org ToDo/dates <flagfile>
    #
    #   Goes to http://vsop.sc.eso.org/data/GMOS?/YYYY-MM-DD/
    #   data: vsop@vsop.sc.eso.org/public_html/data/GMOS?/YYYY-MM-DD/
    
    remotesite = 'ftp.eso.org'
    username = 'vsop'
    remotedir = '/'.join((instrument,dateobs))
    
    uploadspec = ' '.join(('ncftpput -m -u',username,'-R',remotesite,remotedir,vsopfile))
    if options.keep2d:
        upload2d = ' '.join(('ncftpput -m -u',username,'-R',remotesite,remotedir,vsop2dfile))
    if options.flag:
        uploadflag = ' '.join(('ncftpput -u',username,'-R',remotesite,'ToDo/dates',flagfile))
    if options.publish:
        os.system(uploadspec)
        if options.keep2d:
            os.system(upload2d)
        if options.flag:
            os.system(uploadflag)

    else:
        print
        print 'Test run. Would be running the following system calls:'
        print '   '+uploadspec
        if options.flag:
            print '   '+uploadflag
        print
    
    # Print GEMPRGID and OBSID to help with the wiki page update
    wikiserver = 'vsop.eso.org'
    print '---------------------------------------'
    print 'OBJECT:    ', objectname
    print 'GEMPRGID:  ', gemprgid
    print 'OBSID:     ', obsid
    print 'DATE-OBS   ', dateobs
    print 'Target ID  ', options.id
    print 'URL:                      https://'+'/'.join((wikiserver,'wiki',objectname.replace(' ','_',1)))
    print 'Spectrum to be stored in: http://'+'/'.join((wikiserver,'data',instrument,dateobs))
    print 'Spectrum file name:      ', vsopfile
    print 'VSOPPIPE   ', pipeline_ver
    print '---------------------------------------'
    
      
if __name__ == '__main__':
    main()
