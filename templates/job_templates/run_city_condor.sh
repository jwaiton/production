CONFIG_PATH=$1
ENV_DIR=$2
CITY=$3
echo "Config path: ${CONFIG_PATH}"
echo "Sourcing IC from ${ENV_DIR}"

source ${ENV_DIR}

echo "Running IC with city ${CITY}"
city ${CITY} ${CONFIG_PATH}
