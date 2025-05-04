import os

def generate_so_with_secret(secret: str, filename: str) -> str:
    # Generate C code that embeds the secret
    c_code = f'''
    #include <stdio.h>

    const char* secret = "{secret}";

    void reveal_secret() {{
        printf("Secret is: %s\\n", secret);
    }}
    '''

    with open("temp.c", "w") as f:
        f.write(c_code)

    # Compile C code to .so file
    so_path = f"/tmp/{filename}"
    compile_command = f"gcc -shared -fPIC temp.c -o {so_path}"
    result = os.system(compile_command)

    if result != 0:
        raise RuntimeError("Failed to compile .so file")

    return so_path
