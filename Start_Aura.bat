@echo off
title Aura Emotion AI Startup
echo ==============================================
echo       Aura Emotion AI - Startup Script
echo ==============================================

:: Check if the C:\av environment exists
IF NOT EXIST "C:\av\Scripts\python.exe" (
    echo.
    echo [1/3] First-time setup: Creating Python environment at C:\av
    echo This is done to bypass Windows long-path limits for TensorFlow.
    python -m venv C:\av
    
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment. Ensure Python is installed and in your PATH.
        pause
        exit /b %errorlevel%
    )

    echo.
    echo [2/3] Upgrading pip...
    C:\av\Scripts\python.exe -m pip install --upgrade pip

    echo.
    echo [3/3] Installing all required dependencies - This will take a few minutes...
    
    :: Install base packages
    C:\av\Scripts\python.exe -m pip install Flask==3.0.3 opencv-python==4.10.0.84 pandas==2.2.3 numpy==2.1.3 scikit-learn==1.5.2 python-dotenv==1.0.1
    
    :: Install TensorFlow
    C:\av\Scripts\python.exe -m pip install tensorflow==2.21.0
    
    :: Install Google Generative AI components carefully to avoid protobuf conflicts
    C:\av\Scripts\python.exe -m pip install google-generativeai --no-deps
    C:\av\Scripts\python.exe -m pip install google-ai-generativelanguage==0.6.15 google-api-core google-auth google-api-python-client tqdm --no-deps
    C:\av\Scripts\python.exe -m pip install googleapis-common-protos grpcio-status cryptography pyasn1 pyasn1-modules rsa cachetools cffi pydantic-core annotated-types typing-inspection httplib2 uritemplate pyparsing google-auth-httplib2 --no-deps
    
    echo.
    echo Setup complete!
)

echo.
echo Starting the Aura Emotion AI server...
echo Please open http://127.0.0.1:5000 in your browser.
echo.
C:\av\Scripts\python.exe app.py

pause
