#!/bin/bash

cp ./logEvaluat.py ./result/logEvaluat.py
cd ./result
python3 ./logEvaluat.py
rm ./logEvaluat.py
mkdir ./statistics
mv ./*.csv ./statistics
mv ./*.png ./statistics
mv ./*.txt ./statistics
#mv ./*.dat ./statistics

