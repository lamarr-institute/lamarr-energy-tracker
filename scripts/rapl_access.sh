#!/usr/bin/env bash

#set -x
#set -v

sudo su -c 'sh -s' <<EOF
chmod 444 /sys/class/powercap/intel-rapl/intel-rapl:0/energy_uj
chmod 444 /sys/class/powercap/intel-rapl/intel-rapl:0/max_energy_range_uj
chmod 444 /sys/class/powercap/intel-rapl/intel-rapl:0/intel-rapl:0:0/energy_uj
chmod 444 /sys/class/powercap/intel-rapl/intel-rapl:0/intel-rapl:0:0/max_energy_range_uj
chmod 444 /sys/class/powercap/intel-rapl/intel-rapl:0/intel-rapl:0:1/energy_uj
chmod 444 /sys/class/powercap/intel-rapl/intel-rapl:0/intel-rapl:0:1/max_energy_range_uj

chmod 444 /sys/class/powercap/intel-rapl/intel-rapl:1/energy_uj
chmod 444 /sys/class/powercap/intel-rapl/intel-rapl:1/max_energy_range_uj
chmod 444 /sys/class/powercap/intel-rapl/intel-rapl:0/intel-rapl:0:2/energy_uj
chmod 444 /sys/class/powercap/intel-rapl/intel-rapl:0/intel-rapl:0:2/max_energy_range_uj
EOF