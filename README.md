Tested on a Ubuntu 17 VM on VirtualBox

pull git repo

install Boost
- download boost
	- https://dl.bintray.com/boostorg/release/1.64.0/source/:boost_1_64_0.tar.gz
- unpack into some directory
- get required libraries
```shell
	sudo apt-get install build-essential g++ python-dev autotools-dev libicu-dev build-essential libbz2-dev
```
- cd into boost directory
```shell
./bootstrap.sh --prefix=/usr/local
n=`cat /proc/cpuinfo | grep "cpu cores" | uniq | awk '{print $NF}'`
sudo ./b2 --with=all -j $n install
sudo sh -c 'echo "/usr/local/lib" >> /etc/ld.so.conf.d/local.conf'
sudo ldconfig
```

install MultiNEAT
- cd into CS361Final/MultiNEAT
```shell
sudo python setup.py install
```
if you need setuptools:
```shell
pip install setuptools
```

if you need pip:
```shell
sudo apt-get install python-pip
```

build connect four
```shell
./cbuild.sh
```

if you need clang++:
```shell
sudo apt-get install clang
```

if you need concurrent.futures
```shell
pip install futures
```

run program
go into hcf.py, and change sys.path.insert(0, '/path/to/directory/that/contains/MultiNEAT/')

and then:
```shell
python hcf.py output.txt 0 0 0 genome.txt 19
```
arguments:
> file to log to
> enable/disable symmetry
> enable/disable verbose printing
> enable/disable HyperNEAT
> file to save population to
> generation at which to save population

To play games on saved populations:
```shell
python playGame.py Players/NEAT_No_Symmetry_genome.txt 0 0 0 0
```
arguments:
> file where player list is saved
> index of player in list to play
> 1 if you want to go first, 0 if you don't
> 1 if player used symmetry 0 if not
> 1 if player used HyperNEAT 0 if NEAT
