#!/bin/bash
gcc -shared -o libsecret.so -fPIC key_writer.c
echo "libsecret.so built."
