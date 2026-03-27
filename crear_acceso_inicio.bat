@echo off
:: Crea un acceso directo del bot en la carpeta de Inicio de Windows
:: para que se ejecute automáticamente al encender el PC

set STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
set SCRIPT="C:\Users\RAFAX\Documents\PROYECTO CONTADOR\iniciar_bot.vbs"

:: Crear un VBScript que ejecute el .bat sin mostrar ventana negra
echo Set WshShell = CreateObject("WScript.Shell") > %SCRIPT%
echo WshShell.Run chr(34) ^& "C:\Users\RAFAX\Documents\PROYECTO CONTADOR\iniciar_bot.bat" ^& chr(34), 0 >> %SCRIPT%
echo Set WshShell = Nothing >> %SCRIPT%

:: Copiar el VBScript a la carpeta de Inicio
copy %SCRIPT% "%STARTUP%\iniciar_bot_finanzas.vbs"

echo.
echo ===================================
echo  Bot configurado para inicio automatico!
echo  Se ejecutara cada vez que enciendas el PC.
echo  Para desactivarlo, elimina el archivo:
echo  %STARTUP%\iniciar_bot_finanzas.vbs
echo ===================================
echo.
pause
