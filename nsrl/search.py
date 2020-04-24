#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import binascii
import ConfigParser
import sys

from pybloom import BloomFilter

def main():
    default_config_file='/nsrl/nsrl.conf'
    config = ConfigParser.ConfigParser()
    config.read(default_config_file)
    #add commandline options
    hash_type=config.get('config','hashfile_type')

    parser = argparse.ArgumentParser(prog='nsrl')
    parser.add_argument("-v", "--verbose", help="Display verbose output message", action="store_true", required=False)
    parser.add_argument("-0", "--no-hits", help="Suppress Output of matching hashes", action="store_true", required=False)
    parser.add_argument("-1", "--no-misses", help="Suppress Output of mismatching hashes", action="store_true", required=False)
    inputs = parser.add_mutually_exclusive_group(required=True)
    inputs.add_argument('hash', metavar='<{}>'.format(hash_type), type=str, nargs='*', default=[], help='{} hash to search for.'.format(hash_type))
    inputs.add_argument('-s','--stdin',help="Read hashes from stdin", action="store_true")
    args = parser.parse_args()

    if args.verbose:
        print("Version INFO: {}".format(config.get('config',"rds_version")))
        print("Error Rate: {}".format(config.get('config',"error_rate")))
        print("Build Date: {}".format(config.get('config',"build_date")))
        print("Filename: {}".format(config.get('config',"hashfile_name")))
        print("Hashcount: {}".format(config.get('config',"hash_count")))



    with open('nsrl.bloom', 'rb') as nb:
        bf = BloomFilter.fromfile(nb)

        if args.stdin:
            hashlist=[hash.strip() for hash in sys.stdin.readlines()]
        else:
            hashlist=args.hash
        for hash_hex in hashlist:
            hash = binascii.unhexlify(hash_hex)
            output=""

            # only print output if for mismatches if selected
            hash_is_a_match=(hash in bf)
            if (hash_is_a_match and not args.no_hits) or (not hash_is_a_match and not args.no_misses):
                #output
                if args.verbose:
                    output = "{}:{}".format(hash_hex,hash_is_a_match)
                elif args.no_hits != args.no_misses :
                    output = "{}".format(hash_hex)
                else:
                    output = "{}:{}".format("+"if hash_is_a_match else "-",hash_hex)
                print output
    return

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print "Error: %s" % e
