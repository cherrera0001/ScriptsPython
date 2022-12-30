# Crea una lista vacía para almacenar los códigos
codes = []

# Abre el archivo en modo lectura
with open('otp.txt', 'r') as f:
  # Lee todas las líneas del archivo
  lines = f.readlines()
  # Itera sobre cada línea
  for line in lines:
    # Elimina el salto de línea al final de la línea
    line = line.strip()
    # Agrega el código a la lista
    codes.append(line)

# Imprime la lista de códigos
print(codes,'\n')
