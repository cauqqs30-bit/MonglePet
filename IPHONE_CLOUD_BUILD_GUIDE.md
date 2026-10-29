# 몽글펫 — 아이폰만으로 Windows EXE 빌드하기

이 프로젝트에는 GitHub Actions용 Windows 클라우드 빌드 설정이 포함되어 있습니다. 사용자의 PC는 필요 없지만, GitHub 계정과 인터넷 연결은 필요합니다.

## 아이폰에서 진행

1. `MonglePet_Windows_Project.zip`을 파일 앱에 저장하고 압축을 풉니다.
2. Safari에서 https://github.com/new 에 접속해 로그인하고 새 저장소를 만듭니다. 예: `monglepet`. Public 또는 Private 중 원하는 설정을 선택하고 `Create repository`를 누릅니다.
3. 저장소 화면에서 `Add file` → `Upload files`를 선택합니다.
4. 압축을 푼 프로젝트의 파일을 업로드합니다. 반드시 `monglepet.pyw`, `README.md`, `build_exe.bat`, 그리고 `.github/workflows/build-windows.yml` 경로가 저장소에 들어가야 합니다. 모바일 웹에서 숨김 폴더 `.github` 업로드가 어렵다면, 저장소에서 `Add file` → `Create new file`을 선택해 파일 이름을 `.github/workflows/build-windows.yml`로 지정하고 ZIP 안의 `build-windows.yml` 내용을 붙여 넣어 커밋합니다.
5. `Commit changes`를 누릅니다. 저장소의 `Actions` 탭에서 `Build Windows EXE` 실행이 시작됩니다. 자동 실행되지 않으면 해당 workflow를 선택하고 `Run workflow`를 누릅니다.
6. 작업이 초록색 체크로 끝나면 실행 기록을 열고 `Artifacts`에서 `MonglePet-Windows-EXE`를 다운로드합니다. 압축을 풀면 `MonglePet.exe`가 있습니다.

## 참고
- GitHub Actions는 Windows 클라우드 러너에서 EXE를 만듭니다. 이 파일은 Windows용이며 iPhone에서 실행할 수 없습니다.
- GitHub 화면과 메뉴는 모바일 UI/계정 상태에 따라 다를 수 있습니다.
- 이 방식은 GitHub 계정 생성/로그인 및 파일 업로드를 사용자 본인이 해야 합니다. 이 대화에서 GitHub 계정에 직접 접속하거나 빌드를 실행할 수는 없습니다.
