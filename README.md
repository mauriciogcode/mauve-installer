# mauve-installer


## Instalacciones Faltantes (Manuales)
- Estas opciones demoraron bastante por eso las quite. Daban la sensacion de detener el programa
- 
- Anaconda3,2,winget install -e --id Anaconda.Anaconda3 --location "D:\Program Files\Anaconda3" --accept-source-agreements --accept-package-agreements,true
- Docker Desktop,8,winget install -e --id Docker.DockerDesktop --accept-source-agreements --accept-package-agreements,true
- WhatsApp,28,winget install -e --id WhatsApp.WhatsApp --accept-source-agreements --accept-package-agreements,false

- Python 
- Jetbrains toolbox
## Instalacciones Faltantes (que deben ir al csv)
En el csv faltan:
- teams,
- zoom,
- treesieze free,
- bulkcrap unistaller,
- local send,
- fork (git)
- any desk (remote desktop)


## Fixes
#### Box
- agregar esto como instruccion para box
- reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Box\Box" /v "LoginWithExternalBrowser" /t REG_DWORD /d 0 /f

## Instrucciones
- logearte a dropbox, box, mega
- dejar git conectado...
- recordar instalar aquellas cosas que son propias de la maquina, impresora, tableta grafica, 
tarjeta aceleradora, placa madre, mouse,  etc.

#### activar end task en las opciones de desarrollo de windows

## Mejoras futuras
- Poner alguna animacion de seguimiento para saber que la instalacion no esta frenada
- De alguna forma poner instrucciones para instalar lo que falte


### Quitar la busqueda web del menu de inicio
reg add "HKCU\Software\Policies\Microsoft\Windows\Explorer" /v "DisableSearchBoxSuggestions" /t REG_DWORD /d "1" /f

### Recuperar el menu contextual con un comando
reg.exe add "HKCU\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32" /f /ve

### Para activar WSL:
#### Habilitar el Subsistema de Windows para Linux
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

##### Habilitar la característica de Máquina Virtual
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
### Para activar Hyper-V:
#### Habilitar todas las características de Hyper-V
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All

