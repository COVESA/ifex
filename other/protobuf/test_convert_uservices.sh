#!/bin/bash

# Normalize current directory
cd "$(dirname "$0")"

# Clone if not existing
if [ ! -d uservices ] ; then
   (set -x ; git clone https://github.com/COVESA/uservices)
fi

rm -f .failed .ok
touch .failed .ok
rm -rf .output
mkdir -p .output

echo "Running protobuf_to_ifex on all uservices proto files"
find uservices/ -name '*.proto' | while read f ; do 
   echo "=== $f ===" 
   ifexname="$(echo "$(basename "$f")" | sed 's/.proto/.ifex/g')"
   python protobuf_to_ifex.py "$f" >".output/$ifexname"
   if [ $? -eq 0 ] ; then
      echo "$f" >>.ok
   else
      echo "$f" >>.failed
   fi
done

# Results
echo "Success:" 
cat .ok
echo 
echo "Fail:" 
cat .failed

echo "Result files are in .output/"
