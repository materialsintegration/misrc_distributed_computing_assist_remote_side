#!/bin/bash
#QSUB2 queue qM004
#QSUB2 core 48
#QSUB2 mpi 1
#QSUB2 smp 1
#QSUB2 wtime 48:00:00
#PBS -N frontISTRx48x1

. ~/local/intel/oneapi/setvars.sh --force
cd $PBS_O_WORKDIR
time ~/local/intel/oneapi/mpi/latest/bin/mpirun -np 48 fistr1 -t 1 > fistr_qsub.log 2>&1

