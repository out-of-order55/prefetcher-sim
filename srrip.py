import math 
class SRRIP:
    def __init__(self):
        self.way = 2
        self.line_size  = 16 #byte
        self.total_size = 8 #Kb

        self.hit        = 0
        self.miss       = 0
        self.MBIT       = 3#2-bits
    def set_params(self,
                    way,index_num,data_num):
        self.way = way
        self.rrpv = [[2**self.MBIT-1 for _ in range(way)] for _ in range(index_num)]#2-bits

        self.data_num = data_num


    def insert(self,index:int,way:int):
        self.rrpv[index][way] = 2**self.MBIT-2
    

    def promotion(self,index:int,way:int):
        self.rrpv[index][way] = 0
    
    def aging(self,index:int,way:int):
        None

    def eviction(self,index:int):
        i=0
        while(i<self.way):
            if(self.rrpv[index][i]==2**self.MBIT-1):
                break
            if (i==self.way-1)&(self.rrpv[index][i]!=2**self.MBIT-1):
                i=0
                for j in range(self.way):
                    self.rrpv[index][j] += 1
            else :
                i+=1
        return i 
    def check_hit(self,tag,index):
        for row_index,row in enumerate(self.tagv):
            if tag==row[index]:
                return True,row_index 
        return False,-1
    
