import re
from collections import defaultdict
import matplotlib.pyplot as plt

def extract_can_ids(log_file):
    """Analiza el archivo de log y extrae todos los IDs CAN con estadísticas"""
    id_stats = defaultdict(lambda: {'count': 0, 'payloads': defaultdict(int)})
    total_lines = 0

    print(f"Analizando archivo: {log_file}")
    
    with open(log_file, 'r') as f:
        for line in f:
            total_lines += 1
            match = re.match(r'\([\d\.]+\) can0 (\w+)#(\w+)', line)
            if match:
                can_id = match.group(1).upper()
                payload = match.group(2).upper()
                id_stats[can_id]['count'] += 1
                id_stats[can_id]['payloads'][payload] += 1

    # Ordenar por frecuencia descendente
    sorted_ids = sorted(id_stats.items(), key=lambda x: x[1]['count'], reverse=True)
    
    return {
        'total_lines': total_lines,
        'unique_ids': len(id_stats),
        'id_stats': dict(sorted_ids)
    }

def print_id_report(analysis):
    """Muestra un reporte detallado de los IDs encontrados"""
    print(f"\n=== RESUMEN DE ANÁLISIS CAN ===")
    print(f"Líneas totales: {analysis['total_lines']}")
    print(f"IDs CAN únicos encontrados: {analysis['unique_ids']}")
    
    print("\nTop 20 IDs más frecuentes:")
    print("{:<8} {:<10} {:<15} {:<10}".format("ID", "Count", "% del total", "Payloads únicos"))
    print("-" * 45)
    
    for can_id, data in list(analysis['id_stats'].items())[:20]:
        percent = (data['count'] / analysis['total_lines']) * 100
        unique_payloads = len(data['payloads'])
        print("{:<8} {:<10} {:<15.2f} {:<10}".format(
            can_id, data['count'], percent, unique_payloads))

def plot_id_frequency(analysis, top_n=20):
    """Genera gráfico de frecuencia de IDs"""
    top_ids = list(analysis['id_stats'].items())[:top_n]
    ids = [x[0] for x in top_ids]
    counts = [x[1]['count'] for x in top_ids]
    
    plt.figure(figsize=(12, 6))
    bars = plt.bar(ids, counts, color='#2c7fb8')
    
    # Añadir etiquetas
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:,}',
                ha='center', va='bottom', fontsize=8)
    
    plt.title(f'Top {top_n} IDs CAN por frecuencia (Total: {analysis["total_lines"]} mensajes)')
    plt.xlabel('ID CAN')
    plt.ylabel('Número de mensajes')
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('can_ids_frequency.png', dpi=150)
    print("\nGráfico de frecuencia guardado como 'can_ids_frequency.png'")

def save_payload_samples(analysis, output_file='payload_samples.txt'):
    """Guarda muestras de payloads para cada ID"""
    with open(output_file, 'w') as f:
        f.write("Muestras de payloads por ID CAN:\n")
        f.write("="*50 + "\n")
        for can_id, data in analysis['id_stats'].items():
            f.write(f"\nID: {can_id} (Count: {data['count']}, Payloads únicos: {len(data['payloads'])})\n")  # Paréntesis corregido aquí
            for payload, count in list(data['payloads'].items())[:5]:  # Muestra 5 payloads por ID
                f.write(f"  {payload} (count: {count})\n")
    print(f"\nMuestras de payloads guardadas en '{output_file}'")

# Ejecutar análisis
if __name__ == "__main__":
    log_file = '00000001.log'  # Cambia esto si tu archivo tiene otro nombre
    analysis = extract_can_ids(log_file)
    
    print_id_report(analysis)
    plot_id_frequency(analysis)
    save_payload_samples(analysis)
