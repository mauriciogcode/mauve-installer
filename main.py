import csv
import subprocess
import sys
import os
import time
import ctypes
import winreg
import threading
import itertools
from pathlib import Path
from colorama import init, Fore, Back, Style

# Inicializar colorama
init(autoreset=True)

class LoadingAnimation:
    def __init__(self, description="Instalando"):
        self.description = f"{Fore.CYAN}{description}{Style.RESET_ALL}"
        self.done = False
        self.thread = None

    def animate(self):
        for c in itertools.cycle(['⢿', '⣻', '⣽', '⣾', '⣷', '⣯', '⣟', '⡿']):
            if self.done:
                break
            sys.stdout.write(f'\r{self.description} {Fore.YELLOW}{c}{Style.RESET_ALL}')
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write('\r')

    def start(self):
        self.thread = threading.Thread(target=self.animate)
        self.thread.start()

    def stop(self):
        self.done = True
        if self.thread is not None:
            self.thread.join()

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
        print(f"{Fore.RED}Error creando directorio {path}: {e}{Style.RESET_ALL}")
        return False

def modify_registry_key(key_path, name, value, key_type=winreg.REG_EXPAND_SZ):
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, name, 0, key_type, value)
        return True
    except Exception as e:
        print(f"{Fore.RED}Error modificando registro {key_path}\\{name}: {e}{Style.RESET_ALL}")
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

    print(f"{Fore.CYAN}Creando directorios necesarios...{Style.RESET_ALL}")
    for folder_path in folders_to_modify.values():
        if not create_directory_if_not_exists(folder_path):
            return False

    print(f"{Fore.CYAN}Modificando registros...{Style.RESET_ALL}")
    for registry_path in registry_paths:
        for folder_name, folder_path in folders_to_modify.items():
            if not modify_registry_key(registry_path, folder_name, folder_path):
                return False

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
        print(f"{Fore.RED}Error cambiando USERPROFILE: {e}{Style.RESET_ALL}")
        return False

    print(f"\n{Fore.GREEN}Cambios en las carpetas completados. Es necesario cerrar sesión para aplicar los cambios.{Style.RESET_ALL}")
    return True

def run_command(command):
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, text=True)

        loading = LoadingAnimation(f"Ejecutando comando: {command[:40]}...")
        loading.start()

        stdout, stderr = process.communicate()
        loading.stop()

        if process.returncode != 0:
            print(f"\n{Fore.RED}Error ejecutando el comando: {command}")
            print(f"Código de salida: {process.returncode}")
            print(f"Salida de error:")
            print(f"{stderr}")
            print(f"Salida estándar:")
            print(f"{stdout}{Style.RESET_ALL}")
            return False
        return True
    except subprocess.CalledProcessError as e:
        loading.stop()
        print(f"\n{Fore.RED}Error ejecutando el comando: {command}")
        print(f"Código de salida: {e.returncode}")
        print(f"Salida de error: {e.stderr if hasattr(e, 'stderr') else 'No disponible'}{Style.RESET_ALL}")
        return False
    except Exception as e:
        loading.stop()
        print(f"\n{Fore.RED}Error inesperado ejecutando el comando: {command}")
        print(f"Detalles del error: {str(e)}{Style.RESET_ALL}")
        return False

def set_execution_policy():
    command1 = "powershell -Command Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force"
    if not run_command(command1):
        print(f"{Fore.RED}Error al configurar la política de ejecución para CurrentUser{Style.RESET_ALL}")
        return False

    command2 = "powershell -Command Set-ExecutionPolicy Bypass -Scope Process -Force"
    if not run_command(command2):
        print(f"{Fore.RED}Error al configurar la política de ejecución para Process{Style.RESET_ALL}")
        return False

    return True

def check_chocolatey():
    try:
        subprocess.run("choco -v", check=True, shell=True, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
        print(f"{Fore.GREEN}Chocolatey ya está instalado.{Style.RESET_ALL}")
        return True
    except subprocess.CalledProcessError:
        print(f"{Fore.YELLOW}Chocolatey no está instalado. Instalando Chocolatey...{Style.RESET_ALL}")
        return install_chocolatey()

def install_chocolatey():
    if not set_execution_policy():
        print(f"{Fore.RED}Error al configurar la política de ejecución{Style.RESET_ALL}")
        return False

    command = (
        'powershell -Command "'
        '[System.Net.ServicePointManager]::SecurityProtocol = '
        '[System.Net.ServicePointManager]::SecurityProtocol -bor 3072; '
        'iex ((New-Object System.Net.WebClient).DownloadString('
        "'https://community.chocolatey.org/install.ps1'))\"")

    if run_command(command):
        print(f"{Fore.GREEN}Chocolatey instalado con éxito.{Style.RESET_ALL}")
        return True
    return False

def install_from_csv(csv_file):
    if not os.path.exists(csv_file):
        print(f"{Fore.YELLOW}El archivo {csv_file} no existe. Creando un archivo nuevo con ejemplo...{Style.RESET_ALL}")
        with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['ProgramName', 'InstallOrder', 'InstallCommand', 'SkipFlag'])
            writer.writerow(['7zip', 1, 'choco install 7zip -y', 'false'])
        print(f"{Fore.GREEN}Archivo {csv_file} creado con ejemplo.{Style.RESET_ALL}")
        input(f"\n{Fore.CYAN}Presiona Enter para continuar...{Style.RESET_ALL}")
        return

    try:
        with open(csv_file, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            programs = sorted(list(reader), key=lambda x: int(x['InstallOrder']))

            if not programs:
                print(f"{Fore.YELLOW}No hay programas para instalar en el archivo CSV.{Style.RESET_ALL}")
                input(f"\n{Fore.CYAN}Presiona Enter para continuar...{Style.RESET_ALL}")
                return

            total_programs = len([p for p in programs if p['SkipFlag'].strip().lower() != 'true'])
            current_program = 0

            for row in programs:
                if row['SkipFlag'].strip().lower() == 'true':
                    print(f"\n{Fore.YELLOW}Saltando la instalación de {row['ProgramName']} según la configuración.{Style.RESET_ALL}")
                    continue

                current_program += 1
                print(f"\n{Fore.CYAN}Progreso: [{current_program}/{total_programs}]{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Instalando {row['ProgramName']} (Orden: {row['InstallOrder']})...{Style.RESET_ALL}")

                try:
                    if not run_command(row['InstallCommand']):
                        print(f"\n{Fore.RED}Error al instalar {row['ProgramName']}.{Style.RESET_ALL}")
                        choice = input(f"{Fore.YELLOW}Presiona 'S' para continuar o cualquier otra tecla para detener: {Style.RESET_ALL}")
                        if choice.lower() != 's':
                            print(f"\n{Fore.RED}Proceso de instalación detenido por el usuario.{Style.RESET_ALL}")
                            input(f"\n{Fore.CYAN}Presiona Enter para volver al menú principal...{Style.RESET_ALL}")
                            return
                except Exception as e:
                    print(f"\n{Fore.RED}Error inesperado instalando {row['ProgramName']}: {str(e)}{Style.RESET_ALL}")
                    choice = input(f"{Fore.YELLOW}Presiona 'S' para continuar o cualquier otra tecla para detener: {Style.RESET_ALL}")
                    if choice.lower() != 's':
                        print(f"\n{Fore.RED}Proceso de instalación detenido por el usuario.{Style.RESET_ALL}")
                        input(f"\n{Fore.CYAN}Presiona Enter para volver al menú principal...{Style.RESET_ALL}")
                        return

            print(f"\n{Fore.GREEN}Todas las instalaciones han sido procesadas.{Style.RESET_ALL}")
            input(f"\n{Fore.CYAN}Presiona Enter para volver al menú principal...{Style.RESET_ALL}")

    except Exception as e:
        print(f"\n{Fore.RED}Error leyendo el archivo CSV: {str(e)}{Style.RESET_ALL}")
        input(f"\n{Fore.CYAN}Presiona Enter para volver al menú principal...{Style.RESET_ALL}")

def setup_store_apps_location():
    try:
        new_path = "D:\\ProgramasWindowsApps"
        create_directory_if_not_exists(new_path)

        reg_content = f"""Windows Registry Editor Version 5.00

[HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Appx]
"PackageRoot"="{new_path}"
"""

        temp_reg_file = os.path.join(os.environ['TEMP'], 'store_location.reg')
        with open(temp_reg_file, 'w') as f:
            f.write(reg_content)

        command = f'regedit /s "{temp_reg_file}"'
        success = run_command(command)

        try:
            os.remove(temp_reg_file)
        except:
            pass

        if success:
            print(f"{Fore.GREEN}Ubicación de las aplicaciones de Store cambiada exitosamente.{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Es necesario reiniciar el sistema para aplicar los cambios.{Style.RESET_ALL}")
            return True
        return False

    except Exception as e:
        print(f"{Fore.RED}Error configurando ubicación de Store apps: {e}{Style.RESET_ALL}")
        return False

def disable_web_search():
    command = 'reg add "HKCU\\Software\\Policies\\Microsoft\\Windows\\Explorer" /v "DisableSearchBoxSuggestions" /t REG_DWORD /d "1" /f'
    if run_command(command):
        print(f"{Fore.GREEN}Búsqueda web en menú de inicio deshabilitada correctamente.{Style.RESET_ALL}")
        return True
    return False

def restore_context_menu():
    command = 'reg.exe add "HKCU\\Software\\Classes\\CLSID\\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\\InprocServer32" /f /ve'
    if run_command(command):
        print(f"{Fore.GREEN}Menú contextual clásico restaurado correctamente.{Style.RESET_ALL}")
        return True
    return False

def enable_wsl():
    print(f"\n{Fore.CYAN}Habilitando WSL...{Style.RESET_ALL}")

    command1 = 'dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart'
    if not run_command(command1):
        print(f"{Fore.RED}Error habilitando el Subsistema de Windows para Linux{Style.RESET_ALL}")
        return False

    command2 = 'dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart'
    if not run_command(command2):
        print(f"{Fore.RED}Error habilitando la plataforma de Máquina Virtual{Style.RESET_ALL}")
        return False

    print(f"{Fore.GREEN}WSL habilitado correctamente. Es necesario reiniciar el sistema.{Style.RESET_ALL}")
    return True

def enable_hyperv():
    command = 'powershell -Command "Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All"'
    if run_command(command):
        print(f"{Fore.GREEN}Hyper-V habilitado correctamente. Es necesario reiniciar el sistema.{Style.RESET_ALL}")
        return True
    return False

def show_menu():
    while True:
        print(f"\n{Fore.CYAN}=== MENÚ PRINCIPAL ==={Style.RESET_ALL}")
        print(f"{Fore.WHITE}1. Cambiar ubicación de carpetas de usuario a unidad D:")
        print("2. Instalar programas desde CSV")
        print("3. Cambiar ubicación de aplicaciones de Store a unidad D:")
        print("4. Deshabilitar búsqueda web en menú de inicio")
        print("5. Restaurar menú contextual clásico")
        print("6. Habilitar WSL")
        print("7. Habilitar Hyper-V")
        print(f"{Fore.RED}8. Salir{Style.RESET_ALL}")

        choice = input(f"\n{Fore.YELLOW}Seleccione una opción (1-8): {Style.RESET_ALL}")

        if choice == "1":
            print(f"\n{Fore.CYAN}Cambiando ubicación de carpetas...{Style.RESET_ALL}")
            change_shell_folders()
        elif choice == "2":
            print(f"\n{Fore.CYAN}Iniciando instalación de programas...{Style.RESET_ALL}")
            if check_chocolatey():
                install_from_csv('install_list.csv')
            else:
                print(f"{Fore.RED}Error en la instalación de Chocolatey.{Style.RESET_ALL}")
        elif choice == "3":
            print(f"\n{Fore.CYAN}Cambiando ubicación de aplicaciones de Store...{Style.RESET_ALL}")
            setup_store_apps_location()
        elif choice == "4":
            print(f"\n{Fore.CYAN}Deshabilitando búsqueda web en menú de inicio...{Style.RESET_ALL}")
            disable_web_search()
        elif choice == "5":
            print(f"\n{Fore.CYAN}Restaurando menú contextual clásico...{Style.RESET_ALL}")
            restore_context_menu()
        elif choice == "6":
            print(f"\n{Fore.CYAN}Habilitando WSL...{Style.RESET_ALL}")
            enable_wsl()
        elif choice == "7":
            print(f"\n{Fore.CYAN}Habilitando Hyper-V...{Style.RESET_ALL}")
            enable_hyperv()
        elif choice == "8":
            print(f"\n{Fore.YELLOW}Saliendo del programa...{Style.RESET_ALL}")
            break
        else:
            print(f"\n{Fore.RED}Opción no válida. Por favor, seleccione una opción válida.{Style.RESET_ALL}")

        input(f"\n{Fore.CYAN}Presione Enter para continuar...{Style.RESET_ALL}")

def main():
    if not is_admin():
        print(f"{Fore.RED}Este programa requiere permisos de administrador.{Style.RESET_ALL}")
        input(f"{Fore.CYAN}Presiona una tecla para salir...{Style.RESET_ALL}")
        sys.exit(1)

    show_menu()

    print(f"\n{Fore.GREEN}Proceso finalizado.{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}IMPORTANTE: Debes reiniciar el sistema para aplicar todos los cambios.{Style.RESET_ALL}")
    input(f"{Fore.CYAN}Presiona Enter para salir...{Style.RESET_ALL}")

if __name__ == '__main__':
    main()