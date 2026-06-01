import csv

INPUT_FILE = 'afluenciastc_simple_04_2026.csv'
OUTPUT_FILE = 'afluenciastc_2020_2021.csv'
YEARS = {'2020', '2021'}


def filtrar_metros_por_anio(ruta):
    registros = []
    with open(ruta, encoding='utf-8', newline='') as csvfile:
        lector = csv.DictReader(csvfile)
        for fila in lector:
            anio = fila.get('anio', '').strip()
            if anio in YEARS:
                registros.append(fila)
    return lector.fieldnames, registros


def main():
    fieldnames, registros = filtrar_metros_por_anio(INPUT_FILE)
    if not registros:
        print('No se encontraron registros para 2020 y 2021.')
        return

    with open(OUTPUT_FILE, 'w', encoding='utf-8', newline='') as salida:
        escritor = csv.DictWriter(salida, fieldnames=fieldnames)
        escritor.writeheader()
        escritor.writerows(registros)

    print(f'Archivo generado: {OUTPUT_FILE} con {len(registros)} registros para {sorted(YEARS)}.')


if __name__ == '__main__':
    main()
