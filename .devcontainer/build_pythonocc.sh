#!/bin/bash

PYTHON_OCC_CORE_VERSION=$1

wget -q https://github.com/tpaviot/pythonocc-core/archive/$PYTHON_OCC_CORE_VERSION.tar.gz
tar -xf $PYTHON_OCC_CORE_VERSION.tar.gz

# patch for python 3.10
patch -d ./pythonocc-core-$PYTHON_OCC_CORE_VERSION -s "-Np1" -i ../python3.10.patch


# 3.10-bullseye image has python3.10 installed to /usr/local,
# ensure we use the correct prefix
cmake  ./pythonocc-core-$PYTHON_OCC_CORE_VERSION \
    -DPython3_EXECUTABLE:FILEPATH=`which python`

cmake --build ./ -j$(nproc --all)
cmake --install .
# rm -rf * .*