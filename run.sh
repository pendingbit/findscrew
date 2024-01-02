#!/bin/bash

path="/home/joey/Desktop/output/"$(date "+%Y_%m_%d_%H_%M_%S")
#path="/home/joey/Desktop/output/test"

a=0
logpath=$path"/"
while [ -d "$logpath" ]
	do
		let a++
		logpath=$path"("$a")/"
	done
echo $logpath

mkdir -p $logpath

logfile=$logpath"stand.log"
errfile=$logpath"error.log"
touch $logfile
touch $errfile

python3 /home/joey/gitee/findscrew/my_screw_detect.py $logpath 1>$logfile 2>$errfile
