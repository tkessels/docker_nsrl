# !/usr/bin/env python
# -*- coding: utf-8 -*-

import binascii
import os
import configparser
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
    config.add_argument('-f', "--config", help='Config file with all settings')
    settings = config.add_argument_group()
    settings.add_argument('-e','--error-rate', type=float, help="Error Rate for False-Positives")
    settings.add_argument('-n','--hashcount',type=int, help="Provide the hashcount")
    settings.add_argument('-c','--column', type=int, help="Which Column of inputfile should be processed (0,1,...)")
    settings.add_argument('-l','--label', help="What kind of Data is beeing processed (MD5,filenames,...)")
    settings.add_argument('-d','--delimiter', ' , help="Which char is used to delimit columns in inputfile")
    settings.add_argument('-i','--inputfile',  help="Path of input file")
    settings.add_argument('-o','--outputfile',  help="Path of input file")


    args = parser.parse_args()

    #check if config-file was given
    configfiles=['/nsrl/nsrl.conf']
    if not args.config is None:
        #add user config
        if os.path.isfile(args.config):
            configfiles.append(args.config)

    #build config
    config = ConfigParser.ConfigParser()
    config.read(configfiles)
    #add commandline options
    conf=config["config"]
    if args.error_rate:
        conf["error_rate"]=args.error_rate
    if args.hashcount:
        conf["hash_count"]=args.hashcount
    if args.column:
        conf["hashfile_column"]=args.column
    if args.label:
        conf["hashfile_type"]=args.label
    if args.delimiter:
        conf["hashfile_delimiter"]=args.delimiter
    if args.inputfile:
        conf["hashfile_path"]=args.inputfile

    nsrl_path=conf.get("hashfile_path",'/nsrl/NSRLFile.txt')
    error_rate=conf.getfloat('error_rate',0.01)
    hashfile_delimiter=conf.get('hashfile_delimiter',',')
    hashfile_column=conf.getint('hashfile_column',0)
    hashfile_type=conf.get('hashfile_type','Hash')

    print "[BUILDING] Using error-rate: {}".format(error_rate)
    if os.path.isfile(nsrl_path):
        print "[BUILDING] Reading in NSRL Database"
        if not conf.has_option("hash_count"):
            with open(nsrl_path) as f_line:
                # Strip off header
                _ = f_line.readline()
                print "[BUILDING] Calculating number of entries in Inputfile..."
                num_lines = sum(bl.count("\n") for bl in blocks(f_line))
        else:
            num_lines=conf.getint("error_rate")
        print "[BUILDING] There are {} {}s in the Database".format(num_lines,hashfile_type)
        with open(nsrl_path) as f_nsrl:
            # Strip off header
            _ = f_nsrl.readline()
            print "[BUILDING] Creating bloomfilter"
            bf = BloomFilter(num_lines, error_rate)
            print "[BUILDING] Inserting {} into bloomfilter".format(hashfile_type)
            # sha1 hash is in column 0
            for line in f_nsrl:
                hashline = line.split(hashfile_delimiter)[hashfile_column].strip('"')
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
