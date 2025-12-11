# set directory path to variable
export PROD_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
echo "PROD: $PROD_DIR"

# setup environment variables
export PATH=$PROD_DIR/bin:$PATH

echo "Initialised production"
