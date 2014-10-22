#!/usr/bin/python
import os
import rpm
import sys


def readRpmHeader(ts, filename):
    """ Read an rpm header. """
    fd = os.open(filename, os.O_RDONLY)
    h = None
    try:
        h = ts.hdrFromFdno(fd)
    except rpm.error, e:
        if str(e) == "error reading package header":
            sys.stderr.write(str(e))
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
            sys.stderr.write("Error: file %r was not found!" % f)
            return 1
        h = readRpmHeader(ts, f)
        name = h[rpm.RPMTAG_NAME]
        if (name not in fresh_rpms
                or rpm.versionCompare(h, fresh_rpms[name]['header']) > 0):
            fresh_rpms[name] = {'header': h, 'filename': f}

    for n, v in fresh_rpms.iteritems():
        print v['filename']

if __name__ == '__main__':
    sys.exit(main(sys.argv))
