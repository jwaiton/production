#!/bin/bash
#SBATCH --partition={partition}
#SBATCH --qos=regular
#SBATCH --job-name={job_name}
#SBATCH --time={time}
#SBATCH --array=0-{num_of_configs}
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task={cpus_per_task}
#SBATCH --mem={mem}

#SBATCH --error={job_path}/errors_{tag}/%x-%j-%A-%a.err
#SBATCH --output={job_path}/output_{tag}/%x-%j-%A-%a.out
#SBATCH --log={job_path}/log_{tag}/%x-%j-%A-%a.log

#SBATCH --mail-user=john.waiton@postgrad.manchester.ac.uk
#SBATCH --mail-type=ALL

{init_ic}

configs=({config_path}/*.conf)
cfg="${configs[$SLURM_ARRAY_TASK_ID]}"

if [[ -z "$cfg" ]]; then
    echo "No config for task ID $SLURM_ARRAY_TASK_ID"
    exit 1
fi

echo "[$SLURM_ARRAY_TASK_ID] Running $cfg"
city {city} "$cfg"
