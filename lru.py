import os
import math
class LRU:
    def __init__(self):
        self.way = 2
        self.line_size  = 16 #byte
        self.total_size = 8 #Kb
        self.addr_size = 32 #bit

   
    def set_params(self,
                   way,
                   tag_bit, index_bit,
                   offset_bit,index_num):

        self.tag_bit = tag_bit
        self.index_bit = index_bit
        self.offset_bit = offset_bit
        self.tagv = [[ 0xffffffff for _ in range(index_num)] for _ in range(way)]
        self.data = [[ 0  for _ in range(index_num)] for _ in range(way)]
        self.lru  = [0]*(way-1)


    def check_hit(self,tag,index):
        for row_index,row in enumerate(self.tagv):
            if tag in row:
                return True,row_index 
        return False,-1
    
    def read(self,addr):
        tag     = addr>>(self.offset_bit+self.index_bit)
        index   = (addr<<self.tag_bit)>>(self.tag_bit+self.offset_bit)

        hit, row = self.check_hit(tag,index)

        data = self.data[row][index]
        if hit:
            return data
        else:
            print("miss")
        

            

    
        
