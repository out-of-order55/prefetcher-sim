import os
import math
from lru import LRU
from cache import Cache,DRAM
##################################
#TODO: 
#########DRAM  Model##############

class L1Cache(Cache):
    def __init__(self,
                   way,
                   total_size, line_size,
                   replacement,addr_size,data_size,isllc):
        super().__init__(way,
                   total_size, line_size,
                   replacement,addr_size,data_size,isllc)
        self.backing_mem = None
    
class Scratchpad:
    def __init__(self,bank_num,bank_row,dim,data_size):
        self.bank_num = bank_num
        self.bank_row =bank_row 
        self.dim=dim
        self.data_size = data_size
        self.backing_mem = None
        
    def read(self,addr):
        req_num = int(self.dim*(self.data_size/8)/self.backing_mem.line_size)#需要去读的cacheline的数目
        data_num = int(self.backing_mem.line_size/self.backing_mem.data_size)

        rdata = [0 for _ in range(req_num*(data_num))]
        for i in range(req_num):
            data = self.backing_mem.read_line(addr)
            for j  in range(data_num):
                rdata[j+i*data_num] = data[j]
        return rdata

    def write(self,addr,data):
        req_num = int(self.dim*(self.data_size/8)/self.backing_mem.line_size)#需要去写的cacheline的数目
        data_num = int(self.backing_mem.line_size/self.backing_mem.data_size)

        wdata = [[0 for _ in range(data_num)] for _ in range(req_num)]


        for i in range(req_num):
            for j  in range(data_num):
                wdata[i][j] = data[j+i*data_num]
        for i in range(req_num):
            self.backing_mem.write_line(wdata[i],addr)

class L2Cache(Cache):
    def __init__(self,
                   way,
                   total_size, line_size,
                   replacement,addr_size,data_size,isllc):
        super().__init__(way,
                   total_size, line_size,
                   replacement,addr_size,data_size,isllc)
        self.backing_mem = None


    def read_line(self,addr):
        # print("read_line")
        tag     = addr>>(self.offset_bit+self.index_bit)
        index   = (addr>>self.offset_bit)&((1<<(self.index_bit))-1)
        hit,row = self.check_hit(tag,index)
        if hit:
            self.hit +=1
            self.replacement.promotion(row)
            return self.data[row][index]
        else:
            self.miss+=1
            way=self.replacement.eviction()
            self.replacement.insert(way)
            rep_tag  = self.tagv[way][index]
            rep_addr = (rep_tag<<(self.offset_bit+self.index_bit)) + index<<self.offset_bit
            self.tagv[way][index]=tag
            data = self.backing_mem.read_line(addr)
            self.data[way][index] = data 
            return data


    def write_line(self,addr,data):
        
        tag     = addr>>(self.offset_bit+self.index_bit)
        index   = (addr>>self.offset_bit)&((1<<(self.index_bit))-1)
        hit,row = self.check_hit(tag,index)
        if hit:
            self.hit +=1
            self.replacement.promotion(row)

        else:
            self.miss+=1
            way=self.replacement.eviction()
            self.replacement.insert(way)
            rep_tag  = self.tagv[way][index]
            rep_addr = (rep_tag<<(self.offset_bit+self.index_bit)) + index<<self.offset_bit
            self.tagv[way][index]=tag
            self.backing_mem.write_line(addr)

    

##################################
class MemSim:
    def __init__(self):
        # self.way = 2
        # self.line_size  = 16 #byte
        # self.total_size = 8 #Kb     
        # self.addr_size = 32 #bit
        self.hit_latency = 1

        # self.l1cache   = L1Cache()
        # self.l2cache   = L2Cache()
    def set_params(self,bank_num,bank_row,dim,data_size,
                   l1_way,l1_total_size, l1_line_size,l1_replacement,l1_addr_size,l1_data_size,
                   l2_way,l2_total_size, l2_line_size,l2_replacement,l2_data_size):
        assert l1_line_size%2==0,"Cacheline size is unalign!"
        assert l1_total_size%2==0,"Cacheline size is unalign!"
        assert (l1_data_size>>3)<=l1_line_size, "Data size is too big,it must less than 64bits"
        assert l1_replacement=="PLRU"

##################init####################
        self.dram = DRAM(int(l1_line_size/(l1_data_size/8)))
        self.scratchpad = Scratchpad(bank_num,bank_row,dim,data_size)
        self.l2cache=L2Cache(l2_way,l2_total_size, l2_line_size,l2_replacement,l1_addr_size,l2_data_size,True)
        self.l1cache=L1Cache(l1_way,l1_total_size, l1_line_size,l1_replacement,l1_addr_size,l1_data_size,False)
        
        self.l2cache.backing_mem = self.dram 
        self.l1cache.backing_mem = self.l2cache    
        self.scratchpad.backing_mem = self.l2cache  
        # self.l1_way         = l1_way #way=0-> 全相连 way=-1 直接相连 way>1 组相联 
        # self.l1_line_size   = l1_line_size #byte
        # self.l1_total_size  = l1_total_size #Kb
        # self.l1_addr_size   = l1_addr_size
        # self.l1_data_size   = l1_data_size#bit
        
        # if(l1_way<1):
        #     self.l1_index_num   = int(l1_total_size*1024/l1_line_size)
        # else:
        #     self.l1_index_num   = int(l1_total_size*1024/l1_way/l1_line_size)

        # self.l1_index_bit   = int(math.log2(self.l1_index_num)) 
        # self.l1_tag_bit     = int(self.l1_addr_size-math.log2(self.l1_line_size)-self.l1_index_bit) 
        # self.l1_offset_bit  = l1_addr_size-self.l1_index_bit-self.l1_tag_bit


    def cache_read(self,addr):

        data = self.l1cache.read(addr)
        return  data
    def cache_write(self,addr,data):
        self.l1cache.write(addr,data)

    def spm_read(self,addr):
        # data = self.l1cache.read(addr)
        # return  data
        return self.scratchpad.read(addr)
    def spm_write(self,addr,data):
        # self.l1cache.write(addr,data)
        self.scratchpad.write(addr,data)

    def print_info(self):
        l1_miss,l1_hit=self.l1cache.print_info()
        l2_miss,l2_hit=self.l2cache.print_info()
        l1_miss_rate = l1_miss/(l1_miss+l1_hit+1)
        l2_miss_rate = l2_miss/(l2_hit+l2_miss+1)
        total_miss_rate = l1_miss_rate*l2_miss_rate    
        print(f'L1Cache hit {l1_hit}  miss {l1_miss} miss rate {l1_miss_rate}')
        print(f'L2Cache hit {l2_hit}  miss {l2_miss} miss rate {l2_miss_rate}')
        print(f'Total miss rate {total_miss_rate}')
    # def cache_write(self,addr,size,data):


    #     tag     = addr>>(self.offset_bit+self.index_bit)
    #     index   = (addr>>self.offset_bit)&((1<<(self.index_bit))-1)
    #     temp = int ((addr&((1<<(self.offset_bit))-1)))
    #     data_region = int(temp/(self.data_size/8))
    #     # assert addr
    #     self.l1cache.write(tag,index,0,data,data_region)
    #     # if not hit:
    #     #     data = self.dram.write(addr,0)
    #     # return  data