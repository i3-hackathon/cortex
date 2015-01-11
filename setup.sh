sudo apt-get update
sudo apt-get upgrade
sudo apt-get install python-pip python-dev build-essential python-numpy python-matplotlib
sudo pip install requests flake8 flask

# Setup R dependencies
# sudo apt-get install build-dep r-base
sudo add-apt-repository ppa:marutter/rrutter
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install r-base r-base-dev

sudo pip install rpy2

# Manual step for now
sudo R
# install.packages("changepoint")
# q()

# Front End
sudo apt-get install nodejs npm