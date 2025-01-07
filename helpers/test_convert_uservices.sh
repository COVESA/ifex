#!/bin/bash

# A small test script to use https://github.com/COVESA/uservices
# as a quite comprehensive input test suite, (it is defined in protobuf/gRPC IDL)
# and convert as much as possible using the protobuf/grpc->IFEX converter

# Normalize current directory
cd "$(dirname "$0")"

P2I=../input_filters/protobuf_to_ifex.py

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
   python $P2I "$f" >".output/$ifexname"
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
