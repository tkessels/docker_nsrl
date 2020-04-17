#!/bin/sh
#set -x

#read information from config
rds_url=$(cat /nsrl/nsrl.conf | grep 'rds_url' | cut -f2- -d= | grep -o -E '\S+.*')
echo "rds_url=${rds_url}"
version_url=$(cat /nsrl/nsrl.conf | grep 'version_url' | cut -f2- -d= | grep -o -E '\S+.*')
echo "version_url=${version_url}"
error_rate=$(cat /nsrl/nsrl.conf | grep 'error_rate' | cut -f2- -d=| grep -o -E '\S+.*' )
echo "error_rate=${error_rate}"
rds_name=$(cat /nsrl/nsrl.conf | grep 'rds_name' | cut -f2- -d= | grep -o -E '\S+.*')
echo "rds_name=${rds_name}"
hashfile_name=$(cat /nsrl/nsrl.conf | grep 'hashfile_name' | cut -f2- -d= | grep -o -E '\S+.*')
echo "hashfile_name=${hashfile_name}"
build_date=$(date +%Y%M%d_%H%M)
echo "build_date=${build_date}"

#check if a zipfile was provided
if [ -f /nsrl/*.zip ]; then
  zip_filename=$(ls /nsrl/*.zip | head -n1)
  echo "[INFO] ZIP-File Exists : ${zip_filename}"
  zip_md5=$(md5sum "${zip_filename}" | cut -f1 -d" ")
  rds_version=$(stat -c %y "${zip_filename}" )
else
  zip_filename=${rds_url##*/}
  echo "[INFO] Downloading NSRL Sets (${rds_name}):"
  echo "[INFO] URL: ${rds_url}"
  #Downloading and Hashing at the same time
  zip_md5=$(wget -O - "${rds_url}" 2>/dev/null | tee "/nsrl/${zip_filename}" | md5sum | cut -f1 -d" ")
  rds_version=$(wget -O - "${version_url}" 2>/dev/null | tee "/nsrl/.version" | head -n1 )
fi


echo "[INFO] Unzip NSRL Database zip to /nsrl/ ..."
7z x -o/nsrl/ "/nsrl/${zip_filename}"

echo "[INFO] Counting Hashes in /nsrl/${hashfile_name} ..."
#counting lines in hashfile without headline
let hash_count=$(cat "/nsrl/${hashfile_name}"|wc -l )-1
echo "[INFO] /nsrl/${hashfile_name} contains ${hash_count} Hashes"

echo "[INFO] Build bloomfilter from NSRL Database ..."
cd /nsrl && python /nsrl/build.py -e "${error_rate}" -n "${hash_count}"
echo "[INFO] Listing created files ..."
ls -lah /nsrl

echo "[INFO] Deleting all unused files ..."
rm -f /nsrl/*.zip /nsrl/*.txt
ls -lah /nsrl

#update config
echo "[INFO] Update Config ..."
echo "build_date = ${build_date}" >> /nsrl/nsrl.conf
echo "zip_filename = ${zip_filename}" >> /nsrl/nsrl.conf
echo "zip_md5 = ${zip_md5}" >> /nsrl/nsrl.conf
echo "rds_version = ${rds_version}" >> /nsrl/nsrl.conf
echo "hash_count = ${hash_count}" >> /nsrl/nsrl.conf
cat /nsrl/nsrl.conf
