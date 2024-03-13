import hashlib

def get_hash(string: str) -> str:
    hash_object = hashlib.md5(string.encode("utf-8"))
    return hash_object.hexdigest()