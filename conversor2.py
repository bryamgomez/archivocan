from asammdf import MDF

# Paso 1: Convertir MF4 a ASC
print("Iniciando conversión de MF4 a ASC...")

input_mf4 = "00000001.MF4"
output_asc = "00000001.asc"

mdf = MDF(input_mf4)
mdf.export(fmt="asc", filename=output_asc)

print(f"Conversión completada: {output_asc}")

# Paso 2: Convertir ASC a formato candump
print("Iniciando conversión de ASC a LOG (candump)...")

input_asc = output_asc
output_log = "00000001.log"

with open(input_asc, "r") as f_in, open(output_log, "w") as f_out:
    for line in f_in:
        if " Rx " in line and " d " in line:
            try:
                parts = line.strip().split()
                timestamp = parts[0]
                can_id = parts[2]
                d_index = parts.index("d")
                data_bytes = parts[d_index + 1:]
                data = ''.join(data_bytes)
                f_out.write(f"({timestamp}) can0 {can_id}#{data}\n")
            except Exception as e:
                print("Error procesando línea:", line.strip())

print(f"Conversión completada: {output_log}")
