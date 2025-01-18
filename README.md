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
- zoomit,
- treesieze free,
- bulkcrap unistaller,
- local send,
- fork (git)
- any desk


## Fixes
#### Box
- agregar esto como instruccion para box
- reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Box\Box" /v "LoginWithExternalBrowser" /t REG_DWORD /d 0 /f

## Instrucciones
- logearte a dropbox, box, mega
- dejar git conectado...
- recordar instalar aquellas cosas que son propias de la maquina, impresora, tableta grafica, 
tarjeta aceleradora, placa madre, mouse,  etc.


## Mejoras futuras
- Poner alguna animacion de seguimiento para saber que la instalacion no esta frenada
- De alguna forma poner instrucciones para instalar lo que falte


### Quitar la busqueda web del menu de inicio
reg add "HKCU\Software\Policies\Microsoft\Windows\Explorer" /v "DisableSearchBoxSuggestions" /t REG_DWORD /d "1" /f

### Recuperar el menu contextual con un comando
