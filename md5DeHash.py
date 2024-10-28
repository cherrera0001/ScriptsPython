# El hash MD5 que queremos descifrar
hash_objetivo = "hash_Encontrado"  # Reemplaza con tu hash

# Cargar el archivo de diccionario
with open("diccionario.txt", "r") as diccionario:
    for linea in diccionario:
        # Quitar espacios en blanco o saltos de línea
        palabra = linea.strip()

        # Crear hash MD5 de la palabra
        hash_palabra = hashlib.md5(palabra.encode()).hexdigest()

        # Comparar el hash generado con el hash objetivo
        if hash_palabra == hash_objetivo:
            print(f"¡Texto original encontrado!: {palabra}")
            break
    else:
        print("No se encontró coincidencia en el diccionario.")
