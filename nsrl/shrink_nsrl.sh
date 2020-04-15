#!/bin/sh

rds_url=$(cat /nsrl/nsrl.conf | grep -Pio '(?<=rds_url = )\S+')
version_url=$(cat /nsrl/nsrl.conf | grep -Pio '(?<=version_url = )\S+')
ERROR_RATE=$(cat /nsrl/nsrl.conf | grep -Pio '(?<=error_rate = )\S+')
rds_name=$(cat /nsrl/nsrl.conf | grep -Pio '(?<=rds_name = ).+')
hashfile_name=$(cat /nsrl/nsrl.conf | grep -Pio '(?<=hashfile_name = ).+')
build_date=$(date +%Y%M%d_%H%M)

if [ -f /nsrl/*.zip ]; then
  zip_filename=$(ls /nsrl/*.zip | head -n1)
  echo "[INFO] ZIP-File Exists > ${zip_filename}"
  zip_md5=$(md5sum "${zip_filename}" | cut -f1 -d" ")
  rds_version=$(stat -c %y "${zip_filename}" )
else
  zip_filename=${rds_url##*/}
  echo "[INFO] Downloading NSRL Sets (${rds_name}):"
  echo "[INFO] URL: ${rds_url}"
  #Downloading and Hashing at the same time
  zip_md5=$(wget -O - "${rds_url}" 2>/dev/null | tee "/nsrl/${zip_filename}" | md5sum | cut -f1 -d" ")
  wget -O /nsrl/.version "${version_url}" 2>/dev/null
  rds_version=$(grep -F "${zip_md5}" /nsrl/.version | cut -f2 -d, | tr -d '"' )
fi

#update config
echo "build_date = ${build_date}" >> /nsrl/nsrl.conf
echo "zip_filename = ${zip_filename}" >> /nsrl/nsrl.conf
echo "zip_md5 = ${zip_md5}" >> /nsrl/nsrl.conf
echo "rds_version = ${rds_version}" >> /nsrl/nsrl.conf


echo "[INFO] Unzip NSRL Database zip to /nsrl/ ..."
7za x -o/nsrl/ "${zip_filename}"

echo "[INFO] Counting Hashes in /nsrl/${hashfile_name} ..."
hash_count=$(wc -l "/nsrl/${hashfile_name}")
#remove headline from count
(( hash_count=hash_count - 1 ))
echo "[INFO] /nsrl/${hashfile_name} contains ${hash_count} Hashes"
echo "hash_count = ${hash_count}" >> /nsrl/nsrl.conf


echo "[INFO] Build bloomfilter from NSRL Database ..."
cd /nsrl && python /nsrl/build.py $ERROR_RATE
echo "[INFO] Listing created files ..."
ls -lah /nsrl

echo "[INFO] Deleting all unused files ..."
rm -f /nsrl/*.zip /nsrl/*.txt
ls -lah /nsrl
