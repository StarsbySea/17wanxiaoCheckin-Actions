'''
Dependencies:
    Module hashlib
Uses:
    Calculates the sha256 of a string
    Returns the encoded value in hexadecimal
'''
import hashlib


def sha256(string):
    '''
    Parameters:
    The string to be calculated
    Return:
    Sha256 value in hexadecimal code
    '''
    sha1_object = hashlib.sha256()
    sha1_object.update(str(string))
    return sha1_object.hexdigest()
