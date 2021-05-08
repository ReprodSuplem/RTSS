#!/bin/bash

rm -rf ./result

cd ./instance/ip/hp1
for groupName in $(ls); do
	mkdir -p "../../../result/ip/hp1/${groupName}"
	cd $groupName
	for insName in $(ls *.lp | awk -F "." '{print $1}'); do
		$1 -c "set threads 1" "set timelimit 600" "read ${insName}.lp" "read ${insName}.mst" "opt" "disp sol var -" 2>&1 | tee "../../../../result/ip/hp1/${groupName}/${insName}.log"
	done
	rm ./cplex.log
	cd ../
done

cd ../../../instance/ip/hp2
for groupName in $(ls); do
	mkdir -p "../../../result/ip/hp2/${groupName}"
	cd $groupName
	for insName in $(ls *.lp | awk -F "." '{print $1}'); do
		$1 -c "set threads 1" "set timelimit 600" "read ${insName}.lp" "read ${insName}.mst" "opt" "disp sol var -" 2>&1 | tee "../../../../result/ip/hp2/${groupName}/${insName}.log"
	done
	rm ./cplex.log
	cd ../
done



cd ../../../instance/maxsat/hp1
for groupName in $(ls); do
	mkdir -p "../../../result/maxsat/hp1/${groupName}"
	cd $groupName
	for insName in $(ls *.wcnf | awk -F "." '{print $1}'); do
		../../../../qmaxsatRtss -cpu-lim=600 -card=mrwto -pmodel=0 -incr=1 "${insName}.wcnf" "${insName}.ext" ./answer.txt 2>&1 | tee "../../../../result/maxsat/hp1/${groupName}/${insName}.log"
	done
	rm ./answer.txt
	cd ../
done

cd ../../../instance/maxsat/hp2
for groupName in $(ls); do
	mkdir -p "../../../result/maxsat/hp2/${groupName}"
	cd $groupName
	for insName in $(ls *.wcnf | awk -F "." '{print $1}'); do
		../../../../qmaxsatRtss -cpu-lim=600 -card=mrwto -pmodel=0 -incr=1 "${insName}.wcnf" "${insName}.ext" ./answer.txt 2>&1 | tee "../../../../result/maxsat/hp2/${groupName}/${insName}.log"
	done
	rm ./answer.txt
	cd ../
done



