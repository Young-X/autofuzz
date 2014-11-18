# STATUS works, but is very slow (7/sec)

class cppcheck:
    name = __name__
    home = "http://cppcheck.sourceforge.net/"
    scmOrigin = "git clone https://github.com/danmar/cppcheck.git"
    dataTypes = [
        "c"    # XXX also use cpp input sample
    ]

    target = "cppcheck"
    targetParam = "test.c"
    aflFuzzParam = "-f test.c"

    clean = [
        "make clean"
    ]

    build = [
        "CXX=afl-g++ make"
    ]