# 🚚 Optimización de Rutas de Distribución (CVRP)

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Status](https://img.shields.io/badge/Status-Terminado-green)
![Library](https://img.shields.io/badge/Library-Google%20OR--Tools-orange)

## 📋 Descripción del Proyecto

Este proyecto implementa una solución algorítmica para el **Problema de Enrutamiento de Vehículos Capacitado (CVRP)** aplicado a un escenario de logística de última milla. 

El objetivo es optimizar las rutas de distribución de una flota de vehículos limitada para atender a un conjunto de clientes dispersos geográficamente, minimizando la distancia total recorrida y respetando las restricciones de capacidad de carga de cada vehículo.

El sistema utiliza **Google OR-Tools** para el cálculo matemático y **Matplotlib** para la visualización gráfica de las rutas resultantes.

## 🚀 Características Principales

* **Cálculo de Rutas Óptimas:** Minimización de costos de distancia euclidiana.
* **Restricciones de Capacidad:** Gestión inteligente de la carga máxima por vehículo (15 unidades).
* **Visualización Interactiva:** Generación de un mapa 2D con nodos (clientes/depósito) y arcos (rutas) diferenciados por colores.
* **Escalabilidad:** Código adaptable para modificar coordenadas, número de vehículos o demandas fácilmente.

## 🛠️ Tecnologías Utilizadas

* **Lenguaje:** Python 3.x
* **Motor de Optimización:** [Google OR-Tools](https://developers.google.com/optimization) (Constraint Solver).
* **Visualización:** Matplotlib.
* **Matemáticas:** Math & Scipy.

## 📦 Instalación y Uso

Sigue estos pasos para ejecutar el proyecto en tu máquina local:

1.  **Clonar el repositorio:**
    ```bash
    git clone [https://github.com/rmaneiro28/optimizacion-rutas-logistica-cvrp.git](https://github.com/rmaneiro28/optimizacion-rutas-logistica-cvrp.git)
    cd optimizacion-rutas-logistica-cvrp
    ```

2.  **Instalar dependencias:**
    Se recomienda usar un entorno virtual.
    ```bash
    pip install -r requirements.txt
    ```

3.  **Ejecutar el programa:**
    ```bash
    python optimizador_rutas.py
    ```

## 📊 Escenario de Prueba (Datos)

El script viene pre-configurado con un escenario ficticio:
* **Depósito Central:** Coordenada (20, 20).
* **Flota:** 4 Vehículos.
* **Clientes:** 16 puntos de entrega con demandas variables.
* **Capacidad por Vehículo:** 15 unidades.

## 📷 Resultados Visuales

El programa genera una ventana gráfica similar a esta descripción:
* **Cuadrado Rojo:** Representa el Almacén Central.
* **Círculos Azules:** Representan a los clientes (con etiquetas de ID y Demanda).
* **Líneas de Colores:** Representan la ruta exclusiva de cada vehículo.

*(Aquí puedes subir una captura de pantalla de la ventana que genera tu código y ponerla así: `![Mapa de Rutas](ruta_a_tu_imagen.png)`)*

## 📄 Estructura del Modelo Matemático

El problema se modela buscando minimizar la función objetivo:

$$Min Z = \sum_{k \in K} \sum_{i \in V} \sum_{j \in V} c_{ij} x_{ijk}$$

Sujeto a:
1.  Cada cliente es visitado exactamente una vez.
2.  El flujo de entrada y salida de cada nodo se conserva.
3.  La demanda acumulada en una ruta no excede la capacidad $Q$ del vehículo.

## ✒️ Autor

* **Rúbel Maneiro** - *Desarrollo e Implementación* - [Tu Perfil de GitHub](https://github.com/rmaneiro28)

---
*Proyecto realizado para la asignatura "Optimización de Sistemas de Información".*