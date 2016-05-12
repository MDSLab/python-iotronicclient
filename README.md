# python-iotronicclient
Python client library for the IoTronic API

After cloning the git repository you have to install some python packages which are:
* python-dev
* python-oslo-utils
* python-oslo-i18n
* python-keystoneauth1

The first package can be easily installed using any OS-depending software package managers (e.g.: apt-get, dpkg, yum, etc...). The other ones will be installed using ```pip``` (https://pypi.python.org/pypi/pip) from inside the git repository already downloaded by launching: ```sudo pip install -r requirements.txt```

Once you have the previous packages installed you have to launch: ```sudo ./build.sh``` and then test the iotronicclient for example by using the python shell.
