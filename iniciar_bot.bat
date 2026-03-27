@echo off
:: Bot de Finanzas Personales - Inicio automático
:: Este script inicia Ollama y el bot de Telegram

echo Iniciando Bot de Finanzas...

:: Esperar a que Ollama esté listo (se inicia solo con Windows)
timeout /t 5 /nobreak >nul

:: Ir a la carpeta del proyecto
cd /d "C:\Users\RAFAX\Documents\PROYECTO CONTADOR"

:: Iniciar el bot
"C:\Users\RAFAX\AppData\Local\Python\pythoncore-3.14-64\python.exe" bot.py
