import re
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

# Configuración de estilos
plt.style.use('seaborn-v0_8-darkgrid')  # Usando un estilo disponible

def decode_tahoe_rpm(payload):
    """Decodificación mejorada para RPM - Fórmula GM verificada"""
    if len(payload) >= 8:
        try:
            rpm = (int(payload[4:6], 16) * 256 + int(payload[6:8], 16)) / 4
            return rpm if 500 <= rpm <= 3000 else None
        except:
            return None
    return None

def decode_tahoe_speed(payload):
    """Decodificación mejorada para velocidad - Byte alternativo"""
    if len(payload) >= 6:
        try:
            # Probando byte en posición 4-6 que mostró variación en los logs
            speed = int(payload[4:6], 16) / 2  # División para ajustar escala
            return speed if 0 <= speed <= 180 else None
        except:
            return None
    return None

def decode_tahoe_temp(payload):
    """Decodificación mejorada para temperatura - Byte alternativo"""
    if len(payload) >= 6:
        try:
            # Probando byte en posición 2-4 que muestra variación en logs
            temp = int(payload[2:4], 16) - 60  # Offset ajustado
            return temp if 70 <= temp <= 110 else None
        except:
            return None
    return None

# Configuración de parámetros
target_ids = {
    'rpm': {'id': '1E5', 'decoder': decode_tahoe_rpm, 'color': '#FF6B6B', 'unit': 'RPM'},
    'speed': {'id': 'AA', 'decoder': decode_tahoe_speed, 'color': '#4ECDC4', 'unit': 'km/h'},
    'temp': {'id': '1C7', 'decoder': decode_tahoe_temp, 'color': '#45B7D1', 'unit': '°C'}
}

# Procesamiento de datos
data = {param: {'time': [], 'values': []} for param in target_ids}
stats = defaultdict(int)

print("Procesando datos con decodificadores mejorados...")

with open('00000001.log', 'r') as f:
    for line in f:
        if match := re.match(r'\((\d+\.\d+)\) can0 (\w+)#(\w+)', line):
            time, can_id, payload = match.groups()
            can_id = can_id.upper()
            stats[can_id] += 1
            
            for param, config in target_ids.items():
                if can_id == config['id']:
                    if value := config['decoder'](payload):
                        data[param]['time'].append(float(time))
                        data[param]['values'].append(value)

# Análisis de resultados
print("\n=== RESULTADOS MEJORADOS ===")
valid_messages = sum(len(v['values']) for v in data.values())
print(f"Datos válidos obtenidos: {valid_messages}")

for param in target_ids:
    if values := data[param]['values']:
        print(f"{param.upper()}: {len(values)} muestras | Min: {min(values):.1f} | Max: {max(values):.1f} | Avg: {np.mean(values):.1f}")

# Visualización mejorada
fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)

for ax, (param, config) in zip(axes, target_ids.items()):
    if data[param]['values']:
        # Gráfico principal
        ax.plot(data[param]['time'], data[param]['values'], 
               color=config['color'], linewidth=1.5, alpha=0.8, label='Datos')
        
        # Línea de promedio
        avg = np.mean(data[param]['values'])
        ax.axhline(avg, color='darkred', linestyle='--', linewidth=1, alpha=0.7)
        
        # Configuración visual
        ax.set_ylabel(config['unit'], fontsize=12)
        ax.set_title(f"{param.upper()} (ID {config['id']}) - {len(data[param]['values'])} muestras", 
                    pad=12, fontsize=13)
        ax.grid(True, alpha=0.4)
        
        # Leyenda de estadísticas
        stats_text = (f"Mín: {min(data[param]['values']):.1f}{config['unit']}\n"
                     f"Máx: {max(data[param]['values']):.1f}{config['unit']}\n"
                     f"Prom: {avg:.1f}{config['unit']}")
        ax.text(0.98, 0.95, stats_text, transform=ax.transAxes,
               ha='right', va='top', fontsize=10,
               bbox=dict(facecolor='white', alpha=0.8))

plt.xlabel('Tiempo (segundos)', fontsize=12)
plt.suptitle('Análisis de Datos CAN - Chevrolet Tahoe 2015\n(Decodificación Mejorada)', 
             y=0.98, fontsize=15, weight='bold')
plt.tight_layout()
plt.savefig('tahoe_improved_analysis.png', dpi=300, bbox_inches='tight')
print("\nGráfico guardado como 'tahoe_improved_analysis.png'")
