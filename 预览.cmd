@echo off
chcp 65001 >nul
cd /d "%~dp0"
title 生成本地预览

set "PYCMD="

python -c "import sys" >nul 2>nul
if not errorlevel 1 set "PYCMD=python"

if not defined PYCMD (
  py -3 -c "import sys" >nul 2>nul
  if not errorlevel 1 set "PYCMD=py -3"
)

if not defined PYCMD (
  if exist "%USERPROFILE%\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe" (
    set PYCMD="%USERPROFILE%\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe"
  )
)

if not defined PYCMD (
  echo.
  echo 没找到 Python。两个办法：
  echo   1. 直接双击 _site_local\index.html 看上次生成的预览；
  echo   2. 到 python.org 装一个，然后重新双击本文件。
  echo.
  pause
  exit /b 1
)

call %PYCMD% "tools\preview.py"
if errorlevel 1 (
  echo.
  echo 生成失败了。把上面的报错发给虎鲸。
  pause
  exit /b 1
)

start "" "_site_local\index.html"
