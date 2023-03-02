
#Este script utiliza un bucle while para verificar continuamente si la aplicación de la calculadora está en ejecución. Primero establece el nombre del proceso en "calc.exe" e inicializa una variable booleana calcup en False.
#Luego utiliza un bucle for para iterar sobre todos los procesos en ejecución en el sistema utilizando la función psutil.process_iter(). Para cada proceso, verifica si el nombre del proceso contiene "calc.exe" utilizando el método proc.name(). Si la aplicación de la calculadora está en ejecución, establece calcup en True.
#Si calcup todavía es False después de que se completa el bucle for, significa que la aplicación de la calculadora no está en ejecución. En este caso, utiliza la función os.startfile() para iniciar la aplicación de la calculadora.
#Finalmente, el script duerme durante un segundo utilizando la función time.sleep() antes de verificar nuevamente si la aplicación de la calculadora está en ejecución.




import os
import psutil
import time

while True:
    nombre_proceso = "calc.exe"
    calcup = False

    for proc in psutil.process_iter():
        if nombre_proceso in proc.name():
            calcup = True

    if calcup == False:
        os.startfile("calc.exe")

    time.sleep(1)
