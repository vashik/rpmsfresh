#!/usr/bin/python
import os
import rpm
import sys


def printError(filename, message):
    sys.stderr.write(sys.argv[0]+": `"+filename+"': "+message+"\n")

def readRpmHeader(ts, filename):
    """ Read an rpm header. """
    fd = os.open(filename, os.O_RDONLY)
    h = None
    try:
        h = ts.hdrFromFdno(fd)
    except rpm.error, e:
        if str(e) == "error reading package header":
            printError(filename, str(e))
        h = None
    finally:
        os.close(fd)
    return h

def main(argv):
    if len(argv) < 2:
        sys.stderr.write("Usage: %s PACKAGE_NAME...\n" % (argv[0],))
        return 1

    ts = rpm.TransactionSet()
    ts.setVSFlags(rpm._RPMVSF_NOSIGNATURES | rpm._RPMVSF_NODIGESTS)
    fresh_rpms = {}
    for f in argv[1:]:
        if not os.path.exists(f):
            printError(f, "file was not found")
            continue
        try:
            h = readRpmHeader(ts, f)
        except IOError as e:
            printError(f, "I/O error ({0}: {1}".format(e.errno, e.strerror))
            continue
        except:
            printError(f, "Unexpected error")
            continue
        if h is None:
            continue

        name = h[rpm.RPMTAG_NAME]
        arch = h[rpm.RPMTAG_ARCH]
        if (name,arch not in fresh_rpms
                or rpm.versionCompare(h, fresh_rpms[name,arch]['header']) > 0):
            fresh_rpms[name,arch] = {'header': h, 'filename': f}

    for n, v in fresh_rpms.iteritems():
        print v['filename']

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
