import os
import math

##########################LRU logic#####################
class LRU:
    def __init__(self):
        self.way = 2
        self.line_size  = 16 #byte
        self.total_size = 8 #Kb
        # self.addr_size = 32 #bit
        self.lrutree    =   LruTree(0)
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
       
        self.lrutree  = self.lrutree.create_full_binary_tree(int(math.log2(way)),0)
        # self.lrutree.print_tree()
        

    def insert(self,index:int,way:int):
        self.update(way)
    

    def promotion(self,index:int,way:int):
        self.update(way)
    
    def aging(self,index:int,way:int):
        None

    def eviction(self,index:int):
        val,node_id = self.lrutree.replace()
        way = int(2*(node_id-2**int(math.log2(self.way)-1))+val)  
        return (way)
    
    def check_hit(self,tag,index):
        for row_index,row in enumerate(self.tagv):
            if tag==row[index]:
                return True,row_index 
        return False,-1
    
    def update(self,way:int):
        way_bin = int((self.way)/2)
        # assert(way_bin%2==0|way_bin==1)
        depth = int(math.log2(self.way))
        i=0
        # way+=1 #way is array addr begin->0
        way_i = way+1
        node_id = 1
        # print(f"way {way } {way_bin} depth {depth} node {node_id}")
        while(i<depth):
            
            if(way_i>way_bin):
                self.lrutree.update(node_id,0)#right has been access
                node_id=node_id*2+1
                way_i-=way_bin
            else:
                self.lrutree.update(node_id,1)
                node_id=node_id*2
            way_bin/=2
            # print(f"way {way_i } {way_bin}")
            i+=1
#     # ADD trace here
#     def read(self,tag,index,data_region,mask):
#         # tag     = addr>>(self.offset_bit+self.index_bit)
#         # index   = (addr>>self.offset_bit)&((1<<(self.index_bit))-1)
#         # temp = int ((addr&((1<<(self.offset_bit))-1)))
#         # data_region = int(temp/(self.data_size/8))
#         # print(f"region {data_region} addr {addr} temp {temp}")
#         # result = (number >> start) & mask
#         # print(f"tag {tag:x} index {index:x} addr {addr:x} ")
#         hit, row = self.check_hit(tag,index)
#         # print(hit,row)
        
#         if hit:

#             data = self.data[row][index][data_region]
#             self.hit=self.hit+1
#             self.update(row)
#             # print(f'hit tag {self.tagv[row][index]:x} index{index } data {data }')
#             # self.lrutree.print_tree()
#             return data,hit
#         else:
#             self.miss=self.miss+1 
#             val,node_id = self.lrutree.replace()
#             way = 2*(node_id-2**int(math.log2(self.way)-1))+val
#             # print(f"rep_id {node_id} way {way}")
#             self.update(way)
#             # self.lrutree.update(node_id,1 if val==0 else 0)
            
#             # self.lrutree.print_tree()
#             self.tagv[way][index] = tag

# # TODO : add data support
#             # for i in range(self.data_num):
#             #     self.data[way][index][i] = 0; 
#             return -1,hit
        
#     def write(self,tag,index,mask,data,data_region):

#         # print(f"region {data_region} addr {addr} temp {temp}")
#         # result = (number >> start) & mask
#         # print(f"tag {tag:x} index {index:x} addr {addr:x} ")
#         hit, row = self.check_hit(tag,index)
#         if hit :
#             self.hit+=1
#             self.data[row][index][data_region] =  data
#             self.dirty[row][index] = True
#             self.update(row)
#         else :
#             self.miss +=1
#             val,node_id = self.lrutree.replace()
#             way = 2*(node_id-2**int(math.log2(self.way)-1))+val    
#             if self.dirty[way][index]:
#                 #TODO:add miss read
#                 None
#             self.update(way)
#             self.tagv[way][index] = tag    


#     def print_info(self):
#         print(f'Total hit {self.hit} Total miss {self.miss} hit rate {self.hit/(self.hit+self.miss)}')




######################Bin Tree###################
class LruTree:
    
    def __init__(self, val: int, node_id: int = 0):
        self.val: int = val
        self.node_id: int = node_id  # 新增的 node_id 属性
        self.left: LruTree | None = None
        self.right: LruTree | None = None

    def create_full_binary_tree(self, depth: int, start_val: int = 1, node_id_start: int = 1):
        if depth <= 0:
            return None

        # 当前节点的 node_id 是传入的 node_id_start
        root = LruTree(start_val, node_id_start)

        if depth > 1:
            # 左子节点的 node_id 从 node_id_start * 2 开始
            root.left = self.create_full_binary_tree(depth - 1, start_val , node_id_start * 2)
            # 右子节点的 node_id 从 node_id_start * 2 + 1 开始
            root.right = self.create_full_binary_tree(depth - 1, start_val , node_id_start * 2 + 1)

        return root
    def replace(self):
        node = self
        while node.left and node.right:
            if node.val==0:
                node = node.left

            else:
                node = node.right
        return  node.val,node.node_id

    # update the entire right node or left node 
    # the node_id input is the leaf node
    def update(self, node_id: int, val: int):

        node = self.search(node_id)
        if node:
            node.val = val
            # print(f"Node with ID {node_id} found and updated to {val}.")
        else:
            print(f"Node with ID {node_id} not found.")


    def search(self, node_id: int):
 
        if self.node_id == node_id:
            return self
        # 递归搜索左子树
        if self.left:
            result = self.left.search(node_id)
            if result:
                return result
        # 递归搜索右子树
        if self.right:
            result = self.right.search(node_id)
            if result:
                return result
        return None
        
    

        
    def print_tree(self):
        """打印二叉树的节点值和ID"""
        lines, *_ = self._display_aux()
        for line in lines:
            print(line)

    def _display_aux(self):
        """返回二叉树的行表示形式，包含node_id"""
        # No child.
        if self.right is None and self.left is None:
            line = f'{self.val}(ID={self.node_id})'
            width = len(line)
            height = 1
            middle = width // 2
            return [line], width, height, middle

        # Only left child.
        if self.right is None:
            lines, n, p, x = self.left._display_aux()
            s = f'{self.val}(ID={self.node_id})'
            u = len(s)
            first_line = f'{s}{" " * (n - x)}'
            second_line = f'{" " * x}/'
            shifted_lines = [line + ' ' * u for line in lines]
            return [first_line, second_line] + shifted_lines, n + u, p + 2, u // 2

        # Only right child.
        if self.left is None:
            lines, n, p, x = self.right._display_aux()
            s = f'{self.val}(ID={self.node_id})'
            u = len(s)
            first_line = f'{" " * (x + 1)}{s}'
            second_line = f'{" " * (x + 1)}\\'
            shifted_lines = [' ' * u + line for line in lines]
            return [first_line, second_line] + shifted_lines, n + u, p + 2, n + u // 2

        # Two children.
        left, n, p, x = self.left._display_aux()
        right, m, q, y = self.right._display_aux()
        s = f'{self.val}(ID={self.node_id})'
        u = len(s)
        first_line = f'{" " * (x + 1)}{s}{" " * (y + 1)}'
        second_line = f'{" " * x}/{" " * (u - 2)}\\{" " * y}'
        if p < q:
            left += [' ' * n] * (q - p)
        elif q < p:
            right += [' ' * m] * (p - q)
        zipped_lines = zip(left, right)
        lines = [first_line, second_line] + [a + ' ' * u + b for a, b in zipped_lines]
        return lines, n + m + u, max(p, q) + 2, n + u // 2


    
        
