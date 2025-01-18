# mauve-installer


## Mejoras
- Poner alguna animacion de seguimiento para saber que la instalacion no esta frenada
- De alguna forma poner instrucciones para instalar lo que falte

- En el csv faltan teams, zoom, zoomit, treesieze free, bulkcrap unistaller, local send, git extensions
- 
- Estas opciones demoraron bastante por eso las quite. Daban la sensacion de detener el programa
- Anaconda3,2,winget install -e --id Anaconda.Anaconda3 --location "D:\Program Files\Anaconda3" --accept-source-agreements --accept-package-agreements,true
Docker Desktop,8,winget install -e --id Docker.DockerDesktop --accept-source-agreements --accept-package-agreements,true
WhatsApp,28,winget install -e --id WhatsApp.WhatsApp --accept-source-agreements --accept-package-agreements,false

- Agrega uno para jet brains esto no funciona
- JetBrains Toolbox,20,choco install jetbrainstoolbox --params "/Dir:D:\Program Files\JetBrains\Toolbox" -y,false

-Python y Whats app tambien..




-Agrgar any desk al csv

- agregar esto como instruccion para box
- reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Box\Box" /v "LoginWithExternalBrowser" /t REG_DWORD /d 0 /f

logearte a dropbox, box, mega

dejar git conectado...


con este se quita la busqueda en el menu de inicio
reg add "HKCU\Software\Policies\Microsoft\Windows\Explorer" /v "DisableSearchBoxSuggestions" /t REG_DWORD /d "1" /f


recuperar el menu contextual con un comando

recordar instalar aquellas cosas que son propias de la maquina, impresora, tableta grafica, 
tarjeta aceleradora, placa madre, mouse,  etc.