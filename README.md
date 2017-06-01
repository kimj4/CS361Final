Tested on a Ubuntu 17 VM on VirtualBox

pull git repo

install Boost
- download boost
	- https://dl.bintray.com/boostorg/release/1.64.0/source/:boost_1_64_0.tar.gz
- unpack into some directory
- get required libraries
	- sudo apt-get install build-essential g++ python-dev autotools-dev libicu-dev build-essential libbz2-dev
- cd into boost directory
- ./bootstrap.sh --prefix=/usr/local
- n=`cat /proc/cpuinfo | grep "cpu cores" | uniq | awk '{print $NF}'`
- sudo ./b2 --with=all -j $n install
- sudo sh -c 'echo "/usr/local/lib" >> /etc/ld.so.conf.d/local.conf'
- sudo ldconfig

install MultiNEAT
- CS361Final/MultiNEAT
- sudo python setup.py install
	- needs setuptools
		- pip install setuptools
			- to get pip, sudo apt-get install python-pip

build connect four
- ./cbuild.sh
	- to install clang++, sudo apt-get install clang

need concurrent futures
pip install futures

run program
- go into hcf.py, and change sys.path.insert(0, '/path/to/directory/that/contains/MultiNEAT/')
- python hcf.py
