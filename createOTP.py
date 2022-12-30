# Abre un archivo en modo escritura
with open('otp.txt', 'w') as f:
  # Itera sobre todos los números entre 1 y 999999
  for i in range(1, 1000000):
    # Convierte el número a una cadena de 6 dígitos con ceros a la izquierda
    otp = str(i).zfill(6)
    # Escribe el OTP en el archivo
    f.write(otp + '\n')
