def hex_to_bin(hex_str):
    """Chuyển chuỗi Hex sang chuỗi Nhị phân (Binary String)"""
    num_bits = len(hex_str) * 4
    return bin(int(hex_str, 16))[2:].zfill(num_bits)

def bin_to_hex(bin_str):
    """Chuyển chuỗi Nhị phân sang chuỗi Hex (Viết hoa)"""
    hex_str = hex(int(bin_str, 2))[2:].upper()
    if len(hex_str) % 2 != 0:
        hex_str = '0' + hex_str
    return hex_str

def permute(input_bits, table):
    """Thực hiện hoán vị các bit dựa trên bảng tra"""
    output_bits = ""
    for position in table:
        output_bits += input_bits[position - 1]
    return output_bits

def xor_bits(bits1, bits2):
    """Thực hiện phép XOR giữa 2 chuỗi bit"""
    return ''.join('1' if b1 != b2 else '0' for b1, b2 in zip(bits1, bits2))

def int_to_bin(number, width):
    """Chuyển số nguyên sang chuỗi nhị phân với độ dài cố định"""
    return format(number, f'0{width}b')

def text_to_hex(text):
    """Chuyển văn bản ASCII sang Hex"""
    return text.encode('utf-8').hex().upper()

def xor_hex_strings(hex1, hex2):
    """
    [MỚI] XOR hai chuỗi Hex (Dùng cho trộn Key Components)
    Input: 2 chuỗi hex 16 ký tự
    Output: Chuỗi hex kết quả
    """
    int1 = int(hex1, 16)
    int2 = int(hex2, 16)
    result = int1 ^ int2
    return format(result, '016X')