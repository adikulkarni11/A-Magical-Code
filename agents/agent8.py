import hashlib
import heapq
import os.path as path
import pdb
from enum import Enum
from math import ceil, factorial, log2
from operator import indexOf
from pprint import pprint
from random import Random
from string import ascii_letters, digits, punctuation
from typing import Callable, Dict, Optional

# ================
# Frequency Distributions
# ================


class FrequencyDistribution(Enum):
    """
    Frequency distributions for the English language.

    A frequency distribution is a mapping from characters to their frequency in English text.

    The frequencies are based on the following sources:

    lowercase_only:
        - Source for frequencies: http://mathcenter.oxford.emory.edu/site/math125/englishLetterFreqs/
        - the average english word is 4.7 characters long, so we take the probability of a space to be 1/(4.7+1)

    letters_and_space:
        - derived from ascii_printable by removing all non-letters and renormalizing

    ascii_printable:
        - (from analyzing the Rutgers Corpus) https://github.com/piersy/ascii-char-frequency-english

    numbers:
        - assume that numbers are equally likely to appear in a message
    """

    lowercase_and_space = {
        " ": 1 / (4.7 + 1),
        "a": 0.08167 * (4.7 / 5.7),
        "b": 0.01492 * (4.7 / 5.7),
        "c": 0.02782 * (4.7 / 5.7),
        "d": 0.04253 * (4.7 / 5.7),
        "e": 0.12702 * (4.7 / 5.7),
        "f": 0.02228 * (4.7 / 5.7),
        "g": 0.02015 * (4.7 / 5.7),
        "h": 0.06094 * (4.7 / 5.7),
        "i": 0.06966 * (4.7 / 5.7),
        "j": 0.00153 * (4.7 / 5.7),
        "k": 0.00772 * (4.7 / 5.7),
        "l": 0.04025 * (4.7 / 5.7),
        "m": 0.02406 * (4.7 / 5.7),
        "n": 0.06749 * (4.7 / 5.7),
        "o": 0.07507 * (4.7 / 5.7),
        "p": 0.01929 * (4.7 / 5.7),
        "q": 0.00095 * (4.7 / 5.7),
        "r": 0.05987 * (4.7 / 5.7),
        "s": 0.06327 * (4.7 / 5.7),
        "t": 0.09056 * (4.7 / 5.7),
        "u": 0.02758 * (4.7 / 5.7),
        "v": 0.00978 * (4.7 / 5.7),
        "w": 0.02360 * (4.7 / 5.7),
        "x": 0.00150 * (4.7 / 5.7),
        "y": 0.01974 * (4.7 / 5.7),
        "z": 0.00074 * (4.7 / 5.7),
    }

    letters_and_space = {
        " ": 0.00167564443682168,
        "A": 2.4774830020061095e-05,
        "B": 1.7387002075069484e-05,
        "C": 2.987392712176473e-05,
        "D": 1.0927723198318497e-05,
        "E": 1.2938206232079081e-05,
        "F": 1.220297284016159e-05,
        "G": 9.310209736100016e-06,
        "H": 8.752446473266058e-06,
        "I": 2.0910417959267183e-05,
        "J": 8.814561018445295e-06,
        "K": 3.808001912620934e-06,
        "L": 1.0044809306127923e-05,
        "M": 1.8134911904778658e-05,
        "N": 1.2758834637326799e-05,
        "O": 8.210528757671702e-06,
        "P": 1.38908405321239e-05,
        "Q": 1.0001709417636209e-06,
        "R": 1.1037374385216535e-05,
        "S": 3.0896915651553376e-05,
        "T": 3.07010646876719e-05,
        "U": 1.0426370083657518e-05,
        "V": 2.556203680692448e-06,
        "W": 8.048270353938186e-06,
        "X": 6.572732994986532e-07,
        "Y": 2.519442011096573e-06,
        "Z": 8.619977698342993e-07,
        "a": 0.000612553996079051,
        "b": 0.0001034644514338097,
        "c": 0.0002500268898936656,
        "d": 0.0003188948073064199,
        "e": 0.0008610229517681191,
        "f": 0.00015750347191785568,
        "g": 0.00012804659959943725,
        "h": 0.0002619237267611581,
        "i": 0.0005480626188138746,
        "j": 6.17596049210692e-06,
        "k": 4.945712204424292e-05,
        "l": 0.0003218192615049607,
        "m": 0.00018140172626462204,
        "n": 0.0005503703643138501,
        "o": 0.000541904405334676,
        "p": 0.00017362092874808832,
        "q": 1.00853739070613e-05,
        "r": 0.0005152502934119982,
        "s": 0.000518864979648296,
        "t": 0.000632964962389326,
        "u": 0.00019247776378510318,
        "v": 7.819143740853554e-05,
        "w": 9.565830104169262e-05,
        "x": 2.3064144740073766e-05,
        "y": 0.00010893686962847832,
        "z": 5.762708620098124e-06,
    }

    letters_numbers_and_space = {
        " ": 0.00167564443682168,
        "0": 5.918945715880591e-05,
        "1": 4.937789430804492e-05,
        "2": 2.756237869045172e-05,
        "3": 2.1865587546870336e-05,
        "4": 1.8385271551164355e-05,
        "5": 2.526921109393665e-05,
        "6": 1.9199098857390265e-05,
        "7": 1.824329544789753e-05,
        "8": 2.552781042488694e-05,
        "9": 2.442242504945237e-05,
        "A": 2.4774830020061095e-05,
        "B": 1.7387002075069484e-05,
        "C": 2.987392712176473e-05,
        "D": 1.0927723198318497e-05,
        "E": 1.2938206232079081e-05,
        "F": 1.220297284016159e-05,
        "G": 9.310209736100016e-06,
        "H": 8.752446473266058e-06,
        "I": 2.0910417959267183e-05,
        "J": 8.814561018445295e-06,
        "K": 3.808001912620934e-06,
        "L": 1.0044809306127923e-05,
        "M": 1.8134911904778658e-05,
        "N": 1.2758834637326799e-05,
        "O": 8.210528757671702e-06,
        "P": 1.38908405321239e-05,
        "Q": 1.0001709417636209e-06,
        "R": 1.1037374385216535e-05,
        "S": 3.0896915651553376e-05,
        "T": 3.07010646876719e-05,
        "U": 1.0426370083657518e-05,
        "V": 2.556203680692448e-06,
        "W": 8.048270353938186e-06,
        "X": 6.572732994986532e-07,
        "Y": 2.519442011096573e-06,
        "Z": 8.619977698342993e-07,
        "a": 0.000612553996079051,
        "b": 0.0001034644514338097,
        "c": 0.0002500268898936656,
        "d": 0.0003188948073064199,
        "e": 0.0008610229517681191,
        "f": 0.00015750347191785568,
        "g": 0.00012804659959943725,
        "h": 0.0002619237267611581,
        "i": 0.0005480626188138746,
        "j": 6.17596049210692e-06,
        "k": 4.945712204424292e-05,
        "l": 0.0003218192615049607,
        "m": 0.00018140172626462204,
        "n": 0.0005503703643138501,
        "o": 0.000541904405334676,
        "p": 0.00017362092874808832,
        "q": 1.00853739070613e-05,
        "r": 0.0005152502934119982,
        "s": 0.000518864979648296,
        "t": 0.000632964962389326,
        "u": 0.00019247776378510318,
        "v": 7.819143740853554e-05,
        "w": 9.565830104169262e-05,
        "x": 2.3064144740073766e-05,
        "y": 0.00010893686962847832,
        "z": 5.762708620098124e-06,
    }

    ascii_printable = {
        chr(32): 0.00167564443682168,
        chr(101): 0.0008610229517681191,
        chr(116): 0.000632964962389326,
        chr(97): 0.000612553996079051,
        chr(110): 0.0005503703643138501,
        chr(105): 0.0005480626188138746,
        chr(111): 0.000541904405334676,
        chr(115): 0.000518864979648296,
        chr(114): 0.00051525029341199825,
        chr(108): 0.0003218192615049607,
        chr(100): 0.0003188948073064199,
        chr(104): 0.0002619237267611581,
        chr(99): 0.0002500268898936656,
        chr(10): 0.00019578060965172565,
        chr(117): 0.00019247776378510318,
        chr(109): 0.00018140172626462205,
        chr(112): 0.00017362092874808832,
        chr(102): 0.00015750347191785568,
        chr(103): 0.00012804659959943725,
        chr(46): 0.00011055184780313847,
        chr(121): 0.00010893686962847832,
        chr(98): 0.0001034644514338097,
        chr(119): 0.00009565830104169261,
        chr(44): 0.00008634492219614468,
        chr(118): 0.00007819143740853554,
        chr(48): 0.00005918945715880591,
        chr(107): 0.00004945712204424292,
        chr(49): 0.00004937789430804492,
        chr(83): 0.000030896915651553373,
        chr(84): 0.000030701064687671904,
        chr(67): 0.00002987392712176473,
        chr(50): 0.00002756237869045172,
        chr(56): 0.00002552781042488694,
        chr(53): 0.000025269211093936652,
        chr(65): 0.000024774830020061096,
        chr(57): 0.00002442242504945237,
        chr(120): 0.000023064144740073764,
        chr(51): 0.000021865587546870337,
        chr(73): 0.000020910417959267183,
        chr(45): 0.00002076717421222119,
        chr(54): 0.000019199098857390264,
        chr(52): 0.000018385271551164353,
        chr(55): 0.000018243295447897528,
        chr(77): 0.000018134911904778657,
        chr(66): 0.000017387002075069484,
        chr(34): 0.000015754276887500987,
        chr(39): 0.000015078622753204398,
        chr(80): 0.0000138908405321239,
        chr(69): 0.000012938206232079082,
        chr(78): 0.000012758834637326799,
        chr(70): 0.00001220297284016159,
        chr(82): 0.000011037374385216535,
        chr(68): 0.000010927723198318497,
        chr(85): 0.000010426370083657518,
        chr(113): 0.0000100853739070613,
        chr(76): 0.000010044809306127922,
        chr(71): 0.000009310209736100016,
        chr(74): 0.000008814561018445294,
        chr(72): 0.000008752446473266058,
        chr(79): 0.000008210528757671701,
        chr(87): 0.000008048270353938186,
        chr(106): 0.00000617596049210692,
        chr(122): 0.000005762708620098124,
        chr(47): 0.00000519607185080999,
        chr(60): 0.0000044107665296153596,
        chr(62): 0.000004404428310719519,
        chr(75): 0.000003808001912620934,
        chr(41): 0.000003314254660634964,
        chr(40): 0.000003307916441739124,
        chr(86): 0.000002556203680692448,
        chr(89): 0.0000025194420110965734,
        chr(58): 0.0000012036277683200988,
        chr(81): 0.0000010001709417636208,
        chr(90): 0.08619977698342993e-05,
        chr(88): 0.06572732994986532e-05,
        chr(59): 0.0741571610813331e-06,
        chr(63): 0.04626899793963519e-06,
        chr(127): 0.031057272589618137e-06,
        chr(94): 0.022183766135441526e-06,
        chr(38): 0.020282300466689395e-06,
        chr(43): 0.015211725350017046e-06,
        chr(91): 0.0697204078542448e-07,
        chr(93): 0.06338218895840436e-07,
        chr(36): 0.05070575116672349e-07,
        chr(33): 0.05070575116672349e-07,
        chr(42): 0.04436753227088305e-07,
        chr(61): 0.025352875583361743e-07,
        chr(126): 0.019014656687521307e-07,
        chr(95): 0.012676437791680872e-07,
        chr(9): 0.012676437791680872e-07,
        chr(123): 0.06338218895840436e-08,
        chr(64): 0.06338218895840436e-08,
        chr(5): 0.06338218895840436e-08,
        chr(27): 0.06338218895840436e-08,
        chr(30): 0.06338218895840436e-08,
        "#": 0.01e-08,
        "%": 0.01e-08,
        "\\": 0.01e-08,
        "`": 0.01e-08,
        "|": 0.01e-08,
        "}": 0.01e-08,
    }

    numbers = {
        "0": 0.1,
        "1": 0.1,
        "2": 0.1,
        "3": 0.1,
        "4": 0.1,
        "5": 0.1,
        "6": 0.1,
        "7": 0.1,
        "8": 0.1,
        "9": 0.1,
    }


# ================
# Message <-> Bits
# ================
class FreqTree:
    char: Optional[str]
    freq: float
    left: Optional["FreqTree"]
    right: Optional["FreqTree"]

    def __init__(self, char: Optional[str], freq: float):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other: "FreqTree"):
        return self.freq < other.freq

    def __eq__(self, other: object):
        if not isinstance(other, FreqTree):
            return NotImplemented
        return self.freq == other.freq


# def make_huffman_encoding(frequencies: Dict[str, float]) -> Dict[str, str]:
def make_huffman_encoding(frequencies: FrequencyDistribution) -> Dict[str, str]:
    """
    frequencies is a dictionary mapping from a character in the English alphabet to its frequency.
    Returns a dictionary mapping from a character to its Huffman encoding.
    """
    huffman_encoding: Dict[str, str] = {}
    heap: list[FreqTree] = []

    for char, freq in frequencies.value.items():
        heapq.heappush(heap, FreqTree(char, freq))

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        node = FreqTree(None, left.freq + right.freq)
        node.left = left
        node.right = right
        heapq.heappush(heap, node)

    root = heapq.heappop(heap)

    def traverse(node, encoding):
        if node.char:
            huffman_encoding[node.char] = encoding
        else:
            traverse(node.left, encoding + "0")
            traverse(node.right, encoding + "1")

    traverse(root, "")

    return huffman_encoding


def huffman_encode_message(message: str, encoding: Dict[str, str]) -> str:
    """
    Encodes a message using the given encoding.
    """
    encoded_message = []
    for char in message:
        if not char in encoding:
            raise ValueError()
        encoded_message.append(encoding[char])
    return "".join(encoded_message)


def huffman_decode_message(encoded_message: str, encoding: Dict[str, str]) -> str:
    """
    Decodes a message using the given encoding.
    """
    decoded_message = ""
    while encoded_message:
        dead = True
        for char, code in encoding.items():
            if encoded_message.startswith(code):
                dead = False
                decoded_message += char
                encoded_message = encoded_message[len(code) :]
        if dead:
            raise ValueError()
    return decoded_message


def huffman_coders(
    encoding: Dict[str, str]
) -> tuple[Callable[[str], str], Callable[[str], str]]:
    return lambda m: huffman_encode_message(
        m, encoding
    ), lambda m: huffman_decode_message(m, encoding)


def dict_coders() -> tuple[Callable[[str], str], Callable[[str], str]]:
    words = []
    word_index: dict[str, int] = {}
    # Word list sourced from https://github.com/first20hours/google-10000-english
    with open(path.join(path.dirname(__file__), "agent8", "dict.txt")) as dict_file:
        words = [word.strip() for word in dict_file]
        word_index = {word: i for i, word in enumerate(words)}

    bits_per_word = int(ceil(log2(len(word_index))))

    def encode(message: str) -> str:
        # assume lowercase words separated by spaces
        to_encode = message.lower().split()
        encoded = ""
        for word in to_encode:
            if not word in word_index:
                raise ValueError()
            encoded += pad(to_bit_string(word_index[word]), bits_per_word)
        return encoded

    def decode(message: str) -> str:
        decoded = []
        for off in range(0, len(message), bits_per_word):
            word_bits = message[off : off + bits_per_word]
            word_index = from_bit_string(word_bits)
            if word_index < 0 or word_index >= len(words):
                raise ValueError()
            decoded.append(words[word_index])
        return " ".join(decoded)

    return encode, decode


# ==============
# Bits <-> Cards
# ==============
def bottom_cards_encode(value: int, n: int) -> list[int]:
    if value >= factorial(n):
        raise ValueError(f"{value} is too large to encode in {n} cards!")

    cards = []
    current_value = 0
    digits = list(range(n))
    for i in range(n):
        # First n bins of (n-1)!, then n-1 bins of (n-2)!, and so on bin_width = factorial(n - i) // (n - i)
        bin_width = factorial(n - i) // (n - i)
        # Target value falls into one of these bins
        bin_no = (value - current_value) // bin_width
        # Of the cards still available, ordered by value, select the bin_no'th largest
        card_value = digits[bin_no]
        # Once a card has been used, it can't be used again
        digits = [digit for digit in digits if digit != card_value]
        cards.append(card_value)
        # Move to the bottom of the current bin
        current_value += bin_no * bin_width
    print('hehehe', cards)

    return cards


def bottom_cards_decode(cards: list[int], n: int) -> int:
    cards = [card for card in cards if card < n]
    # Assuming the top card is the first card in the list
    lo = 0
    hi = factorial(n)
    digits = list(range(n))
    for i in range(n):
        card_value = cards[i]
        # Range will always be divisible by the place value
        bin_width = (hi - lo) // (n - i)
        bin_no = digits.index(card_value)
        lo = lo + bin_no * bin_width
        hi = lo + bin_width
        digits = [digit for digit in digits if digit != card_value]

    return lo


def find_c_for_message(bits: str) -> int:
    # In practice, with an 8 bits checksum, this value is always > 5,
    for c in range(1, 52):
        if int(log2(factorial(c))) >= len(bits):
            return c
    return 0


def to_bit_string(value: int) -> str:
    """255 -> 11111111"""
    return bin(value)[2:]


def from_bit_string(bits: str) -> int:
    """11111111 -> 255"""
    return int("0b" + bits, 2)


# ===================
# Checksum Algorithms
# ===================
def quarter_sum_checksum(sent_message: str) -> str:
    k = int(((len(sent_message) / 4) + 1) // 1)

    # Dividing sent message in packets of k bits.
    c1 = sent_message[0:k]
    c2 = sent_message[k : 2 * k]
    c3 = sent_message[2 * k : 3 * k]
    c4 = sent_message[3 * k : 4 * k]

    # Calculating the binary sum of packets
    sum = bin(int(c1, 2) + int(c2, 2) + int(c3, 2) + int(c4, 2))[2:]

    # Adding the overflow bits
    if len(sum) > k:
        x = len(sum) - k
        sum = bin(int(sum[0:x], 2) + int(sum[x:], 2))[2:]
    if len(sum) < k:
        sum = "0" * (k - len(sum)) + sum

    # Calculating the complement of sum
    checksum = ""
    for i in sum:
        if i == "1":
            checksum += "0"
        else:
            checksum += "1"
    return checksum


# Create separate random instance with constant seed
# so that the pearson_table is always the same
random = Random(0)
pearson_table = list(range(256))
random.shuffle(pearson_table)


def pearson_checksum(bits: str) -> str:
    padding = 8 - (len(bits) % 8)
    padded_bits = "0" * padding + bits
    checksum = 0
    for off in range(0, len(padded_bits), 8):
        byte = padded_bits[off : off + 8]
        byte_val = from_bit_string(byte)
        checksum = pearson_table[checksum ^ byte_val]
    checksum_bits = to_bit_string(checksum)
    padded_checksum = pad(checksum_bits, CHECKSUM_BITS)
    return padded_checksum


def sha_checksum(bits: str, c: int) -> str:
    # Lowest c bits of sha269 hash
    bitstr = bytes(bits, "utf-8")
    hashstr = hashlib.sha256(bitstr).hexdigest()

    scale = 16  ## equals to hexadecimal
    num_of_bits = 8
    binstr = bin(int(hashstr, scale))[2:].zfill(num_of_bits)

    return binstr[-c:]


def extract_bit_fields(bits: str, format: list[int]) -> list[str]:
    """
    bits: encoded message bits
    format: list of field lengths, in reverse order with the LAST field FIRST in the list
    """
    fields = []
    current_offset = len(bits)
    for field_length in format:
        # Pad in case of very low numbers (leading 0's are trimmed by card encoding)
        fields.append(
            pad(bits[(current_offset - field_length) : current_offset], field_length)
        )
        current_offset -= field_length

    # The remaining bits (message content)
    fields.append(bits[:current_offset])
    return fields


def check_and_remove(bits: str) -> tuple[bool, int, str]:
    """Returns `(passed_checksum, encoding_id, message)`"""
    message_checksum, length_byte, encoding_bits, message = extract_bit_fields(
        pad(bits, CHECKSUM_BITS + LENGTH_BITS + ENCODING_BITS, allow_over=True),
        [CHECKSUM_BITS, LENGTH_BITS, ENCODING_BITS],
    )

    # Debug
    # print("all bits:", bits)
    # print("message checksum:", message_checksum)
    # print("length", length_byte)
    # print("encoding", encoding_bits)
    # print("message", message)

    message_length = from_bit_string(length_byte)
    encoding_id = from_bit_string(encoding_bits)

    if len(message) > message_length:
        return False, -1, ""

    # Pad message to target length with leading 0's
    message = pad(message, message_length, allow_over=True)
    checked_bits = message + encoding_bits + length_byte

    checked_checksum = sha_checksum(checked_bits, CHECKSUM_BITS)
    return checked_checksum == message_checksum, encoding_id, message


def length_byte(bits: str) -> str:
    length_bits = to_bit_string(len(bits))
    return pad(length_bits, 8)


def pad(message: str, length: int, allow_over=False):
    if len(message) > length and not allow_over:
        raise ValueError(
            f"Message to pad is length {len(message)}, longer than target length {length}: {message}"
        )
    needed_padding = length - len(message)
    return "0" * needed_padding + message


# ============
# Multiplexing
# ============
LOWERCASE_HUFFMAN = make_huffman_encoding(FrequencyDistribution.lowercase_and_space)
MIXED_HUFFMAN = make_huffman_encoding(FrequencyDistribution.letters_and_space)
ALPHANUM_HUFFMAN = make_huffman_encoding(
    FrequencyDistribution.letters_numbers_and_space
)
ASCII_HUFFMAN = make_huffman_encoding(FrequencyDistribution.ascii_printable)
NUMBER_HUFFMAN = make_huffman_encoding(FrequencyDistribution.numbers)

# [(encode, decode)]
# Encoding identifier denotes index in this list
CHARACTER_ENCODINGS: list[tuple[Callable[[str], str], Callable[[str], str]]] = [
    huffman_coders(LOWERCASE_HUFFMAN),
    huffman_coders(MIXED_HUFFMAN),
    huffman_coders(ALPHANUM_HUFFMAN),
    huffman_coders(ASCII_HUFFMAN),
    huffman_coders(NUMBER_HUFFMAN),
    dict_coders(),
]

CHECKSUM_BITS = 10
LENGTH_BITS = 8
ENCODING_BITS = max(int(ceil(log2(len(CHARACTER_ENCODINGS)))), 1)


def select_character_encoding(message: str) -> tuple[str, int]:
    """Select the shortest encoding for this message."""
    shortest_encoding = -1
    shortest_encoded: Optional[str] = None
    for encoding_index, (encode, _) in enumerate(CHARACTER_ENCODINGS):
        try:
            candidate_encoding = encode(message)
            if shortest_encoded is None or len(candidate_encoding) < len(
                shortest_encoded
            ):
                shortest_encoded = candidate_encoding
                shortest_encoding = encoding_index
        except ValueError:
            pass

    if shortest_encoded is None:
        raise ValueError(
            f"Could not encode message with any available encodings: {message}"
        )

    return shortest_encoded, shortest_encoding


class Agent:
    def __init__(self):
        self.frequencies = FrequencyDistribution.lowercase_and_space
        self.encoding = make_huffman_encoding(self.frequencies)

        self.total_decodes = 0
        self.failed_decodes = 0

    @property
    def failed_decode_rate(self):
        return self.failed_decodes / self.total_decodes

    def encode(self, message: str):
        print(message)
        try:
            encoded, encoding_id = select_character_encoding(message)
            print('encoded',encoded, type(encoded))
            
        except ValueError as e:
            # TODO: Lossy encoding when no encodings cover the message domain
            print(e)
            return list(range(52))
        print('message', message)
        message_length = length_byte(encoded)
        print('ml',message_length)
        encoding_bits = pad(to_bit_string(encoding_id), ENCODING_BITS)
        print('encoding_bits', encoding_bits)
        checked_bits = encoded + encoding_bits + message_length
        # Checksum checks all other bits
        checksum = sha_checksum(checked_bits, CHECKSUM_BITS)
        print('yerrrrrrrr',checksum)
        with_checksum = checked_bits + checksum
        print(with_checksum)
        c = find_c_for_message(with_checksum)
        print('ceeee', c)
        try:
            card_encoded = bottom_cards_encode(from_bit_string(with_checksum), c)
        except ValueError as e:
            # TODO: Lossy encoding when message length > available bits in card deck
            print(e)
            return list(range(52))

        # Debugging
        # print("Message:", encoded)
        # print("Encoding:", encoding_bits)
        # print("Length:", message_length)
        # print("Checksum:", checksum)
        # print("C:", c)

        return list(range(c, 52)) + card_encoded

    def decode(self, deck: list[int]):
        # Minimum 16 bit suffix for checksum + length
        # log2(9!) > 2 ^ 16
        for c in range(9, 52):
            encoded = [card for card in deck if card < c]
            decoded = to_bit_string(bottom_cards_decode(encoded, c))
            passes_checksum, encoding_id, message = check_and_remove(decoded)
            if passes_checksum:
                self.total_decodes += 1
                if encoding_id >= len(CHARACTER_ENCODINGS):
                    continue
                try:
                    _, decode = CHARACTER_ENCODINGS[encoding_id]
                    out_message = decode(message)
                    return out_message
                except ValueError:
                    self.failed_decodes += 1
                    print("Failed to decode:", deck)
        return "NULL"


def uniform_random_message(character_set: str, length: int) -> str:
    return "".join(random.choices(character_set, k=length))


def shuffle(n, deck):
    rng = np.random.default_rng()
    shuffles = rng.integers(0, 52, n)
    for pos in shuffles:
        top_card = deck[0]
        deck = deck[1:]
        deck = deck[:pos] + [top_card] + deck[pos:]
    return deck


if __name__ == "__main__":
    agent = Agent()

    for c in ascii_letters + digits + punctuation:
        deck = agent.encode(c)
        rted = agent.decode(deck)
        if rted != c:
            print("Failed to encode:", c)

    for n in range(1, 52):
        assert (
            bottom_cards_decode(bottom_cards_encode(factorial(n) - 1, n), n)
            == factorial(n) - 1
        )
        assert (
            bottom_cards_decode(bottom_cards_encode(factorial(n) // 2, n), n)
            == factorial(n) // 2
        )
        assert bottom_cards_decode(bottom_cards_encode(0, n), n) == 0
