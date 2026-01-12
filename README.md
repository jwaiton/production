Repo for all the productions applied on slurm based systems.

Should be developed to be as maintainable, improvable, modifiable, extendable, etc.

Lets try our best!



In each *job* we have *runners* as shown below

IC-beersheba:
    params_0: '5 * pes'
    params_1: 123.456
    params_2: 1234
    params_3:
        params_3a: "'x'"
        params_3b: x

Each runner schedules a bunch of slurm or condor `jobs`, which we will call *sub-jobs*, these are different from our 'jobs'.
