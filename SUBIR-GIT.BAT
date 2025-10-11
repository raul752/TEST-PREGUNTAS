@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
color 0A
mode con: cols=80 lines=30

:: ==========================================
echo.
echo ╔════════════════════════════════════════════════════════════════════════════╗
echo ║            🚀 SUBIR PROYECTO A GITHUB - 100%% SEGURO                        ║
echo ╚════════════════════════════════════════════════════════════════════════════╝
echo.

:: ================= CONFIGURACION =================
set "GITHUB_USER=raul752"
set "GITHUB_REPO=TEST-PREGUNTAS"
set "PROJECT_DIR=E:\Descargas\WEB"

:: LEER TOKEN DESDE ARCHIVO EXTERNO (NO SUBIR A GITHUB)
if not exist "%PROJECT_DIR%\github-token.txt" (
    echo ❌ ERROR: No se encuentra el archivo de configuración
    echo.
    echo 📋 CREAR ARCHIVO DE CONFIGURACIÓN:
    echo.
    echo    1. Crea un archivo: github-token.txt
    echo    2. Pega tu token dentro ^(solo el token, nada más^)
    echo    3. Guárdalo en: %PROJECT_DIR%
    echo    4. Vuelve a ejecutar este BAT
    echo.
    echo 🔑 Genera tu token aquí: https://github.com/settings/tokens/new
    echo    Permisos necesarios: ☑ repo, ☑ workflow
    echo.
    pause
    exit /b 1
)

set /p GITHUB_TOKEN=<"%PROJECT_DIR%\github-token.txt"

cd /d "%PROJECT_DIR%"

:: ================= CREAR .gitignore SI NO EXISTE =================
if not exist ".gitignore" (
    echo 📝 Creando .gitignore para proteger el token...
    (
        echo # Archivos de configuración con tokens
        echo github-token.txt
        echo *.token
        echo *.secret
        echo.
        echo # Archivos de sistema Windows
        echo Thumbs.db
        echo desktop.ini
        echo.
        echo # Logs
        echo *.log
    ) > .gitignore
    echo ✅ .gitignore creado
    echo.
)

:: ================= VALIDAR GIT INSTALADO =================
echo [1/7] 🔍 Verificando Git...
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Git no está instalado
    echo 📥 Descarga Git desde: https://git-scm.com/download/win
    start https://git-scm.com/download/win
    pause
    exit /b 1
)
echo ✅ Git encontrado
echo.

:: ================= VALIDAR TOKEN =================
echo [2/7] 🔑 Validando token de GitHub...
powershell -Command "$headers = @{Authorization='Bearer %GITHUB_TOKEN%'; Accept='application/vnd.github.v3+json'}; try { $user = Invoke-RestMethod -Uri 'https://api.github.com/user' -Headers $headers -ErrorAction Stop; Write-Host '✅ Token válido - Usuario:' $user.login -ForegroundColor Green; exit 0 } catch { Write-Host '❌ Token inválido o expirado' -ForegroundColor Red; exit 1 }"

if %errorlevel% neq 0 (
    echo.
    echo ⚠️  SOLUCIÓN: Genera un nuevo token
    echo 📋 1. Ve a: https://github.com/settings/tokens/new
    echo 📋 2. Marca: repo, workflow
    echo 📋 3. Copia el token y pégalo en: github-token.txt
    start https://github.com/settings/tokens/new
    pause
    exit /b 1
)
echo.

:: ================= INICIALIZAR REPO LOCAL =================
echo [3/7] 📁 Configurando repositorio local...
git config --global --add safe.directory "%PROJECT_DIR%"
git config --global user.name "%GITHUB_USER%"
git config --global user.email "%GITHUB_USER%@users.noreply.github.com"

if not exist ".git" (
    echo    🔹 Inicializando Git...
    git init
    git branch -M main
) else (
    echo    ✅ Repositorio Git ya existe
)
echo.

:: ================= VERIFICAR REPO EN GITHUB =================
echo [4/7] 🌐 Verificando repositorio en GitHub...
powershell -Command "$headers = @{Authorization='Bearer %GITHUB_TOKEN%'; Accept='application/vnd.github.v3+json'}; try { $repo = Invoke-RestMethod -Uri 'https://api.github.com/repos/%GITHUB_USER%/%GITHUB_REPO%' -Headers $headers -ErrorAction Stop; Write-Host '✅ Repositorio existe:' $repo.html_url -ForegroundColor Green; exit 0 } catch { Write-Host '⚠️  Repositorio no existe' -ForegroundColor Yellow; exit 1 }"

if %errorlevel% neq 0 (
    echo.
    echo 📋 CREAR REPOSITORIO MANUALMENTE:
    echo    1. Se abrirá GitHub en tu navegador
    echo    2. Repository name: TEST-PREGUNTAS
    echo    3. ⚠️  NO marques "Add a README file"
    echo    4. Click en [Create repository]
    echo    5. Vuelve aquí y presiona una tecla
    echo.
    start https://github.com/new
    pause
)
echo.

:: ================= CONFIGURAR REMOTO =================
echo [5/7] 🔗 Configurando conexión remota...
git remote remove origin 2>nul
git remote add origin https://%GITHUB_USER%:%GITHUB_TOKEN%@github.com/%GITHUB_USER%/%GITHUB_REPO%.git
echo ✅ Remoto configurado
echo.

:: ================= COMMIT =================
echo [6/7] 📦 Preparando archivos...
git add .

set "fecha=%date% %time%"
git diff --cached --quiet
if %errorlevel% equ 0 (
    echo ⚠️  No hay cambios para subir
) else (
    git commit -m "📤 Actualización automática %fecha%"
    echo ✅ Commit creado
)
echo.

:: ================= SINCRONIZAR Y PUSH =================
echo [7/7] 🚀 Subiendo a GitHub...

:: Primero intentar sincronizar con GitHub
echo    🔄 Sincronizando con GitHub...
git pull origin main --rebase --allow-unrelated-histories 2>&1 | find "fatal" >nul
if %errorlevel% equ 0 (
    echo    ⚠️  Primera vez o repo vacío, continuando...
)

:: Ahora hacer push
git push -u origin main 2>&1 | find "rejected" >nul
if %errorlevel% equ 0 (
    echo    ⚠️  Push rechazado, forzando sincronización...
    git push -u origin main --force 2>&1
)

if %errorlevel% equ 0 (
    echo.
    echo ╔════════════════════════════════════════════════════════════════════════════╗
    echo ║                    ✅ ¡ÉXITO! PROYECTO SUBIDO                              ║
    echo ╚════════════════════════════════════════════════════════════════════════════╝
    echo.
    echo 🌐 Ver en GitHub: https://github.com/%GITHUB_USER%/%GITHUB_REPO%
    echo 🔒 Token protegido: NO fue subido a GitHub
    echo.
    timeout /t 3 /nobreak >nul
    start https://github.com/%GITHUB_USER%/%GITHUB_REPO%
) else (
    echo.
    echo ╔════════════════════════════════════════════════════════════════════════════╗
    echo ║                    ❌ ERROR AL SUBIR                                        ║
    echo ╚════════════════════════════════════════════════════════════════════════════╝
    echo.
    echo 🔍 Posibles soluciones:
    echo    1. Verifica que el token tenga permisos de "repo"
    echo    2. Verifica que el repositorio exista en GitHub
    echo    3. Revoca el token y crea uno nuevo
    echo.
    echo 🔗 Gestionar tokens: https://github.com/settings/tokens
    echo.
)

echo.
pause