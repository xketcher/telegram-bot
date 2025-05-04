import os
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

def pad(data):
    pad_len = 16 - (len(data) % 16)
    return data + bytes([pad_len] * pad_len)

def xor_split(key, xor_val=0xAA):
    return ', '.join(f'0x{b ^ xor_val:02x}' for b in key)

def bytes_to_c_array(data):
    return ', '.join(f'0x{b:02x}' for b in data)

def generate_secure_so(secret_key: str, filename: str) -> str:
    aes_key = get_random_bytes(32)
    iv = get_random_bytes(16)

    cipher = AES.new(aes_key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(secret_key.encode()))

    key_blob = xor_split(aes_key)
    iv_blob = bytes_to_c_array(iv)
    enc_blob = bytes_to_c_array(encrypted)

    c_code = f'''
    #include <stdio.h>
    #include <openssl/evp.h>
    #include <string.h>
    #include <stdlib.h>

    void handleErrors() {{
        fprintf(stderr, "Decryption error\\n");
        exit(1);
    }}

    void reveal_secret() {{
        unsigned char enc_data[] = {{{enc_blob}}};
        unsigned char iv[] = {{{iv_blob}}};
        unsigned char xor_key[] = {{{key_blob}}};
        unsigned char key[32];
        for (int i = 0; i < 32; i++) {{
            key[i] = xor_key[i] ^ 0xAA;
        }}

        EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
        unsigned char plaintext[128];
        int len, plaintext_len;

        if (!EVP_DecryptInit_ex(ctx, EVP_aes_256_cbc(), NULL, key, iv))
            handleErrors();
        if (!EVP_DecryptUpdate(ctx, plaintext, &len, enc_data, sizeof(enc_data)))
            handleErrors();
        plaintext_len = len;

        if (!EVP_DecryptFinal_ex(ctx, plaintext + len, &len))
            handleErrors();
        plaintext_len += len;
        plaintext[plaintext_len] = 0;

        printf("Secret is: %s\\n", plaintext);
        EVP_CIPHER_CTX_free(ctx);
    }}
    '''

    with open("secure_temp.c", "w") as f:
        f.write(c_code)

    so_path = f"/tmp/{filename}"
    compile_cmd = f"gcc -shared -fPIC secure_temp.c -o {so_path} -lcrypto"
    if os.system(compile_cmd) != 0:
        raise RuntimeError("Failed to compile secure .so")

    return so_path
