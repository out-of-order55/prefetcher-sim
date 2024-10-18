import math
import random
class RANDOM:
    def __init__(self):
        self.way = 2
        self.line_size  = 16 #byte
        self.total_size = 8 #Kb
        # self.addr_size = 32 #bit
        self.hit        = 0
        self.miss       = 0
        
    def set_params(self,
                    way,index_num,data_num):
        self.way = way
        # self.tag_bit = tag_bit
        # self.index_bit = index_bit
        # self.offset_bit = offset_bit
        # self.data_size = data_size
        self.data_num = data_num
        # print(f"self.data_num {self.data_num}")
        # self.tagv = [[ 0xffffffff for _ in range(index_num)] for _ in range(way)]
        # self.dirty = [[ 0 for _ in range(index_num)] for _ in range(way)]
        # self.data = [[[0  for _ in range(data_num)] for _ in range(index_num)] for _ in range(way)]

    def insert(self,index:int,way:int):
        None

    def promotion(self,index:int,way:int):
        None
    
    def aging(self,index:int,way:int):
        None

    def eviction(self,index:int):
        way = random.randint(0, self.way-1)
        return (way)
    
    def check_hit(self,tag,index):
        for row_index,row in enumerate(self.tagv):
            if tag==row[index]:
                return True,row_index 
        return False,-1
    
