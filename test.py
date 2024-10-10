import argparse
import os
import configparser as cp
from cachesim import MemSim
from cache import Cache
if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-c', metavar='Config file', type=str,
                        default="./scale.cfg",
                        help="Path to the config file"
                        )

    args = parser.parse_args()
    config = args.c
    if not os.path.exists(config):
        print("ERROR: Config file not found") 
        print("Input file:" + config)
        print('Exiting')
        exit()
    else: 
        config_file = config

    config = cp.ConfigParser()
    config.read(config_file)

    section = 'scratchpad_architecture_presets'

    bank_num = int(config.get(section, 'Bank Num'))
    bank_row = int(config.get(section, 'Bank Row per bank'))
    dim = int(config.get(section, 'Dim'))
    data_size = int(config.get(section, 'Data Size'))

    section = 'l1cache_architecture_presets'
    l1_size = int(config.get(section, 'Total Size'))
    l1_cacheline_size = int(config.get(section, 'Cacheline Size'))
    l1_way = int(config.get(section, 'Way of Associativity'))
    l1_replacement = (config.get(section, 'Way of Replacement'))
    l1_data_size   = int(config.get(section, 'Data Size'))

    section = 'l2cache_architecture_presets'
    l2_size = int(config.get(section, 'Total Size'))
    l2_cacheline_size = int(config.get(section, 'Cacheline Size'))
    l2_way = int(config.get(section, 'Way of Associativity'))
    l2_replacement = (config.get(section, 'Way of Replacement'))
    l2_data_size   = int(config.get(section, 'Data Size'))


    sim = MemSim()
    sim.set_params(bank_num,bank_row,dim,data_size,l1_way,l1_size, l1_cacheline_size,l1_replacement,32,l1_data_size,l1_way,l1_size, l1_cacheline_size,l1_replacement,l1_data_size)
    for i in range(0, 0x10000, 0x4):
        sim.cache_read(i)
    for i in range(0, 0x10000, 0x4):
        sim.cache_read(i)
    # sim.cache_read(0)
    # sim.cache_read(0)
    # sim.cache_read(0x4,0,0,0)
    # sim.cache_read(0x8,0,0,0)
    # sim.cache_read(0xc,0,0,0)
    # sim.cache_read(0x14,0,0,0)
    # sim.cache_read(0,0,0,0)

    sim.print_info()
