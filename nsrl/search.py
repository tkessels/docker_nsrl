#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import binascii

from pybloom import BloomFilter

def main():
    parser = argparse.ArgumentParser(prog='nsrl')
    parser.add_argument("-v", "--verbose", help="Display verbose output message", action="store_true", required=False)
    parser.add_argument("-m", "--mismatched", help="Echo only mismatched Hashvalues", action="store_true", required=False)
    parser.add_argument('hash', metavar='MD5', type=str, nargs='+', help='md5 hash to search for.')
    args = parser.parse_args()

    with open('nsrl.bloom', 'rb') as nb:
        bf = BloomFilter.fromfile(nb)

        for hash_hex in args.hash:
            hash = binascii.unhexlify(hash_hex)
            output=""

            # only print output if for mismatches if selected
            if ((not hash in bf) or (not args.mismatched)):
                if args.verbose:
                    output = "{}:{}".format(hash_hex,hash in bf)
                else:
                    if args.mismatched:
                        output = "{}".format(hash_hex)
                    else:
                        output = "{}".format(hash in bf)

                print output
    return

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print "Error: %s" % e
