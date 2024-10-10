import os
import math

from lru import LRU

class DRAM:
    def __init__(self,data_region):
        self.data_region = data_region
        self.data = [0 for _ in range(self.data_region)]
    def read_line(self,addr):
        return self.data
    def write_line(self,addr,data):
        None
    def read(self,addr):
        return 0
    
#move the tagv and data to cache ,replacement only need to have update and find the replace way



##################################
class Cache:
    def __init__(self,way,
                   total_size, line_size,
                   replacement,addr_size,data_size,isllc):
        self.way = way
        self.line_size  = line_size #byte
        self.total_size = total_size #Kb     
        self.addr_size = addr_size #bit
        self.data_size = data_size
        self.hit_latency = 1
        self.hit=0
        self.miss=0
        self.isllc = isllc 
        self.backing_mem = None
        if(way<1):
            self.index_num   = int(total_size*1024/line_size)
        else:
            self.index_num   = int(total_size*1024/way/line_size)

        self.index_bit   = int(math.log2(self.index_num)) 
        self.tag_bit     = int(self.addr_size-math.log2(self.line_size)-self.index_bit) 
        self.offset_bit  = addr_size-self.index_bit-self.tag_bit
        data_num = int((2**self.offset_bit)/(data_size/8))

        self.tagv = [[ 0xffffffff for _ in range(self.index_num)] for _ in range(way)]
        self.dirty = [[ 0 for _ in range(self.index_num)] for _ in range(way)]
        self.data = [[[0  for _ in range(data_num)] for _ in range(self.index_num)] for _ in range(way)]

        if replacement=="PLRU":
            self.replacement = LRU()
            self.replacement.set_params(way,self.index_num,data_num)
    # def set_params(self,
    #                way,
    #                total_size, line_size,
    #                replacement,addr_size,data_size,isllc):
    #     assert line_size%2==0,"Cacheline size is unalign!"
    #     assert total_size%2==0,"Cacheline size is unalign!"
    #     assert (data_size>>3)<=line_size, "Data size is too big,it must less than 64bits"
    #     assert replacement=="PLRU"
    #     self.isllc = isllc
    #     self.way = way #way=0-> 全相连 way=-1 直接相连 way>1 组相联 
    #     self.line_size  = line_size #byte
    #     self.total_size = total_size #Kb
    #     self.addr_size   = addr_size
    #     self.data_size = data_size#bit
    #     # self.backing_mem = backing_mem

        


        

    def check_hit(self,tag,index):
        for row_index,row in enumerate(self.tagv):
            if tag==row[index]:
                return True,row_index 
        return False,-1

    def read(self,addr):
        print("read")
        tag     = addr>>(self.offset_bit+self.index_bit)
        index   = (addr>>self.offset_bit)&((1<<(self.index_bit))-1)
        temp = int ((addr&((1<<(self.offset_bit))-1)))
        data_region = int(temp/(self.data_size/8))
        hit,row = self.check_hit(tag,index)
        if hit:
            self.hit +=1
            self.replacement.promotion(row)
            return False,self.data[row][index][data_region]
        else:
            self.miss+=1
            way=self.replacement.eviction()
            self.replacement.insert(way)
            self.tagv[way][index]=tag
            if self.dirty[way][index]:
                data =  self.data[way][index]
                rep_tag  = self.tagv[way][index]
                rep_addr = (rep_tag<<(self.offset_bit+self.index_bit)) + index<<self.offset_bit
                self.backing_mem.write_line(rep_addr,data)
                self.dirty[way][index] = False
            miss,data = self.backing_mem.read_line(addr)
            self.data[way][index] = data
            return miss,data[data_region]
    #write hit ,将数据写入l1cache,但不写入l2cache,
    #write miss,找到被替换的行,假设有脏位,那么写入下级存储,此时l2cache绝对不会miss(inclusive),假设没有脏位,从l2读出数据,如果数据miss,则将数据放到l1和l2中
    def write(self,addr,data):


        tag     = addr>>(self.offset_bit+self.index_bit)
        index   = (addr>>self.offset_bit)&((1<<(self.index_bit))-1)
        temp = int ((addr&((1<<(self.offset_bit))-1)))
        data_region = int(temp/(self.data_size/8))
        hit, row = self.check_hit(tag,index)
        
        if hit :
            self.hit+=1
            self.data[row][index][data_region] =  data
            self.dirty[row][index] = True
            self.replacement.promotion(row)
            return False
        else :
            self.miss +=1
            way = self.replacement.eviction()
            if self.dirty[way][index]:
                wdata =  self.data[way][index]
                rep_tag  = self.tagv[way][index]
                rep_addr = (rep_tag<<(self.offset_bit+self.index_bit)) + index<<self.offset_bit
                self.backing_mem.write_line(rep_addr,wdata)

            miss,self.data[way][index] = self.read_line(addr)
            self.data[way][index][data_region] =data
            self.replacement.insert(way)
            self.tagv[way][index] = tag   
            return miss


    def print_info(self):
        return self.miss,self.hit