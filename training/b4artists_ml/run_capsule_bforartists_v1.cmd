@echo off
set B4ML_BONEFORGE_SOURCE=\\100.114.2.71\Gdrive\LapArt\Projects\Blender Ghost_Tool B4Artists\.runtime-test\BoneForge_B4Artists_github
"C:\Program Files\Bforartists\5.1.2\bforartists.exe" --background --python-exit-code 1 --python "G:\LapArt\Projects\Blender Ghost_Tool B4Artists\.runtime-test\run_capsule_bforartists_v1.py"
exit /b %ERRORLEVEL%
