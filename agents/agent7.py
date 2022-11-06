import math
import hashlib

class EncoderDecoder:
    def __init__(self, n):
        self.encoding_len = n
        characters = " 1234567890abcdefghijklmnopqrstuvwxyz.," 
        self.chars = characters
        self.char_dict, self.bin_dict = self.binary_encoding_dicts(characters)
        if n < 7: #If less than 7 bits its for checksum
            self.perm_zero = [46,47,48,49,50,51]
        else:
            self.perm_zero = list(range(46-n, 46)) #[24,25,...45]
        self.max_messge_length = 12 #TODO TEST AND CHANGE THIS VALUE
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

    def binary_encoding_dicts(self, characters):
        char_dict = {}
        bin_dict = {}
        for i in range(len(characters)):
            b = self.to_binary_padded(i)
            char_dict[characters[i]] = b
            bin_dict[b] = characters[i]
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
        n = int(ret, 2)
        return self.nth_perm(n)

    def str_to_num(self, message):
        # Adapted from Group 1 Agent
        # Stop match string at unknown char, to meet with partial requirements
        tokens = []
        for ch in message:
            if ch in self.chars:    #TODO utilize self.char_dict
                tokens.append(ch)
            else:
                break
        while len(tokens) < self.max_messge_length:
            tokens.append(" ")
        tokens = tokens[::-1]

        # Convert char to int
        max_trials = 100
        while max_trials > 0:
            max_trials -= 1
            num = 0
            for idx, ch in enumerate(tokens):   #TODO utilize char_dict, etc
                num += self.chars.index(ch) * len(self.chars) ** idx

            # Check if message can fit in N cards
            if num // self.factorials[0] < len(self.perm_zero):
                break
            else:
                tokens = tokens[1:]
        return num

    def num_to_perm(self, n):
        # Adapted from Group 1 Code
        perm = []
        items = list(self.perm_zero[:])
        for idx, f in enumerate(self.factorials):
            lehmer = n // f
            perm.append(items.pop(lehmer))
            n %= f
        return perm

    def perm_to_str(self, permutation):
        n = self.perm_number(permutation)
        binary_string = self.to_binary(n)
        binary_string = '0' * ((6 - len(binary_string) % 6) % 6) + binary_string

        ret = ''
        for i in range(0, len(binary_string) - 5, 6):
            if binary_string[i:i + 6] not in self.bin_dict:
                return 'PARTIAL: '
            ret += self.bin_dict[binary_string[i:i + 6]]
        return ret

    def perm_to_num(self, permutation):
        # Adapted from Group 1
        n = len(permutation)
        number = 0
        for i in range(n):
            k = 0
            for j in range(i + 1, n):
                if permutation[j] < permutation[i]:
                    k += 1
            number += k * self.factorials[i]
        return number


    def set_checksum(self, num, base=10):
        num_bin = bin(num)[2:]
        chunk_len = 5
        checksum = 0
        mod_prime = 113
        # From wikipedia - rollin hash
        # ASCII a = 97, b = 98, r = 114.
        # hash("abr") =  [ ( [ ( [  (97 × 256) % 101 + 98 ] % 101 ) × 256 ] %  101 ) + 114 ]   % 101   =  4
        while len(num_bin) > 0:
            bin_chunk = num_bin[:chunk_len]
            num_bin = num_bin[chunk_len:]

            num_chunk = int(bin_chunk, 2)
            checksum = ((checksum + num_chunk) * base) % mod_prime
            # if len(num_bin) > 0:
            #     checksum = (checksum * base) % mod_prime
        return checksum


    def get_checksum(self, perm):
        pass

class Agent:
    def __init__(self, encoding_len=26):
        self.encoding_len = encoding_len - 6 # Reserve for checksum

        self.ed = EncoderDecoder(self.encoding_len)
        self.perm_ck = EncoderDecoder(6)

    def encode(self, message):
        print('Encoding...')
        print('message to encode: ', message)

        x  = self.ed.str_to_num(message)
        checksum = self.ed.set_checksum(x)
        print('Checksum int_val w/ set_checksum:', checksum)
        checksum_cards = self.perm_ck.num_to_perm(checksum)
        print('Checksum Cards: ', checksum_cards)

        encoded_deck = list(range(48 - self.encoding_len - 2)) + self.ed.str_to_perm(message) + checksum_cards
        
        print('Encoded deck:\n', encoded_deck, '\n---------')
        return encoded_deck

    def decode(self, deck):

        print('\n')
        print('Decoding...')
        print('Deck to decode:', deck)
        msg_perm = []
        checksum = []
        for card in deck:
            if 26 <= card <= 45:
                msg_perm.append(card)
            if card > 45:
                checksum.append(card)

        print('\nMessage Cards:', msg_perm)
        print('Checksum Cards:', checksum)

        decoded_checksum = self.perm_ck.perm_to_num(checksum)
        print('Checksum int_val using perm_to_num: ', decoded_checksum)

        ### We get same int_val as encode using perm_to_num of checksum cards. Now need to get checksum val from message cards itself
        
        msg_num = self.ed.perm_to_num(msg_perm)
        message_checksum = self.ed.set_checksum(msg_num)
        print(message_checksum) #GETTING WRONG VALUE HERE

        print('decoded_checksum', decoded_checksum)
        print('message_Checksum', message_checksum)
        

        if message_checksum != decoded_checksum:
            print("MESSAGE CHECKSUM IS NOT EQUAL TO DECODED CHECKSUM")
            return "NULL"
        else:
            print(self.ed.perm_to_str(msg_perm))
            return self.ed.perm_to_str(msg_perm)

'''
import math
import hashlib

class EncoderDecoder:
    def __init__(self, n=26):
        self.encoding_len = n
        characters = " 1234567890abcdefghijklmnopqrstuvwxyz.," 
        self.char_dict, self.bin_dict = self.binary_encoding_dicts(characters)
        self.perm_zero = list(range(48-n, 48)) #[24,25,...48,49]

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

    def binary_encoding_dicts(self, characters):
        char_dict = {}
        bin_dict = {}
        for i in range(len(characters)):
            b = self.to_binary_padded(i)
            char_dict[characters[i]] = b
            bin_dict[b] = characters[i]
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
        n = int(ret, 2)
        return self.nth_perm(n)

    def str_to_bitstr(self, s):
        ret = ''
        for c in s[:14]:
            ret += self.char_dict[c]
        n = int(ret, 2)
        return n

    def perm_to_str(self, permutation):
        n = self.perm_number(permutation)
        binary_string = self.to_binary(n)
        binary_string = '0' * ((6 - len(binary_string) % 6) % 6) + binary_string

        ret = ''
        for i in range(0, len(binary_string) - 5, 6):
            if binary_string[i:i + 6] not in self.bin_dict:
                return 'PARTIAL: '
            ret += self.bin_dict[binary_string[i:i + 6]]
        return ret

    def set_checksum(self, bits: str, checksum_bits=10) -> str:
        bitstr = bytes(bits, "utf-8")
        hasher = hashlib.blake2b(bitstr).hexdigest()
        scale,num_bits = 16,8
        binstr = bin(int(hasher, scale))[2:].zfill(num_bits)
        return binstr[-checksum_bits:]


    def get_checksum(self, perm):
        pass

    def to_bin_string(self, value: int) -> str:
        
        return bin(value)[2:]

class Agent:
    def __init__(self, encoding_len=26):
        self.encoding_len = encoding_len
        self.ed = EncoderDecoder(self.encoding_len)

    def encode(self, message):
        x  = self.ed.str_to_bitstr(message)
        print('xxx',x, type(x))
        y = self.ed.to_bin_string(x)
        print(y, type(y))
        checksum = self.ed.set_checksum(y)
        print('ccc', checksum, type(checksum))
        yerr = self.ed.str_to_perm(checksum)
        print(yerr, type(yerr))

        sds
        return list(range(48 - self.encoding_len)) + self.ed.str_to_perm(message) + checksum


    def decode(self, deck):
        perm = []
        for card in deck:
            if 24 <= card <= 48:
                perm.append(card)
        print(perm)
        if perm[-4:] != self.ed.get_checksum(deck): #deck or perm
            return "NULL"

        return self.ed.perm_to_str(perm[:-2])



'''