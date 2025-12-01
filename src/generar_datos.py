import pandas as pd
import numpy as np
import os

# Configuración de la semilla para reproducibilidad
np.random.seed(42)

# Parámetros del escenario
NUM_CLIENTES = 20
NUM_VEHICULOS = 4
CAPACIDAD_VEHICULO = 100
ALMACEN_X, ALMACEN_Y = 0, 0
RANGO_COORDENADAS = 50  # km
HORIZONTE_TIEMPO = 480  # minutos (8 horas)

def generar_datos_clientes():
    print("Generando datos de clientes...")
    clientes = []
    
    # Agregar el almacén (Depósito) como el cliente 0
    clientes.append({
        'id': 0,
        'nombre': 'Almacén Central',
        'x': ALMACEN_X,
        'y': ALMACEN_Y,
        'demanda': 0,
        'tiempo_servicio': 0,
        'ventana_inicio': 0,
        'ventana_fin': HORIZONTE_TIEMPO
    })
    
    for i in range(1, NUM_CLIENTES + 1):
        x = np.random.randint(-RANGO_COORDENADAS, RANGO_COORDENADAS)
        y = np.random.randint(-RANGO_COORDENADAS, RANGO_COORDENADAS)
        demanda = np.random.randint(5, 20)  # Demanda entre 5 y 20 unidades
        tiempo_servicio = np.random.randint(10, 30) # Tiempo de descarga en minutos
        
        # Ventanas de tiempo (simplificado)
        # Inicio aleatorio en la primera mitad del día
        ventana_inicio = np.random.randint(0, HORIZONTE_TIEMPO // 2)
        # Fin debe ser al menos 60 mins después del inicio
        ventana_fin = np.random.randint(ventana_inicio + 60, HORIZONTE_TIEMPO)
        
        clientes.append({
            'id': i,
            'nombre': f'Cliente {i}',
            'x': x,
            'y': y,
            'demanda': demanda,
            'tiempo_servicio': tiempo_servicio,
            'ventana_inicio': ventana_inicio,
            'ventana_fin': ventana_fin
        })
        
    df_clientes = pd.DataFrame(clientes)
    output_path = os.path.join('data', 'clientes.csv')
    df_clientes.to_csv(output_path, index=False)
    print(f"Datos de clientes guardados en: {output_path}")
    return df_clientes

def generar_datos_vehiculos():
    print("Generando datos de vehículos...")
    vehiculos = []
    for k in range(1, NUM_VEHICULOS + 1):
        vehiculos.append({
            'id_vehiculo': k,
            'capacidad': CAPACIDAD_VEHICULO,
            'costo_km': 1.5  # Costo por kilómetro
        })
        
    df_vehiculos = pd.DataFrame(vehiculos)
    output_path = os.path.join('data', 'vehiculos.csv')
    df_vehiculos.to_csv(output_path, index=False)
    print(f"Datos de vehículos guardados en: {output_path}")
    return df_vehiculos

if __name__ == "__main__":
    # Asegurar que existe el directorio data
    if not os.path.exists('data'):
        os.makedirs('data')
        
    generar_datos_clientes()
    generar_datos_vehiculos()
    print("Generación de datos completada.")
