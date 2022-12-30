import random
#Generar códigos nros. largo 6 dígitos.
codigos = []
with open("codigos.txt", "w") as f:
    for i in range(1000):
        codigo_aleatorio = str(random.randint(0, 999999)).zfill(6)
        codigos.append(codigo_aleatorio)
        f.write(codigo_aleatorio + "\n")
