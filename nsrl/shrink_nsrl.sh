#!/bin/sh

# copyright: (c) 2014 by Josh "blacktop" Maine.
# license: MIT

baseurl="https://s3.amazonaws.com/rds.nsrl.nist.gov/RDS/current/"
rds_file="rds_modernm.zip"
version_file="version.txt"

set -x

ERROR_RATE=0.01

if [ -f /nsrl/*.zip ]; then
   echo "File '.zip' Exists."
else
    echo "[INFO] Downloading NSRL Reduced Sets..."
    wget -P /nsrl/ "${baseurl}${rds_file}" 2>/dev/null
    wget -O /nsrl/version "${baseurl}${version_file}" 2>/dev/null
fi

echo "[INFO] Unzip NSRL Database zip to /nsrl/ ..."
7za x -o/nsrl/ /nsrl/*.zip

echo "[INFO] Build bloomfilter from NSRL Database ..."
cd /nsrl && python /nsrl/build.py $ERROR_RATE
echo "[INFO] Listing created files ..."
ls -lah /nsrl

echo "[INFO] Deleting all unused files ..."
rm -f /nsrl/*.zip /nsrl/*.txt /nsrl/build.py
ls -lah /nsrl
