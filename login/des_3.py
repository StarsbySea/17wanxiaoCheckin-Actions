'''
Dependencies:
    Package pycryptodome
Purpose:
    Encrypting a dict after converting it to a string
    Decrypt a string and convert it to a dict
    Use DES3's MODE_CBC to encrypt and decrypt
'''
import base64
import json
import random
from Crypto.Cipher import DES3
from Crypto.Util.Padding import pad, unpad


def get_random_digits(num):
    '''
    parameters: Number of random digits to be generated
    return: (string)random_number
    '''
    digits = ""
    for i in range(num):
        digit = chr(random.randrange(ord('0'), ord('9') + 1))
        digits += digit
    return digits


def des_3_encrypt(text, key, iv):
    '''
    Parameters:
        text (string)
        key (byte string) - The secret key used in symmetric ciphers.
                            It must be 16 or 24 bytes long. The parity bit is ignored.
        iv (byte string) - The initialization vector to be used for encryption or decryption.
    Return：
        ciphertext (byte string)
    '''
    cipher = DES3.new(key, DES3.MODE_CBC, iv.encode("utf-8"))
    ct_bytes = cipher.encrypt(pad(text.encode('utf8'), DES3.block_size))
    ciphertext = base64.b64encode(ct_bytes).decode('utf8')
    return ciphertext


def des_3_decode(text, key, iv):
    '''
    Parameters:
        text (string)
        key (byte string)
        iv (byte string)
    Return：
        plaintext (byte string)
    '''
    ciphertext = base64.b64decode(text)
    cipher = DES3.new(key.encode('utf-8'), DES3.MODE_CBC, iv.encode('utf-8'))
    plaintext = unpad(cipher.decrypt(ciphertext), DES3.block_size)
    return plaintext


def object_encrypt(dict_to_encrypt, key, iv):
    '''
    Parameters:
        dict_to_encrypt (dict)
        key (byte string)
        iv (byte string) - 8 bits.
    Return：
        ciphertext (byte string)
    '''
    return des_3_encrypt(json.dumps(dict_to_encrypt), key, iv)


def object_decrypt(string_to_decrypt, key, iv):
    '''
    Parameters:
        string_to_decrypt (string)
        key (byte string)
        iv (byte string) - 8 bits.
    Return：
        plaintext (byte string)
    '''
    string_to_decrypt = string_to_decrypt.replace('\n', '')
    return json.loads(des_3_decode(string_to_decrypt, key, iv))
