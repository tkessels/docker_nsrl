# !/usr/bin/env python
# -*- coding: utf-8 -*-

import binascii
import os
import ConfigParser
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
    default_config_file='/nsrl/nsrl.conf'
    configfiles=[default_config_file]
    if not args.config is None:
        #add user config
        if os.path.isfile(args.config):
            configfiles.append(args.config)

    #build config
    conf = ConfigParser.ConfigParser()
    conf.read(configfiles)
    #add commandline options
    # conf=config["config"]
    if args.error_rate:
        conf.set("config","error_rate",str(args.error_rate))
    if args.hashcount:
        conf.set("config","hash_count",str(args.hashcount))
    if args.column:
        conf.set("config","hashfile_column",str(args.column))
    if args.label:
        conf.set("config","hashfile_type",str(args.label))
    if args.delimiter:
        conf.set("config","hashfile_delimiter",str(args.delimiter))
    if args.inputfile:
        conf.set("config","hashfile_path",str(args.inputfile))

    nsrl_path='/nsrl/NSRLFile.txt'
    error_rate=0.01
    hashfile_delimiter=','
    hashfile_column=0
    hashfile_type='Hash'
    nsrl_path=conf.get("config","hashfile_path")
    error_rate=conf.getfloat("config",'error_rate')
    hashfile_delimiter=conf.get("config",'hashfile_delimiter')
    hashfile_column=conf.getint("config",'hashfile_column')
    hashfile_type=conf.get("config",'hashfile_type')

    print "[BUILDING] Using error-rate: {}".format(error_rate)
    if os.path.isfile(nsrl_path):
        print "[BUILDING] Reading in NSRL Database"
        if not conf.has_option("config","hash_count"):
            with open(nsrl_path) as f_line:
                # Strip off header
                _ = f_line.readline()
                print "[BUILDING] Calculating number of entries in Inputfile..."
                num_lines = sum(bl.count("\n") for bl in blocks(f_line))
                conf.set("config",'hash_count',str(num_lines))
        else:
            num_lines=conf.getint("config","hash_count")
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

    #save config
    with open(default_config_file,'w') as configfile:
        conf.write(configfile)


if __name__ == "__main__":
    main()
