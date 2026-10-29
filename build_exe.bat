@echo off
chcp 65001 >nul
title 몽글펫 EXE 빌드
echo ===========================================
echo   몽글펫 - Windows 실행파일 만들기
echo ===========================================
where py >nul 2>nul
if errorlevel 1 (
  echo Python이 설치되어 있지 않습니다.
  echo https://www.python.org/downloads/windows/ 에서 Python을 설치하고
  echo 설치 화면에서 Add python.exe to PATH 를 체크한 뒤 다시 실행하세요.
  pause
  exit /b 1
)
py -m pip install --upgrade pip
py -m pip install pyinstaller
py -m PyInstaller --noconfirm --clean --onefile --windowed --name MonglePet monglepet.pyw
if errorlevel 1 (
  echo 빌드에 실패했습니다. 위 오류를 확인하세요.
  pause
  exit /b 1
)
echo.
echo 성공! dist\MonglePet.exe 파일이 만들어졌습니다.
echo 이 파일을 바탕화면 등 원하는 곳으로 복사해서 실행하세요.
pause
