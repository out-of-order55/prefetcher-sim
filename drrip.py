import math 

from srrip import SRRIP
from brrip import BRRIP

class DRRIP:
    def __init__(self):
        self.way = 2
        self.line_size  = 16 #byte
        self.total_size = 8 #Kb

        self.hit        = 0
        self.miss       = 0
        self.MBIT       = 3#2-bits
        self.cnt        = 0#brrip
        self.scale      = 32#brrip 
        self.constituency = 32 #32个set一次抽样
        self.psel       = 0 #10 bits
    def set_params(self,
                    way,index_num,data_num):
        self.way = way
        self.rrpv = [[2**self.MBIT-1 for _ in range(way)] for _ in range(index_num)]#2-bits
        self.identify_bit = int(math.log2(self.constituency))
        self.common_bit   =  int(math.log2(index_num))-int(math.log2(self.constituency))#offset bits
        if self.identify_bit>=self.common_bit:
            self.set_bit = self.common_bit
        else:
            self.set_bit = self.identify_bit
        assert index_num==1024
        self.data_num = data_num

    #return: rep_sel,dedicated_rep_sel
    def rep_sel(self,index:int):
        identify_index = index>>self.common_bit
        common_index = index&((1<<self.common_bit)-1)
        dedicated_srrip_set = identify_index==common_index
        dedicated_brrip_set = (identify_index!=common_index)
        if (dedicated_srrip_set==True)&(dedicated_brrip_set==False):
            return True,1
        elif (dedicated_srrip_set==False)&(dedicated_brrip_set==True):
            return False,0
        elif (dedicated_srrip_set==False)&(dedicated_brrip_set==False):
            if(self.psel>=512):
                return False,-1
            else:
                return True,-1

#only cache miss can use this api
    def insert(self,index:int,way:int):
        rep_sel,dedicated_rep_sel=self.rep_sel(index)
        if rep_sel==False:
            if dedicated_rep_sel==0:
                self.psel-=1
            if(self.cnt==self.scale-1):
                self.rrpv[index][way] = 2**self.MBIT-2
                self.cnt=0
            else:
                self.rrpv[index][way] = 2**self.MBIT-1
                self.cnt+=1
        else:
            if dedicated_rep_sel==1:
                self.psel+=1 
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
                    if(self.rrpv[index][j]>2**self.MBIT-1):
                        self.rrpv[index][j] = 2**self.MBIT-1
            else :
                i+=1

        return i 
    def check_hit(self,tag,index):
        for row_index,row in enumerate(self.tagv):
            if tag==row[index]:
                return True,row_index 
        return False,-1
    