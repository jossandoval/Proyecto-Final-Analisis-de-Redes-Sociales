import csv

INPUT_FILES = ['COVID19MEXICO2020.csv', 'COVID19MEXICO2021.csv']
OUTPUT_FILE = 'COVID19MEXICO2020_2021_CDMX.csv'
SELECTED_COLUMNS = [
    'CLASIFICACION_FINAL',
    'ENTIDAD_RES',
    'MUNICIPIO_RES',
    'TIPO_PACIENTE',
    'FECHA_INGRESO',
    'FECHA_SINTOMAS',
]
POSITIVE_VALUES = {'1', '2', '3'}
CDMX_CODE = '09'


def normalize_entidad(entidad_res):
    if entidad_res is None:
        return ''
    value = entidad_res.strip()
    if value.isdigit():
        return value.zfill(2)
    return value.upper()


def cargar_y_filtrar(ruta):
    registros = []
    with open(ruta, encoding='utf-8-sig', newline='') as csvfile:
        lector = csv.DictReader(csvfile)
        for fila in lector:
            clasificacion = fila.get('CLASIFICACION_FINAL', '').strip()
            entidad = normalize_entidad(fila.get('ENTIDAD_RES', ''))
            if clasificacion not in POSITIVE_VALUES:
                continue
            if entidad != CDMX_CODE:
                continue
            registro = {col: fila.get(col, '').strip() for col in SELECTED_COLUMNS}
            registros.append(registro)
    return registros


def main():
    registros = []
    for ruta in INPUT_FILES:
        registros.extend(cargar_y_filtrar(ruta))

    if not registros:
        print('No se encontraron registros válidos para CDMX y casos positivos.')
        return

    with open(OUTPUT_FILE, 'w', encoding='utf-8', newline='') as salida:
        escritor = csv.DictWriter(salida, fieldnames=SELECTED_COLUMNS)
        escritor.writeheader()
        escritor.writerows(registros)

    print(f'Archivo generado: {OUTPUT_FILE} con {len(registros)} registros.')


if __name__ == '__main__':
    main()
