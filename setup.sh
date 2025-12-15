#!/usr/bin/env bash


function install_mamba {
    "${SHELL}" <(curl -L https://micro.mamba.pm/install.sh)
}		


PYTHON_VERSION='3.12'
DATE='15-25'
# set env name
PROD_ENV_NAME=PROD-${PYTHON_VERSION}-${DATE}


# set directory path to variable
export PROD_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
echo "PROD: $PROD_DIR"

# setup environment variables
export PATH=$PROD_DIR/bin:$PATH

# initialise micromamba if possible
if micromamba --version ; then
	echo Initialising Micromamba...
else
	echo "No micromamba installation detected, installing micromamba."
	echo 'Download micromamba? Select [1/2]:'
	select yn in Yes No; do
		case $yn in
			Yes ) install_mamba; break;;
			No ) echo "micromamba activation aborted"; return;;
		esac
	done
fi

# If micromamba environment exists, activate it. Otherwise create it
if ! (micromamba env list | grep ${PROD_ENV_NAME}) >> /dev/null
then
	echo "Couldn't find environment, creating environment..."
	micromamba env create -f prod_environment.yml
fi

echo "Initialised production"

micromamba activate ${PROD_ENV_NAME}
cd ${PROD_DIR}
