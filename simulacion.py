import os
import random
import time


def proceso_vehiculo(
    id_vehiculo,
    semaforo,
    lock,
    evento_apertura,
    dentro,
    atendidos,
    recaudo,
    cola_eventos,
):
    pid = os.getpid()

    cola_eventos.put({
        "tipo": "creado",
        "vehiculo": id_vehiculo,
        "pid": pid,
    })

    # El proceso queda detenido hasta que se abra el parqueadero
    evento_apertura.wait()

    cola_eventos.put({
        "tipo": "esperando",
        "vehiculo": id_vehiculo,
        "pid": pid,
    })

    # Intenta obtener uno de los cupos disponibles
    semaforo.acquire()

    # Protege el acceso al contador compartido
    with lock:
        dentro.value += 1

    cola_eventos.put({
        "tipo": "entra",
        "vehiculo": id_vehiculo,
        "pid": pid,
    })

    # Simula el tiempo que el vehículo permanece estacionado
    tiempo_estacionado = random.uniform(3.0, 6.0)
    time.sleep(tiempo_estacionado)

    valor_pago = 5000

    # Protege la actualización de los datos compartidos
    with lock:
        dentro.value -= 1
        atendidos.value += 1
        recaudo.value += valor_pago

    cola_eventos.put({
        "tipo": "sale",
        "vehiculo": id_vehiculo,
        "pid": pid,
        "pago": valor_pago,
    })

    # Devuelve el permiso para que pueda entrar otro vehículo
    semaforo.release()