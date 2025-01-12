import csv
import subprocess
import sys
import os
import time
import ctypes


# Función para verificar permisos de administrador
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False


# Función para ejecutar un comando y verificar si tuvo éxito
def run_command(command):
    try:
        result = subprocess.run(command, check=True, shell=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error ejecutando el comando: {command}")
        print(f"Detalles del error: {e}")
        return False


# Función para verificar si Chocolatey está instalado
def check_chocolatey():
    try:
        subprocess.run("choco -v", check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Chocolatey ya está instalado.")
    except subprocess.CalledProcessError:
        print("Chocolatey no está instalado. Instalando Chocolatey...")
        install_chocolatey()


# Función para instalar Chocolatey
def install_chocolatey():
    # Comando para instalar Chocolatey
    command = (
        'Set-ExecutionPolicy Bypass -Scope Process -Force; '
        '[System.Net.ServicePointManager]::SecurityProtocol = '
        '[System.Net.ServicePointManager]::SecurityProtocol -bor 3072; '
        'iex ((New-Object System.Net.WebClient).DownloadString('
        '"https://community.chocolatey.org/install.ps1"))'
    )
    run_command(f"powershell -Command \"{command}\"")
    print("Chocolatey instalado con éxito.")


# Función para instalar programas desde el CSV
def install_from_csv(csv_file):
    if not os.path.exists(csv_file):
        # Si el CSV no existe, lo creamos con encabezados y ejemplo de 7zip
        print(f"El archivo {csv_file} no existe. Creando un archivo nuevo con ejemplo...")
        with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['ProgramName', 'InstallOrder', 'InstallCommand', 'SkipFlag'])
            # Ejemplo de instalación de 7zip usando Chocolatey
            writer.writerow(['7zip', 1, 'choco install 7zip -y', 'false'])
        print(f"Archivo {csv_file} creado con ejemplo.")
        return

    with open(csv_file, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        programs = list(reader)

        if not programs:
            print("No hay programas para instalar en el archivo CSV.")
            return

        for row in programs:
            name = row['ProgramName']
            install_order = row['InstallOrder']
            command = row['InstallCommand']
            skip_flag = row['SkipFlag'].strip().lower() == 'true'

            # Si el programa tiene la flag de omisión, lo saltamos
            if skip_flag:
                print(f"Saltando la instalación de {name} según la configuración.")
                continue

            print(f"Iniciando instalación de {name} (Orden: {install_order})...")

            # Ejecutamos el comando de instalación
            success = run_command(command)

            if not success:
                print(f"Error al instalar {name}, deteniendo el proceso.")
                break  # Detener el proceso si hubo un error

            time.sleep(1)  # Esperar un segundo entre instalaciones

        print("Todas las instalaciones han sido procesadas.")


def main():
    if not is_admin():
        print("Este programa requiere permisos de administrador.")
        input("Presiona una tecla para salir...")
        sys.exit(1)

    # Verificar si Chocolatey está instalado, si no, instalarlo
    check_chocolatey()

    # Ruta al archivo CSV que contiene la información
    csv_file = 'install_list.csv'

    # Ejecutamos la instalación desde el CSV
    install_from_csv(csv_file)

    print("Proceso de instalación finalizado.")


if __name__ == '__main__':
    main()
