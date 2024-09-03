import os
import math
from lru import LRU
class CacheSim:
    def __init__(self):
        self.way = 2
        self.line_size  = 16 #byte
        self.total_size = 8 #Kb     
        self.addr_size = 32 #bit
    
    def set_params(self,
                   way,
                   total_size, line_size,
                   replacement,addr_size):
        assert line_size%2==0,"Cacheline size is unalign!"
        assert total_size%2==0,"Cacheline size is unalign!"

        self.way = way #way=0-> 全相连 way=-1 直接相连 way>1 组相联 
        self.line_size  = line_size #byte
        self.total_size = total_size #Kb
        self.addr_size   = addr_size

        if(way<1):
            self.index_num   = int(total_size*1024/line_size)
        else:
            self.index_num   = int(total_size*1024/way/line_size)

        index_bit   = int(math.log2(self.index_num)) 
        tag_bit     = int(self.addr_size-math.log2(self.line_size)-index_bit) 
        offset_bit  = addr_size-index_bit-tag_bit
        if replacement=="PLRU":
            self.sim = LRU()
            self.sim.set_params(way,tag_bit,index_bit,offset_bit,self.index_num)
        


        


    def cache_read(self,addr,size,prefetch_size):
        return  self.sim.read(addr) 