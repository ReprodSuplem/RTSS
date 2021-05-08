This is an instruction for reproducing the experiments described in our submission.

===== Part A =====
What the experimental environments we need?
1. Operation system: Ubuntu 18.04
2. GCC version: 7.5.0
3. Python2 verson: 2.7.17
4. PySAT verson: 0.1.6.dev11
	please check its installation at https://pysathq.github.io/installation.html
5. Cplex verson: 20.1.0.0
	please get an license and install it via https://www.ibm.com/products/ilog-cplex-optimization-studio

For the scripts that are used to obtain results in the figure and the table in our submission, we further need the following environments.
6. Python3 verson: 3.6.9
7. Some python3 packages including 'pandas', 'matplotlib' and 'seaborn'
	$ pip3 install pandas matplotlib seaborn

===== Part B =====
8. Clone this repository and make sure you are under the directory 'RTSS'
	$ git clone https://github.com/ReprodSuplem/RTSS.git
	$ cd RTSS/

We select and group some of simulated RTSS scenarios in groups of 100 as the instances for our experiments (mentioned in Section 5 of our submission) which are provided in the directory ./benchmarks. Each instance contains two corresponding files: one file (named 'xxx-xxx-externality.txt') has the information of demand and taxis; another file (named 'xxx-xxx-WNet.txt') has information of the road network (i.e., the time cost weight matrix of each taxi). 

Since the simulator we employed is not open source nor publicly available software, the reproducibility of the part of the simulation experiment is not included in this instruction. However, we attach the used road network data file as 'maebashi_4km_170_10.osm.gz', and provide a detailed description of the parameters included in the 'xxx-xxx-externality.txt' file as follows:
	a. 'nOfTaxi 10' indicates that the number of taxis is 10.
	b. 'newDemandSize 1' indicates that the number of passengers of currently occurring demand is 1.
	c. 'capacityOfEachTaxi 3 ... 3' indicates that each taxi's capacity is 3.
	d. 'noListOfCarried 3 0 ... 2' indicates that the current number of passengers on board of each taxi is 3, 0, ..., and 2, respectively.
	e. 'noListOfAcceptedPoint 1 3 ... 2' indicates that the number of the unfinished location point(s) of each taxi is 1, 3, ..., and 2, respectively.
	f. 'noListOfPickDrop -1 2 ... -2' indicates that the number of pick-up (positive value) or drop-off (negative value) passengers corresponding to each taxi's unfinished location points list is -1, 2, ..., and -2, respectively.
	g. 'currenTime 1510' indicates that the current time moment is 1510.
	h. 'deadlineList 1520 1603 ... 2021' indicates that the deadline corresponding to each taxi's unfinished location points list is 1520, 1603, ..., and 2021, respectively.
	i. 'deadlineOfNewDemand 1742 1988' indicates that the deadlines of the pick-up point and the drop-off point of new demand are 1742 and 1988 respectively.
	j. 'viaPointLists 1 2 ... 1' is obtained from the decoded previous optimal assignment (for the heuristic assumption solving). These lists correspond to each taxi's unfinished location points list in its route order respectively, based on the previous optimal assignment, where each number of these lists is the index (ranged from 1) of the unfinished location point in the correspondiong route order.

Our main efforts which include the implementation of both MaxSAT encoding and IP formulation are in the python source code files 'pySatFoRtss_hp1.py' and 'pySatFoRtss_hp2.py', where the former (resp. the latter) corresponds to the existing (resp. the proposed) Hamiltonian path constraint method.

9. Setup QMaxSAT solver with incremental approach
	$ ./build.sh

10. Encode the instances into their MaxSAT formulas and formulate the instances into their IP formulations? (note that in a general PC hardware environment, it would take tens of hours to complete the MaxSAT encodings and the IP formulations for all instances)
	$ ./insGen.sh

11. Solve the generated MaxSAT formulas and IP formulations (note that it is expected to take several days to complete solving all MaxSAT formulas and IP formulations)
	$ ./solveIns.sh [the absolute path of your cplex biniary file]
	for example, if you installed cplex in the default path, then run the following command:
	$ ./solveIns.sh /opt/ibm/ILOG/CPLEX_Studio201/cplex/bin/x86-64_linux/cplex

If you do not want to run step 10 and step 11 sequentially, the alternative way is that you can just run the following command:
	$ ./runAllExp.sh [the absolute path of your cplex biniary file]

===== Part C =====
All the experimental results are saved in the directory ./result, where the solving process for each instance under each solution method corresponds to a proprietary log file.

12. Experimental results can be statisticized by running the following command (the shell script call a provided python3 script ./logEvaluat.py)
	$ ./statisticize.sh

After tens of seconds, you will get a directory named 'statistics' inside the directory ./result. In the directory ./result/statistics, the file 'allLogInfo.csv' lists key informations corresponding to all log files, and the file 'table1.txt' and the file 'figure1.png' correspond to Table 2 and Figure 2 in our submission, respectively.


We hope that this instruction will help you understand and reproduce our experiments. Finally, we hereby declare that all the source code required to perform the experiments will be made publicly available after the publication of the paper, with a license allowing free use for research purposes.










