# password-administrator

## ¿Por qué urlsafe_b64decode en lugar de b64decode normal?

Compatibilidad Multiplataforma: La variante segura para URL (que usa - y _ en lugar de + y /) es más portable entre diferentes sistemas operativos y servidores web, ya que estos caracteres tienen menos probabilidad de causar problemas

## Salt
- Valor random para que la derivacion de una key sea mas segura
- La salt se usa para prevenir ataques de rainbow table y asegurarse que la misma password no genere siempre la misma key
- Una rainbow table es una tabla pre computada usada para encontrar contraseñas. Contiene una gran cantidad de contraseñas comunes y sus respectivos hashes.

### Como funcionan las  <span style="color:red">R</span><span style="color:orange">a</span><span style="color:yellow">i</span><span style="color:green">n</span><span style="color:blue">b</span><span style="color:indigo">o</span><span style="color:violet">w</span>:
1. Atacantes calculan los hashes para millones de contraseñas comunes
2. Las guardan en estas tablas.
3. Cuando consiguen una base de datos de contraseñas hasheadas, pueden rapidamente buscarlas en la rainbow table.

    **Ejemplo sin salt:**
    ```
    Password: "password123"
    Hash: "ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f"
    ```
    Si este hash aparece en una tabla, el atacante inmediatamente sabe que la pass es "password123"

    **Ejemplo con Salts:**
    ```
    Password: "password123"
    Salt 1: "abc123"
    Hash 1: "7f8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f..."

    Password: "password123"
    Salt 2: "xyz789"
    Hash 2: "1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d..."
    ```
    Ahora el atacante necesitaria una tabla para cada posible valor de la salt, lo cual es computacionalmente imposible porque:
    - Con un salt de 16-bytes hay 2^128 posibles combinaciones
    - Crear y mantener una tabla con cada valor posible de salt requeriria una enorme cantidad de almacenamiento y compouto

## Nonce
- Contador para el metodo de cifrado en bloques CTR. Eg numero arbritario grande y le vas sumando 1 por bloque que queres encriptar.
- Tambien se usa en Galois Counter Mode (GCM)
- [Diapositivas 21-22 de Clase Cifrado Simétrico (Alesio)](https://miel.unlam.edu.ar/data7/data2/contenido/3662/Clase-Cifrado-Simetrico.pdf)

## Backend para derive_key
- Es para usar el default del sistema operativo para operaciones criptograficas, permitiendo que el programa sea multiplataforma

## Tag & finalize
- finalize() completa el cifrado
- Asegura que toda la info haya sido cifrada de manera correcta
- En modo GCM, genera la tag de autenticacion
- Esto es la parte de autenticacion que ofrece GCM
- La func es similar:
    - Cerrar un file despues de escribir en el
    - Finalizar una transaccion en una db