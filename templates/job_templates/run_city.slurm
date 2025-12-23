#!/bin/bash
#SBATCH --qos=regular
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --ntasks-per-node=1

#SBATCH --mail-user=john.waiton@postgrad.manchester.ac.uk
#SBATCH --mail-type=ALL

# -------- Runtime parameters (from sbatch) --------
CONFIG_PATH=${CONFIG_PATH:?}
CITY=${CITY:?}

# -------- Apply SLURM settings dynamically --------
#SBATCH --partition=${PARTITION}
#SBATCH --job-name=${JOB_NAME}
#SBATCH --time=${TIME}
#SBATCH --cpus-per-task=${CPUS}
#SBATCH --mem=${MEM}

#SBATCH --error=%x-%A-%a.err
#SBATCH --output=%x-%A-%a.out


# -------- Load environment --------
: "${INIT_ENV:?}"

source "$INIT_ENV"
# -------- Pick config --------
configs=(${CONFIG_PATH}/*.conf)
cfg="${configs[$SLURM_ARRAY_TASK_ID]}"

echo "[$SLURM_ARRAY_TASK_ID] Running $cfg"
city "$CITY" "$cfg"

