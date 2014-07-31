# GPyVSOPutil.py
# Functions for GPyVSOP
#
#  In this module:
#       getvsopname(gemfile, instrument)
#       mef2fits(mef)
#       writefits(hdulist, filename, directory)
#

import re, string, datetime
import pyfits

matchInst = re.compile(r".*?(N|S)\d+S\d+\.fits$")

def getvsopname(gemfile, instrument, path):
    # Defaults
    validInstruments = ('GMOSN', 'GMOSS')
    instDict = {'N': 'GMOSN',
                'S': 'GMOSS'}

    # Verify instrument
    if instrument == None:
        if matchInst.match(gemfile) == None:
            errmsg = 'Invalid Gemini frame name, \''+gemfile+'\''
            raise IOError, errmsg
        instpref = matchInst.sub(r"\1",gemfile)
        instrument = instDict[instpref]
    elif instrument not in validInstruments:
        print '\nUSAGE ERROR: Invalid value for instrument (%s)' % instrument
        p.print_help()
        raise SystemExit
    
    phu = pyfits.getheader(path+'/'+gemfile, 0)
    dateobs = phu['DATE-OBS']
    timeobs = phu['TIME-OBS']
    
    (year,month,date) = map(string.atoi, dateobs.split('-'))
    d = datetime.date(year,month,date)
    (hour,minutes,seconds) = map(string.atof, timeobs.split(':'))
    microseconds = round((seconds - int(seconds)) * 1e6)
    if int(microseconds) == 0:  microseconds += 1
    t = datetime.time(int(hour),int(minutes),int(seconds),int(microseconds))
    dt = datetime.datetime.combine(d,t)

    return instrument+'.'+dt.isoformat()[:-3]+'_s1d.fits'
    
    
def mef2fits(mef, extname, extver):

    inhdulist = pyfits.open(mef)
    
    # inhdulist is a PHU + a SCI extension (with hdr & data)
    # From that we need to create a single FITS file:
    #   - combine the PHU and the SCI hdr into one header
    #   - one extension with combined header and data
    
    phucards = inhdulist[0].header.ascardlist()
    scicards = inhdulist[extname,extver].header.ascardlist()
   
    singlehdu = pyfits.Header()
    
    specialkeys = ['', 'SIMPLE', 'BITPIX', 'EXTEND', 'DATE', 'ORIGIN', \
        'XTENSION', 'PCOUNT', 'GCOUNT', 'EXTNAME', 'EXTVER', 'INHERIT', \
        'HISTORY', 'COMMENT', 'NAXIS']
    singlehdu.update('SIMPLE', True, comment='conforms to FITS standard')
    singlehdu.update('BITPIX', scicards['BITPIX'].value, comment='Bits per pixels')
    singlehdu.update('EXTEND', False, comment='File may contain extensions')
    singlehdu.update('NAXIS', scicards['NAXIS'].value, comment='Number of axes')
    for axis in range(1,scicards['NAXIS'].value+1):
        singlehdu.update('NAXIS'+str(axis), scicards['NAXIS'+str(axis)].value, comment=scicards['NAXIS'+str(axis)].comment)
        specialkeys.append('NAXIS'+str(axis))
    singlehdu.update('ORIGIN', 'PyFITS kernel', comment='FITS file originator')
    singlehdu.update('DATE', datetime.datetime.today().isoformat(), comment='Date FITS file was generated')
    
    #for loop to create hdr
    for card in phucards:
        if card.key not in specialkeys:
            singlehdu.update(card.key, card.value, comment=card.comment)
        elif card.key == 'HISTORY':
            singlehdu.add_history(card.value)
        elif card.key == 'COMMENT':
            singlehdu.add_comment(card.value)        
    for card in scicards:
        if card.key not in specialkeys:
            singlehdu.update(card.key, card.value, comment=card.comment)
        elif card.key == 'HISTORY':
            singlehdu.add_history(card.value)
        elif card.key == 'COMMENT':
            singlehdu.add_comment(card.value)

    scidata = inhdulist[extname,extver].data
        
    newhdu = pyfits.PrimaryHDU(data=scidata, header=singlehdu)
    newhdulist = pyfits.HDUList([newhdu])
    
    return newhdulist


def writefits(hdulist, filename, directory):
    hdulist.writeto(directory+'/'+filename)
    
    return
