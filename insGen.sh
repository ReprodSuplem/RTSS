#!/bin/bash

rm -rf ./instance

cd ./benchmarks

for fullGroupName in $(ls); do
	groupName=$(echo "$fullGroupName" | awk -F "-" '{print $5"-"$6}')
	mkdir -p "../instance/maxsat/hp1/${groupName}"
	mkdir -p "../instance/ip/hp1/${groupName}"
	mkdir -p "../instance/maxsat/hp2/${groupName}"
	mkdir -p "../instance/ip/hp2/${groupName}"
	cd $fullGroupName
	for insName in $(ls | awk -F "-" '{print $1"-"$2}'); do
		python2 ../../pySatFoRtss_hp1.py "${insName}"
		mv -f ./*.wcnf "../../instance/maxsat/hp1/${groupName}"
		mv -f ./*.ext "../../instance/maxsat/hp1/${groupName}"
		mv -f ./*.lp "../../instance/ip/hp1/${groupName}"
		mv -f ./*.mst "../../instance/ip/hp1/${groupName}"
		
		python2 ../../pySatFoRtss_hp2.py "${insName}"
		mv -f ./*.wcnf "../../instance/maxsat/hp2/${groupName}"
		mv -f ./*.ext "../../instance/maxsat/hp2/${groupName}"
		mv -f ./*.lp "../../instance/ip/hp2/${groupName}"
		mv -f ./*.mst "../../instance/ip/hp2/${groupName}"
	done
	cd ../
done

