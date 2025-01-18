import csv
import subprocess
import sys
import os
import time
import ctypes
import winreg
from pathlib import Path


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False


def create_directory_if_not_exists(path):
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creando directorio {path}: {e}")
        return False


def modify_registry_key(key_path, name, value, key_type=winreg.REG_EXPAND_SZ):
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, name, 0, key_type, value)
        return True
    except Exception as e:
        print(f"Error modificando registro {key_path}\\{name}: {e}")
        return False


def change_shell_folders():
    folders_to_modify = {
        "Desktop": "D:\\Desktop",
        "Personal": "D:\\Documents",
        "My Music": "D:\\Music",
        "My Pictures": "D:\\Pictures",
        "My Video": "D:\\Videos",
        "{374DE290-123F-4565-9164-39C4925E467B}": "D:\\Downloads",
        "Downloads": "D:\\Downloads"
    }

    registry_paths = [
        "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\User Shell Folders",
        "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Shell Folders"
    ]

    # Crear directorios primero
    for folder_path in folders_to_modify.values():
        if not create_directory_if_not_exists(folder_path):
            return False

    # Modificar registros
    for registry_path in registry_paths:
        for folder_name, folder_path in folders_to_modify.items():
            if not modify_registry_key(registry_path, folder_name, folder_path):
                return False

    # Cambiar USERPROFILE
    username = os.environ.get('USERNAME')
    new_profile_path = f"D:\\Users\\{username}"
    create_directory_if_not_exists(new_profile_path)

    try:
        import win32con
        import win32api
        win32api.RegSetValueEx(
            win32api.RegOpenKey(
                win32con.HKEY_CURRENT_USER,
                "Environment",
                0,
                win32con.KEY_SET_VALUE
            ),
            "USERPROFILE",
            0,
            win32con.REG_EXPAND_SZ,
            new_profile_path
        )
    except Exception as e:
        print(f"Error cambiando USERPROFILE: {e}")
        return False

    print(
        "\nCambios en las carpetas completados. Es necesario cerrar sesión para aplicar los cambios.")
    return True


def run_command(command):
    try:
        process = subprocess.run(command, shell=True, text=True,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if process.returncode != 0:
            print(f"\nError ejecutando el comando: {command}")
            print(f"Código de salida: {process.returncode}")
            print(f"Salida de error:")
            print(process.stderr)
            print(f"Salida estándar:")
            print(process.stdout)
            return False
        return True
    except subprocess.CalledProcessError as e:
        print(f"\nError ejecutando el comando: {command}")
        print(f"Código de salida: {e.returncode}")
        print(f"Salida de error: {e.stderr if hasattr(e, 'stderr') else 'No disponible'}")
        return False
    except Exception as e:
        print(f"\nError inesperado ejecutando el comando: {command}")
        print(f"Detalles del error: {str(e)}")
        return False


def set_execution_policy():
    command = "powershell -Command Set-ExecutionPolicy AllSigned -Force"
    return run_command(command)


def check_chocolatey():
    try:
        subprocess.run("choco -v", check=True, shell=True, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
        print("Chocolatey ya está instalado.")
        return True
    except subprocess.CalledProcessError:
        print("Chocolatey no está instalado. Instalando Chocolatey...")
        return install_chocolatey()


def install_chocolatey():
    if not set_execution_policy():
        print("Error al configurar la política de ejecución")
        return False

    command = (
        'powershell -Command "'
        '[System.Net.ServicePointManager]::SecurityProtocol = '
        '[System.Net.ServicePointManager]::SecurityProtocol -bor 3072; '
        'iex ((New-Object System.Net.WebClient).DownloadString('
        "'https://community.chocolatey.org/install.ps1'))\"")

    if run_command(command):
        print("Chocolatey instalado con éxito.")
        return True
    return False


def install_from_csv(csv_file):
    if not os.path.exists(csv_file):
        print(f"El archivo {csv_file} no existe. Creando un archivo nuevo con ejemplo...")
        with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['ProgramName', 'InstallOrder', 'InstallCommand', 'SkipFlag'])
            writer.writerow(['7zip', 1, 'choco install 7zip -y', 'false'])
        print(f"Archivo {csv_file} creado con ejemplo.")
        input("\nPresiona Enter para continuar...")
        return

    try:
        with open(csv_file, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            programs = sorted(list(reader), key=lambda x: int(x['InstallOrder']))

            if not programs:
                print("No hay programas para instalar en el archivo CSV.")
                input("\nPresiona Enter para continuar...")
                return

            for row in programs:
                if row['SkipFlag'].strip().lower() == 'true':
                    print(
                        f"Saltando la instalación de {row['ProgramName']} según la configuración.")
                    continue

                print(
                    f"\nIniciando instalación de {row['ProgramName']} (Orden: {row['InstallOrder']})...")
                try:
                    if not run_command(row['InstallCommand']):
                        print(f"Error al instalar {row['ProgramName']}.")
                        print("¿Deseas continuar con las siguientes instalaciones?")
                        choice = input(
                            "Presiona 'S' para continuar o cualquier otra tecla para detener: ")
                        if choice.lower() != 's':
                            print("\nProceso de instalación detenido por el usuario.")
                            input("\nPresiona Enter para volver al menú principal...")
                            return
                except Exception as e:
                    print(f"Error inesperado instalando {row['ProgramName']}: {str(e)}")
                    print("¿Deseas continuar con las siguientes instalaciones?")
                    choice = input(
                        "Presiona 'S' para continuar o cualquier otra tecla para detener: ")
                    if choice.lower() != 's':
                        print("\nProceso de instalación detenido por el usuario.")
                        input("\nPresiona Enter para volver al menú principal...")
                        return
                time.sleep(1)

            print("\nTodas las instalaciones han sido procesadas.")
            input("\nPresiona Enter para volver al menú principal...")

    except Exception as e:
        print(f"\nError leyendo el archivo CSV: {str(e)}")
        input("\nPresiona Enter para volver al menú principal...")


def setup_store_apps_location():
    try:
        new_path = "D:\\ProgramasWindowsApps"
        create_directory_if_not_exists(new_path)

        # Crear archivo .reg temporal
        reg_content = f"""Windows Registry Editor Version 5.00

[HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Appx]
"PackageRoot"="{new_path}"
"""

        temp_reg_file = os.path.join(os.environ['TEMP'], 'store_location.reg')
        with open(temp_reg_file, 'w') as f:
            f.write(reg_content)

        # Ejecutar el archivo .reg
        command = f'regedit /s "{temp_reg_file}"'
        success = run_command(command)

        # Limpiar el archivo temporal
        try:
            os.remove(temp_reg_file)
        except:
            pass

        if success:
            print("Ubicación de las aplicaciones de Store cambiada exitosamente.")
            print("Es necesario reiniciar el sistema para aplicar los cambios.")
            return True
        return False

    except Exception as e:
        print(f"Error configurando ubicación de Store apps: {e}")
        return False


def disable_web_search():
    command = 'reg add "HKCU\\Software\\Policies\\Microsoft\\Windows\\Explorer" /v "DisableSearchBoxSuggestions" /t REG_DWORD /d "1" /f'
    if run_command(command):
        print("Búsqueda web en menú de inicio deshabilitada correctamente.")
        return True
    return False


def restore_context_menu():
    command = 'reg.exe add "HKCU\\Software\\Classes\\CLSID\\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\\InprocServer32" /f /ve'
    if run_command(command):
        print("Menú contextual clásico restaurado correctamente.")
        return True
    return False


def enable_wsl():
    print("\nHabilitando WSL...")

    # Habilitar el Subsistema de Windows para Linux
    command1 = 'dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart'
    if not run_command(command1):
        print("Error habilitando el Subsistema de Windows para Linux")
        return False

    # Habilitar la característica de Máquina Virtual
    command2 = 'dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart'
    if not run_command(command2):
        print("Error habilitando la plataforma de Máquina Virtual")
        return False

    print("WSL habilitado correctamente. Es necesario reiniciar el sistema.")
    return True


def enable_hyperv():
    command = 'powershell -Command "Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All"'
    if run_command(command):
        print("Hyper-V habilitado correctamente. Es necesario reiniciar el sistema.")
        return True
    return False


def show_menu():
    while True:
        print("\n=== MENÚ PRINCIPAL ===")
        print("1. Cambiar ubicación de carpetas de usuario a unidad D:")
        print("2. Instalar programas desde CSV")
        print("3. Cambiar ubicación de aplicaciones de Store a unidad D:")
        print("4. Deshabilitar búsqueda web en menú de inicio")
        print("5. Restaurar menú contextual clásico")
        print("6. Habilitar WSL")
        print("7. Habilitar Hyper-V")
        print("8. Salir")

        choice = input("\nSeleccione una opción (1-8): ")

        if choice == "1":
            print("\nCambiando ubicación de carpetas...")
            change_shell_folders()
        elif choice == "2":
            print("\nCambiando ubicación de aplicaciones de Store...")
            setup_store_apps_location()
        elif choice == "3":
            print("\nDeshabilitando búsqueda web en menú de inicio...")
            disable_web_search()
        elif choice == "4":
            print("\nRestaurando menú contextual clásico...")
            restore_context_menu()
        elif choice == "5":
            print("\nHabilitando WSL...")
            enable_wsl()
        elif choice == "6":
            print("\nHabilitando Hyper-V...")
            enable_hyperv()
        elif choice == "7":
            print("\nIniciando instalación de programas...")
            if check_chocolatey():
                install_from_csv('install_list.csv')
            else:
                print("Error en la instalación de Chocolatey.")
        elif choice == "8":
            print("\nSaliendo del programa...")
            break
        else:
            print("\nOpción no válida. Por favor, seleccione una opción válida.")

        input("\nPresione Enter para continuar...")


def main():
    if not is_admin():
        print("Este programa requiere permisos de administrador.")
        input("Presiona una tecla para salir...")
        sys.exit(1)

    show_menu()

    print("\nProceso finalizado.")
    print("IMPORTANTE: Debes reiniciar el sistema para aplicar todos los cambios.")
    input("Presiona Enter para salir...")


if __name__ == '__main__':
    main()