import os
import math
##########################LRU logic#####################
class LRU:
    def __init__(self):
        self.way = 2
        self.line_size  = 16 #byte
        self.total_size = 8 #Kb
        self.addr_size = 32 #bit
        self.lrutree    =   LruTree(0)
        self.hit        = 0
        self.miss       = 0
        
    def set_params(self,
                   way,
                   tag_bit, index_bit,
                   offset_bit,index_num):
        self.way = way
        self.tag_bit = tag_bit
        self.index_bit = index_bit
        self.offset_bit = offset_bit
        print(index_num)
        self.tagv = [[ 0xffffffff for _ in range(index_num)] for _ in range(way)]
        self.data = [[ 0  for _ in range(index_num)] for _ in range(way)]

        self.lrutree  = self.lrutree.create_full_binary_tree(int(math.log2(way)),0)
        self.lrutree.print_tree()
        


    def check_hit(self,tag,index):
        for row_index,row in enumerate(self.tagv):
            if tag==row[index]:
                return True,row_index 
        return False,-1

    # ADD trace here
    def read(self,addr):
        tag     = addr>>(self.offset_bit+self.index_bit)
        index   = (addr>>self.offset_bit)&((1<<(self.index_bit))-1)
        
        # result = (number >> start) & mask
        # print(f"tag {tag:x} index {index:x} addr {addr:x} ")
        hit, row = self.check_hit(tag,index)
        # print(hit,row)
        data = self.data[row][index]
        if hit:
            self.hit=self.hit+1
            # print(f'hit tag {self.tagv[row][index]:x} index{index } data {data }')
            return data,hit
        else:
            self.miss=self.miss+1 
            val,node_id = self.lrutree.replace()
            self.lrutree.update(node_id,1 if val==0 else 0)
            way = node_id-2**int(math.log2(self.way)-1)+val
            # self.lrutree.print_tree()
            self.tagv[way][index] = tag
            return -1,hit
    def print_info(self):
        print(f'Total hit {self.hit} Total miss {self.miss} hit rate {self.hit/(self.hit+self.miss)}')

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


    
        
