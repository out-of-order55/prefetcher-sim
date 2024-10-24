import os
import math

from lru import LRU
from rand import RANDOM
from srrip import SRRIP
from brrip import BRRIP
from drrip import DRRIP
class DRAM:
    def __init__(self,data_num):
        self.data_num = data_num
        print(f"Dram data num{data_num}")
        self.data = [0 for _ in range(self.data_num)]
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

        if(way==-1):
            self.index_num   = int(total_size*1024/line_size)
            self.way = self.index_num
            self.full=True
        else:
            self.index_num   = int(total_size*1024/way/line_size)
            self.full=False

        self.index_bit   = int(math.log2(self.index_num)) 
        self.tag_bit     = int(self.addr_size-math.log2(self.line_size)-self.index_bit) 
        self.offset_bit  = addr_size-self.index_bit-self.tag_bit
        self.data_num = int((2**self.offset_bit)/(data_size/8))
        print(f"way {self.way}")
        if self.full:
            
            self.tagv = [ 0xffffffff  for _ in range(self.way)]
            self.dirty = [0  for _ in range(self.way)]
            self.data = [[0  for _ in range(self.data_num)]  for _ in range(self.way)]
        else:
            self.tagv = [[ 0xffffffff for _ in range(self.index_num)] for _ in range(way)]
            self.dirty = [[ 0 for _ in range(self.index_num)] for _ in range(way)]
            self.data = [[[0  for _ in range(self.data_num)] for _ in range(self.index_num)] for _ in range(way)]
        print(replacement)
        if replacement=="PLRU":
            self.replacement = LRU()
            self.replacement.set_params(self.way,self.index_num,self.data_num)
        elif replacement=="RANDOM":
            # print("Random")
            self.replacement = RANDOM()
            self.replacement.set_params(self.way,self.index_num,self.data_num)
        elif replacement=="SRRIP":
            self.replacement = SRRIP()
            self.replacement.set_params(self.way,self.index_num,self.data_num)
        elif replacement=="BRRIP":
            self.replacement = BRRIP()
            self.replacement.set_params(self.way,self.index_num,self.data_num)
        elif replacement=="DRRIP":
            self.replacement = DRRIP()
            self.replacement.set_params(self.way,self.index_num,self.data_num)
        
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

        

#can't used in llc
    def read_line(self,addr):

        if self.isllc:
            tag     = addr>>(self.offset_bit+self.index_bit)
            index   = (addr>>self.offset_bit)&((1<<(self.index_bit))-1)
            hit,row = self.check_hit(tag,index)
            if hit:
                self.hit +=1
                self.replacement.promotion(index,row)
                return self.data[row][index]
            else:
                self.miss+=1
                way=self.replacement.eviction(index)
                self.replacement.insert(index,way)
                rep_tag  = self.tagv[way][index]
                rep_addr = (rep_tag<<(self.offset_bit+self.index_bit)) + index<<self.offset_bit
                self.tagv[way][index]=tag
                data = self.backing_mem.read_line(addr)
                self.data[way][index] = data 
                return data
        else:
            raddr = (addr>>self.offset_bit)<<self.offset_bit
            stride = self.backing_mem.data_size/8
            data_num = int(self.line_size/(self.backing_mem.data_size/8))#下级数据需要访问多少次才能凑齐本级一行
            data = [0 for _ in range(data_num)]
            data_region = int(self.line_size*8/self.data_size)
            data_sc = int(self.backing_mem.data_size/self.data_size)#一个下级data_size等于多少个本级data_size
            for i in range(data_num):
                data[i] = self.backing_mem.read(raddr+i*stride)
            rdata = [0 for _ in range(data_region)]
            mask = (1<<self.data_size)-1
            for i in range(data_region):
                region_point = int(i%data_sc)#此次循环应该操作下级传来的数据的哪几位 
                rdata[i] = (data[int(i/data_sc)]&(mask<<(self.data_size*region_point)))>>(self.data_size*region_point)#将下级存储的数据分裂
            return rdata
    def write_line(self,addr,data):
        if self.isllc:
            tag     = addr>>(self.offset_bit+self.index_bit)
            index   = (addr>>self.offset_bit)&((1<<(self.index_bit))-1)
            hit,row = self.check_hit(tag,index)
            if hit:
                self.hit +=1
                self.replacement.promotion(index,row)

            else:
                self.miss+=1
                way=self.replacement.eviction(index)
                self.replacement.insert(index,way)
                rep_tag  = self.tagv[way][index]
                rep_addr = (rep_tag<<(self.offset_bit+self.index_bit)) + index<<self.offset_bit
                self.tagv[way][index]=tag
                self.backing_mem.write_line(addr,data)
        else:
            waddr = (addr>>self.offset_bit)<<self.offset_bit
            stride = self.backing_mem.data_size/8
            data_region = int(self.line_size*8/self.data_size)
            data_num = int(self.line_size/(self.backing_mem.data_size/8))
            wdata = [0 for _ in range(data_num)]
            data_sc = int(self.backing_mem.data_size/self.data_size)#一个下级data_size等于多少个本级data_size
            #两者data_size一样,相当于地址步长一样,可以直接write
            if self.data_size==self.backing_mem.data_size:
                for i in range(data_region):
                    self.write(waddr+i*stride,data[i])
            else :
                assert self.data_size <= self.backing_mem.data_size
                for i in range(data_num):
                    for j in range(data_sc):
                        data[j]   = (data[j]<<(self.data_size*j))
                        wdata[i] += data[j]
                    self.write(waddr+i*stride,wdata[i])

    def check_hit(self,tag,index):
        if self.full:
            for row_index,val in enumerate(self.tagv):
                if tag==val:
                    return True,row_index
        else:
            for row_index,row in enumerate(self.tagv):
                if tag==row[index]:
                    return True,row_index 
        return False,-1

    def read(self,addr):
        if self.full:
            tag     = addr>>(self.offset_bit)
            index   = (addr>>self.offset_bit)&((1<<(self.index_bit))-1)
        else:
            tag     = addr>>(self.offset_bit+self.index_bit)
            index   = (addr>>self.offset_bit)&((1<<(self.index_bit))-1)
        temp = int ((addr&((1<<(self.offset_bit))-1)))
        data_region = int(temp/(self.data_size/8))
        hit,row = self.check_hit(tag,index)

        # print(f"read addr {addr} row {row} index {index} data_region {data_region} data_num {self.data_num}")
        # print(self.data[0][0][2])
        if hit:
            self.hit +=1
            self.replacement.promotion(index,row)
            if self.full:
                return self.data[row][data_region]
            else:
                return self.data[row][index][data_region]
        else:
            self.miss+=1
            way=self.replacement.eviction(index)
            self.replacement.insert(index,way)
            if self.full:
                self.tagv[way]=tag
                
                if self.dirty[way]:
                    data =  self.data[way]
                    rep_tag  = self.tagv[way]
                    rep_addr = (rep_tag<<(self.offset_bit))
                    self.backing_mem.write_line(rep_addr,data)
                    self.dirty[way] = False

                #先查询下一级是否hit,
                bk_tag   = addr>>(self.backing_mem.offset_bit+self.backing_mem.index_bit)
                bk_index = (addr>>self.backing_mem.offset_bit)&((1<<(self.backing_mem.index_bit))-1)
                bk_hit,bk_row = self.backing_mem.check_hit(bk_tag,bk_index)

                # 如果miss,进入l2cache line 替换阶段,此时将会检查l2替换的line所对应的l1 line 是否dirty
                #############invaild l1cache line logic################
                if (~bk_hit):
                    bk_rep_way = self.backing_mem.replacement.eviction(bk_index)
                    bk_rep_tag   = self.backing_mem.tagv[bk_rep_way][bk_index]
                    bk_rep_addr = (bk_rep_tag<<(self.backing_mem.offset_bit+self.backing_mem.index_bit)) + index<<self.backing_mem.offset_bit 
                    #将下级cache索引改为本级的索引
                    bk2ts_tag = bk_rep_addr>>(self.offset_bit)
                    bk2ts_index   = (bk_rep_addr>>self.offset_bit)&((1<<(self.index_bit))-1)                
                    hit,row = self.check_hit(bk2ts_tag,bk2ts_index)
                    if self.dirty[row]:
                        bk_dirty_data = self.data[row]
                        self.backing_mem.write_line(bk_rep_addr,bk_dirty_data)
                        self.dirty[row] = False
                    self.tagv[row]=0xffffffff
                ######################################
                data = self.backing_mem.read_line(addr)
                self.data[way] = data
                return data[data_region]
            else:
                self.tagv[way][index]=tag
                
                if self.dirty[way][index]:
                    data =  self.data[way][index]
                    rep_tag  = self.tagv[way][index]
                    rep_addr = (rep_tag<<(self.offset_bit+self.index_bit)) + index<<self.offset_bit
                    self.backing_mem.write_line(rep_addr,data)
                    self.dirty[way][index] = False

                #先查询下一级是否hit,
                bk_tag   = int(addr>>(self.backing_mem.offset_bit+self.backing_mem.index_bit))
                bk_index = int((addr>>self.backing_mem.offset_bit)&((1<<(self.backing_mem.index_bit))-1))
                bk_hit,bk_row = self.backing_mem.check_hit(bk_tag,bk_index)

                # 如果miss,进入l2cache line 替换阶段,此时将会检查l2替换的line所对应的l1 line 是否dirty
                #############invaild l1cache line logic################
                if (~bk_hit):
                    bk_rep_way = self.backing_mem.replacement.eviction(bk_index)
                    bk_rep_tag   = self.backing_mem.tagv[bk_rep_way][bk_index]
                    bk_rep_addr = (bk_rep_tag<<(self.backing_mem.offset_bit+self.backing_mem.index_bit)) + index<<self.backing_mem.offset_bit 
                    #将下级cache索引改为本级的索引
                    bk2ts_tag = bk_rep_addr>>(self.offset_bit+self.index_bit)
                    bk2ts_index   = (bk_rep_addr>>self.offset_bit)&((1<<(self.index_bit))-1)                
                    hit,row = self.check_hit(bk2ts_tag,bk2ts_index)
                    if self.dirty[row][bk2ts_index]:
                        bk_dirty_data = self.data[row][bk2ts_index]
                        self.backing_mem.write_line(bk_rep_addr,bk_dirty_data)
                        self.dirty[row][bk2ts_index] = False
                    self.tagv[row][index]=0xffffffff
                ######################################
                data = self.backing_mem.read_line(addr)
                self.data[way][index] = data
                return data[data_region]
    #write hit ,将数据写入l1cache,但不写入l2cache,
    #write miss,找到被替换的行,假设有脏位,那么写入下级存储,此时l2cache绝对不会miss(inclusive),假设没有脏位,从l2读出数据,如果数据miss,
    #先查询l1cache对应的way是否含dirty,如果含,先把该数据写入内存,然后将tag置为0xffffffff,如果不含dirty,则直接置位tag
    def write(self,addr,data):

        if self.full:
            tag     = addr>>(self.offset_bit)
            index   = (addr>>self.offset_bit)&((1<<(self.index_bit))-1)
            temp = int ((addr&((1<<(self.offset_bit))-1)))
            data_region = int(temp/(self.data_size/8))
            hit, row = self.check_hit(tag,index)
            
            if hit :
                self.hit+=1
                self.data[row][data_region] =  data
                self.dirty[row] = True
                self.replacement.promotion(index,row)
            else :
                self.miss +=1
                way = self.replacement.eviction(index)
                #将本级dirty 数据写入下一级
                if self.dirty[way]:
                    wdata =  self.data[way]
                    rep_tag  = self.tagv[way]
                    rep_addr = (rep_tag<<(self.offset_bit+self.index_bit)) + index<<self.offset_bit
                    self.backing_mem.write_line(rep_addr,wdata)
                    self.dirty[way] = False
                    # assert miss==False
                #先查询下一级是否hit,
                bk_tag   = addr>>(self.backing_mem.offset_bit+self.backing_mem.index_bit)
                bk_index = (addr>>self.backing_mem.offset_bit)&((1<<(self.backing_mem.index_bit))-1)
                bk_hit,bk_row = self.backing_mem.check_hit(bk_tag,bk_index)
                # 如果miss,进入l2cache line 替换阶段,此时将会检查l2替换的line所对应的l1 line 是否dirty
                #############invaild l1cache line logic################
                if (~bk_hit):
                    bk_rep_way = self.backing_mem.replacement.eviction(bk_index)
                    bk_rep_tag   = self.backing_mem.tagv[bk_rep_way][bk_index]
                    bk_rep_addr = (bk_rep_tag<<(self.backing_mem.offset_bit+self.backing_mem.index_bit)) + index<<self.backing_mem.offset_bit 
                    #将下级cache索引改为本级的索引
                    bk2ts_tag = bk_rep_addr>>(self.offset_bit)
                    bk2ts_index   = (bk_rep_addr>>self.offset_bit)&((1<<(self.index_bit))-1)                
                    hit,row = self.check_hit(bk2ts_tag,bk2ts_index)
                    if self.dirty[row][bk2ts_index]:
                        bk_dirty_data = self.data[row][bk2ts_index]
                        self.backing_mem.write_line(bk_rep_addr,bk_dirty_data)
                        self.dirty[row][bk2ts_index] = False
                    self.tagv[row][index]=0xffffffff
                ###################################### 
                #将l2数据读入l1,更新l1cache
                bk_data               = self.backing_mem.read_line(addr)
                self.data[way][index]              = bk_data
                self.data[way][index][data_region] = data
                self.replacement.insert(index,way)
                self.tagv[way][index] = tag   
                self.dirty[way][index] = True
        else:
            
            tag     = addr>>(self.offset_bit+self.index_bit)
            index   = (addr>>self.offset_bit)&((1<<(self.index_bit))-1)
            temp = int ((addr&((1<<(self.offset_bit))-1)))
            data_region = int(temp/(self.data_size/8))
            hit, row = self.check_hit(tag,index)
            
            if hit :
                self.hit+=1
                self.data[row][index][data_region] =  data
                self.dirty[row][index] = True
                self.replacement.promotion(index,row)
            else :
                self.miss +=1
                way = self.replacement.eviction(index)
                #将本级dirty 数据写入下一级
                if self.dirty[way][index]:
                    wdata =  self.data[way][index]
                    rep_tag  = self.tagv[way][index]
                    rep_addr = (rep_tag<<(self.offset_bit+self.index_bit)) + index<<self.offset_bit
                    self.backing_mem.write_line(rep_addr,wdata)
                    self.dirty[way][index] = False
                    # assert miss==False
                #先查询下一级是否hit,
                bk_tag   = addr>>(self.backing_mem.offset_bit+self.backing_mem.index_bit)
                bk_index = (addr>>self.backing_mem.offset_bit)&((1<<(self.backing_mem.index_bit))-1)
                bk_hit,bk_row = self.backing_mem.check_hit(bk_tag,bk_index)
                # 如果miss,进入l2cache line 替换阶段,此时将会检查l2替换的line所对应的l1 line 是否dirty
                #############invaild l1cache line logic################
                if (~bk_hit):
                    bk_rep_way = self.backing_mem.replacement.eviction(bk_index)
                    bk_rep_tag   = self.backing_mem.tagv[bk_rep_way][bk_index]
                    bk_rep_addr = (bk_rep_tag<<(self.backing_mem.offset_bit+self.backing_mem.index_bit)) + index<<self.backing_mem.offset_bit 
                    #将下级cache索引改为本级的索引
                    bk2ts_tag = bk_rep_addr>>(self.offset_bit+self.index_bit)
                    bk2ts_index   = (bk_rep_addr>>self.offset_bit)&((1<<(self.index_bit))-1)                
                    hit,row = self.check_hit(bk2ts_tag,bk2ts_index)
                    if self.dirty[row][bk2ts_index]:
                        bk_dirty_data = self.data[row][bk2ts_index]
                        self.backing_mem.write_line(bk_rep_addr,bk_dirty_data)
                        self.dirty[row][bk2ts_index] = False
                    self.tagv[row][index]=0xffffffff
                ###################################### 
                #将l2数据读入l1,更新l1cache
                bk_data               = self.backing_mem.read_line(addr)
                self.data[way][index]              = bk_data
                self.data[way][index][data_region] = data
                self.replacement.insert(index,way)
                self.tagv[way][index] = tag   
                self.dirty[way][index] = True


    def print_info(self):
        return self.miss,self.hit