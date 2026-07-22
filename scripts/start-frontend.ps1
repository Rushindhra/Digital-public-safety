@echo off
setlocal
cd /d "%~dp0..\frontend"

if not exist "node_modules" (
    echo Installing frontend dependencies...
    call npm install
)

echo.
echo Starting Next.js frontend on http://localhost:3000
echo.

set NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
call npm run dev
