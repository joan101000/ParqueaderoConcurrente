# Parqueadero Concurrente

Proyecto desarrollado en Python para representar el funcionamiento de un parqueadero utilizando procesos y mecanismos de sincronización.

Cada vehículo se representa mediante un proceso independiente y el parqueadero tiene una capacidad de cuatro puestos.

## Funcionamiento

Cuando se prepara la simulación, los procesos de los vehículos son creados y quedan esperando hasta que se abre el parqueadero.

Al abrirlo, los vehículos intentan ingresar. Como solo existen cuatro puestos, máximo cuatro vehículos pueden estar dentro al mismo tiempo y los demás deben esperar hasta que se libere un espacio.

Durante la simulación también se actualizan datos como los vehículos dentro, los vehículos atendidos y el recaudo.

## Mecanismos utilizados

- `Process`: crea un proceso independiente para cada vehículo.
- `Event`: controla el momento en que se abre el parqueadero.
- `Semaphore`: limita la cantidad de vehículos que pueden entrar al mismo tiempo.
- `Lock`: protege los datos compartidos.
- `Value`: almacena valores compartidos entre procesos.
- `Queue`: permite enviar información desde los procesos hacia la interfaz.

## Interfaz

La interfaz permite visualizar:

- Los cuatro puestos del parqueadero.
- Los vehículos que están dentro.
- Los vehículos que están esperando.
- El PID de cada proceso.
- Los espacios disponibles.
- Los vehículos atendidos.
- El recaudo total.

## Requisitos

- Python 3
- CustomTkinter

Para instalar CustomTkinter:

```bash
pip install customtkinter
