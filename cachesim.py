import os
import math
from lru import LRU
##################################

#########DRAM  Model##############
class DRAM:
    def read(self,addr,mask):
        return 0
##################################
class CacheSim:
    def __init__(self):
        self.way = 2
        self.line_size  = 16 #byte
        self.total_size = 8 #Kb     
        self.addr_size = 32 #bit
        self.dram      = []
        self.hit_latency = 1
        self.dram      = DRAM()
    def set_params(self,
                   way,
                   total_size, line_size,
                   replacement,addr_size,data_size):
        assert line_size%2==0,"Cacheline size is unalign!"
        assert total_size%2==0,"Cacheline size is unalign!"
        assert (data_size>>3)<=line_size, "Data size is too big,it must less than 64bits"
        assert replacement=="PLRU"

        self.way = way #way=0-> 全相连 way=-1 直接相连 way>1 组相联 
        self.line_size  = line_size #byte
        self.total_size = total_size #Kb
        self.addr_size   = addr_size
        self.data_size = data_size#bit
        
        if(way<1):
            self.index_num   = int(total_size*1024/line_size)
        else:
            self.index_num   = int(total_size*1024/way/line_size)

        self.index_bit   = int(math.log2(self.index_num)) 
        self.tag_bit     = int(self.addr_size-math.log2(self.line_size)-self.index_bit) 
        self.offset_bit  = addr_size-self.index_bit-self.tag_bit
        data_num = int((2**self.offset_bit)/(data_size/8))
        if replacement=="PLRU":
            self.sim = LRU()
            self.sim.set_params(way,self.index_num,data_num)
        


        


    def cache_read(self,addr,size,prefetch_size,prefetch_addr):


        assert size <= self.line_size
        assert prefetch_size<= self.line_size
        tag     = addr>>(self.offset_bit+self.index_bit)
        index   = (addr>>self.offset_bit)&((1<<(self.index_bit))-1)
        temp = int ((addr&((1<<(self.offset_bit))-1)))
        data_region = int(temp/(self.data_size/8))
        # assert addr
        data,hit = self.sim.read(tag,index,data_region,0)
        if not hit:
            data = self.dram.read(addr,0)
        return  data

    def cache_write(self,addr,size,data):


        tag     = addr>>(self.offset_bit+self.index_bit)
        index   = (addr>>self.offset_bit)&((1<<(self.index_bit))-1)
        temp = int ((addr&((1<<(self.offset_bit))-1)))
        data_region = int(temp/(self.data_size/8))
        # assert addr
        self.sim.write(tag,index,0,data,data_region)
        # if not hit:
        #     data = self.dram.write(addr,0)
        # return  data