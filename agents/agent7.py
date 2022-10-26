import math
import pdb
import heapq
import re
 
 
 # Huffman encoding from==========================================
 # https://www.geeksforgeeks.org/huffman-coding-greedy-algo-3/
class node:
    def __init__(self, freq, symbol, left=None, right=None):
        # frequency of symbol
        self.freq = freq
 
        # symbol name (character)
        self.symbol = symbol
 
        # node left of current node
        self.left = left
 
        # node right of current node
        self.right = right
 
        # tree direction (0/1)
        self.huff = ''
         
    def __lt__(self, nxt):
        return self.freq < nxt.freq
         
def printNodes(node, val='', return_dict=dict()):
     
    # huffman code for current node
    newVal = val + str(node.huff)
 
    # if node is not an edge node
    # then traverse inside it
    if(node.left):
        printNodes(node.left, newVal, return_dict)
    if(node.right):
        printNodes(node.right, newVal, return_dict)
 
        # if node is edge node then
        # display its huffman code
    if(not node.left and not node.right):
        #print(f"{node.symbol} -> {newVal}")
        return_dict[node.symbol] = newVal
    
def huffman_encoding(chars, freq):
    nodes = []
    # converting characters and frequencies
    # into huffman tree nodes
    for x in range(len(chars)):
        heapq.heappush(nodes, node(freq[x], chars[x]))
    
    while len(nodes) > 1:
        
        # sort all the nodes in ascending order
        # based on their frequency
        left = heapq.heappop(nodes)
        right = heapq.heappop(nodes)
    
        # assign directional value to these nodes
        left.huff = 0
        right.huff = 1
    
        # combine the 2 smallest nodes to create
        # new node as their parent
        newNode = node(left.freq+right.freq, left.symbol+right.symbol, left, right)
    
        heapq.heappush(nodes, newNode)
    
    # Huffman Tree is ready!
    char_dict = dict()
    printNodes(nodes[0], return_dict=char_dict)
    bin_dict = {v: k for k, v in char_dict.items()}
    return char_dict, bin_dict

#================================================================
import random 
def alpha_number_frequency():
    frequency = {
    'e' : 12.0,
    't' : 9.10,
    'a' : 8.12,
    'o' : 7.68,
    'i' : 7.31,
    'n' : 6.95,
    's' : 6.28,
    'r' : 6.02,
    'h' : 5.92,
    'd' : 4.32,
    'l' : 3.98,
    'u' : 2.88,
    'c' : 2.71,
    'm' : 2.61,
    'f' : 2.30,
    'y' : 2.11,
    'w' : 2.09,
    'g' : 2.03,
    'p' : 1.82,
    'b' : 1.49,
    'v' : 1.11,
    'k' : 0.69,
    'x' : 0.17,
    'q' : 0.11,
    'j' : 0.10,
    'z' : 0.07
    }
    for i in range(10):
        frequency[str(i)] = frequency['z']
    frequency[' '] = frequency['e']
    return (
        [k for k, _ in sorted(frequency.items(), key=lambda item: item[1], reverse=True)],
        [v for _, v in sorted(frequency.items(), key=lambda item: item[1], reverse=True)])
    

class EncoderDecoder:
    def __init__(self, n=26):
        self.encoding_len = n
        self.char_dict, self.bin_dict = self.binary_encoding_dicts()
        self.perm_zero = list(range(50-n, 50))

        factorials = [0] * n
        for i in range(n):
            factorials[i] = math.factorial(n-i-1)
        self.factorials = factorials

    @staticmethod
    def to_binary_padded(n):
        ret = ''
        while n > 1:
            ret += str(n % 2)
            n = n // 2
        ret += str(n)
        return '0' * (6 - len(ret)) + ret[::-1]

    @staticmethod
    def to_binary(n):
        ret = ''
        while n > 1:
            ret += str(n % 2)
            n = n // 2
        ret += str(n)
        return ret[::-1]

    def binary_encoding_dicts(self):
        char_dict, bin_dict = huffman_encoding(*alpha_number_frequency())
        return char_dict, bin_dict

    def perm_number(self, permutation):
        n = len(permutation)
        s = sorted(permutation)
        number = 0

        for i in range(n):
            k = 0
            for j in range(i + 1, n):
                if permutation[j] < permutation[i]:
                    k += 1
            number += k * self.factorials[i]
        return number

    def nth_perm(self, n):
        perm = []
        items = self.perm_zero[:]
        for f in self.factorials:
            lehmer = n // f
            perm.append(items.pop(lehmer))
            n %= f
        return perm

    def str_to_perm(self, s):
        ret = ''
        for c in s[:14]:
            ret += self.char_dict[c]
        # need this 1 since some encoding doesnt start with 1
        # i.e. two 'space' ("  ") has encoding 001001
        # when put in front of string, the return binary become
        # 1001xxxxx, which translate to ixxxxx (i has encdoing 1001)
        ret = '1' + ret
        n = int(ret, 2)
        return self.nth_perm(n)

    def perm_to_str(self, permutation):
        n = self.perm_number(permutation)
        binary_string = self.to_binary(n)
        binary_string = binary_string[1:]
        last_i = 0
        ret = ''
        for i in range(1, len(binary_string) + 1):
            current = binary_string[last_i:i]
            if current in self.bin_dict:
                ret += self.bin_dict[current]
                last_i = i
        # for i in range(0, len(binary_string) - 5, 6):
        #     if binary_string[i:i + 6] not in self.bin_dict:
        #         return 'PARTIAL: '
        #     ret += self.bin_dict[binary_string[i:i + 6]]
        return ret


class Agent:
    def __init__(self, encoding_len=26):
        self.encoding_len = encoding_len
        self.ed = EncoderDecoder(self.encoding_len)

    def encode(self, message):
        return list(range(50 - self.encoding_len)) + self.ed.str_to_perm(message) + [50, 51]

    def decode(self, deck):
        perm = []
        for card in deck:
            if 24 <= card <= 51:
                perm.append(card)
        print(perm)
        if perm[-2:] != [50, 51]:
            return "NULL"
        # if perm[:2] != [22, 23]:
        #     return "PARTIAL:"

        return self.ed.perm_to_str(perm[:-2])

#testing
def test_huffman():
    ed = EncoderDecoder(26)
    p = ed.str_to_perm('abcasd1de 123')
    s = ed.perm_to_str(p)

    print(p)
    print(f'#{s}#')
    
    dict = huffman_encoding(*alpha_number_frequency())
    #print(dict)
    
test_huffman()