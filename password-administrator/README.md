# password-administrator

## Why urlsafe_b64decode instead normal b64decode?

Cross-Platform Compatibility: The URL-safe variant (which uses - and _ instead of + and /) is more portable across different operating systems and web servers, as these characters are less likely to cause issues with

## Salt
- A salt is a random value that's used to make the key derivation process more secure
- The salt is used to prevent rainbow table attacks and ensure that the same password doesn't always produce the same key
- A rainbow table is a precomputed table used in password cracking that contains a large number of possible password hashes and their corresponding plaintext passwords

### How  <span style="color:red">R</span><span style="color:orange">a</span><span style="color:yellow">i</span><span style="color:green">n</span><span style="color:blue">b</span><span style="color:indigo">o</span><span style="color:violet">w</span> Tables Work:
1. Attackers precompute hashes for millions/billions of common passwords
2. They store these in a table (the "rainbow table")
3. When they get a database of hashed passwords, they can quickly look up the hashes in their table to find the original passwords

    **Example of the Problem Without Salts:**
    ```
    Password: "password123"
    Hash: "ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f"
    ```
    If this hash appears in a rainbow table, the attacker immediately knows the password is "password123"

    **Example With Salts:**
    ```
    Password: "password123"
    Salt 1: "abc123"
    Hash 1: "7f8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f..."

    Password: "password123"
    Salt 2: "xyz789"
    Hash 2: "1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d..."
    ```

    Now the attacker would need a separate rainbow table for each possible salt value, which is computationally infeasible because:
    - There are 2^128 possible 16-byte salts (as used in this code)
    - Creating a rainbow table for each possible salt would require an enormous amount of storage and computation
    - It's much more efficient to try to crack passwords one at a time using the known salt

## Nonce
- Contador para el metodo de cifrado en bloques CTR. Eg numero arbritario grande y le vas sumando 1 por bloque.
- Tambien se usa en Galois Counter Mode (GCM)
- [Diapositivas 21-22 de Clase Cifrado Simétrico (Alesio)](https://miel.unlam.edu.ar/data7/data2/contenido/3662/Clase-Cifrado-Simetrico.pdf)

## Backend
- Uses default system's mode of operation for crypto operations.
- Allows multiplatform.

## Tag & finalize
- finalize() completes the encryption process
- It ensures all data has been properly encrypted
- It generates the authentication tag (in GCM mode)
- The tag is what allows the authentication part of GCM.
- It's similar to:
    - Closing a file after writing to it
    - Finalizing a transaction in a database