import copy
from optimize import create_data_model, solve_vrp

def run_scenario(scenario_name, data_override=None):
    print(f"\n--- Ejecutando Escenario: {scenario_name} ---")
    data = create_data_model()
    
    if data_override:
        for key, value in data_override.items():
            data[key] = value
            
    solution, routing, manager = solve_vrp(data)
    
    if solution:
        total_distance = solution.ObjectiveValue() / 100 # Convertir a unidades reales
        print(f"Solución encontrada. Distancia Total: {total_distance:.2f}")
        return total_distance
    else:
        print("No se encontró solución.")
        return None

def main():
    results = {}
    
    # Escenario Base
    results['Base (4 Vehículos, Cap 100)'] = run_scenario("Base")
    
    # Escenario 1: Reducir flota a 3 vehículos
    # Nota: Esto podría hacer el problema infactible si la demanda total > capacidad total
    # o si las ventanas de tiempo son muy ajustadas.
    results['Flota Reducida (3 Vehículos)'] = run_scenario(
        "Flota Reducida", 
        {'num_vehicles': 3, 'vehicle_capacities': [100] * 3}
    )
    
    # Escenario 2: Aumentar capacidad a 150
    results['Mayor Capacidad (Cap 150)'] = run_scenario(
        "Mayor Capacidad", 
        {'vehicle_capacities': [150] * 4}
    )
    
    print("\n\n=== Resumen de Análisis de Sensibilidad ===")
    print(f"{'Escenario':<30} | {'Distancia Total':<15}")
    print("-" * 50)
    for scenario, distance in results.items():
        dist_str = f"{distance:.2f}" if distance is not None else "Infactible"
        print(f"{scenario:<30} | {dist_str:<15}")

if __name__ == "__main__":
    main()
