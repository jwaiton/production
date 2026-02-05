
echo "Initialise conda"

# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('/home/halmazan/miniconda/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/home/halmazan/miniconda/etc/profile.d/conda.sh" ]; then
        . "/home/halmazan/miniconda/etc/profile.d/conda.sh"
    else
        export PATH="/home/halmazan/miniconda/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda initialize <<<
#
echo "Config produced, initialising IC"
# Initialise IC
conda init bash
source /scratch/halmazan/NEXT/IC_master/init_IC.sh
conda activate IC-3.8-2024-06-08
