# !/usr/bin/env python
# -*- coding: utf-8 -*-

import binascii
import os
from pybloom import BloomFilter


import argparse



# reference - http://stackoverflow.com/a/9631635
def blocks(this_file, size=65536):
    while True:
        b = this_file.read(size)
        if not b:
            break
        yield b


def main():
    parser = argparse.ArgumentParser(prog='build.py')
    parser.add_argument("-v", "--verbose", help="Display verbose output message", action="store_true", required=False)
    config = parser.add_mutually_exclusive_group()
    config.add_argument('-f', "--config", default="/nsrl/nsrl.conf",help='Config file with all settings')
    settings = config.add_argument_group()
    settings.add_argument('-e','--error-rate', type=float, default=0.01 ,help="Error Rate for False-Positives")
    settings.add_argument('-n','--hashcount',type=int, help="Provide the hashcount")
    settings.add_argument('-c','--column', type=int, default=1 ,help="Which Column of inputfile should be processed (0,1,...)")
    settings.add_argument('-l','--label', default="MD5",help="What kind of Data is beeing processed (MD5,filenames,...)")
    settings.add_argument('-d','--delimiter', default=',' , help="Which char is used to delimit columns in inputfile")
    settings.add_argument('-i','--inputfile', default='/nsrl/NSRLFile.txt' , help="Path of input file")


    args = parser.parse_args()

    nsrl_path = args.inputfile
    error_rate = args.error_rate

    print "[BUILDING] Using error-rate: {}".format(error_rate)
    if os.path.isfile(nsrl_path):
        print "[BUILDING] Reading in NSRL Database"
        if args.hashcount is None:
            with open(nsrl_path) as f_line:
                # Strip off header
                _ = f_line.readline()
                print "[BUILDING] Calculating number of hashes in NSRL..."
                num_lines = sum(bl.count("\n") for bl in blocks(f_line))
        else:
            num_lines=args.hashcount
        print "[BUILDING] There are %s hashes in the NSRL Database" % num_lines
        with open(nsrl_path) as f_nsrl:
            # Strip off header
            _ = f_nsrl.readline()
            print "[BUILDING] Creating bloomfilter"
            bf = BloomFilter(num_lines, error_rate)
            print "[BUILDING] Inserting hashes into bloomfilter"
            # sha1 hash is in column 0
            for line in f_nsrl:
                hashline = line.split(args.delimiter)[args.column].strip('"')
                if hashline:
                    try:
                        hash = binascii.unhexlify(hashline)
                        bf.add(hash)
                    except Exception as e:
                        print "[ERROR] %s" % e
            print "[BUILDING] NSRL bloomfilter contains {} items.".format(len(bf))
            with open('nsrl.bloom', 'wb') as nb:
                bf.tofile(nb)
            print "[BUILDING] Complete"
    else:
        print("[ERROR] No such file or directory: %s", nsrl_path)

    return


if __name__ == "__main__":
    main()
