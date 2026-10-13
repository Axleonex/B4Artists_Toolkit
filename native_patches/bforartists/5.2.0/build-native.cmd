@echo off
setlocal EnableExtensions
rem [CMD] Build the native Timeline application from pinned source/libraries.
rem Usage: build-native.cmd SOURCE LIBRARIES BUILD OUTPUT [JOBS]
set "AA_SOURCE=%~1"
set "AA_LIBRARIES=%~2"
set "AA_BUILD=%~3"
set "AA_OUTPUT=%~4"
set "AA_JOBS=%~5"
if not defined AA_JOBS set "AA_JOBS=2"
if not defined AA_OUTPUT (
  echo Usage: build-native.cmd SOURCE LIBRARIES BUILD OUTPUT [JOBS]
  exit /b 2
)
if not exist "%AA_SOURCE%\CMakeLists.txt" (
  echo Missing application source: %AA_SOURCE%
  exit /b 2
)
if not exist "%AA_LIBRARIES%\python" (
  echo Missing pinned Windows libraries: %AA_LIBRARIES%
  exit /b 2
)
set "AA_VS=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools"
if not exist "%AA_VS%\Common7\Tools\VsDevCmd.bat" (
  echo Visual Studio 2022 C++ Build Tools are required.
  exit /b 2
)
call "%AA_VS%\Common7\Tools\VsDevCmd.bat" -no_logo -arch=x64 -host_arch=x64
if errorlevel 1 exit /b 1
set "AA_CMAKE=%AA_VS%\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe"
set "AA_NINJA=%AA_VS%\Common7\IDE\CommonExtensions\Microsoft\CMake\Ninja"
set "PATH=%AA_NINJA%;%PATH%"
"%AA_CMAKE%" -S "%AA_SOURCE%" -B "%AA_BUILD%" -G Ninja ^
  -DCMAKE_BUILD_TYPE=Release ^
  -DCMAKE_INSTALL_PREFIX="%AA_OUTPUT%" ^
  -DLIBDIR="%AA_LIBRARIES%" ^
  -DWITH_BUILDINFO=ON ^
  -DWITH_INSTALL_COPYRIGHT=ON ^
  -DWITH_GTESTS=OFF ^
  -DNINJA_MAX_NUM_PARALLEL_COMPILE_HEAVY_JOBS=2 ^
  -DNINJA_MAX_NUM_PARALLEL_LINK_JOBS=1 ^
  -DWITH_CYCLES_CUDA_BINARIES=OFF ^
  -DWITH_CYCLES_HIP_BINARIES=OFF ^
  -DWITH_CYCLES_ONEAPI_BINARIES=OFF ^
  -DWITH_CYCLES_DEVICE_ONEAPI=OFF
if errorlevel 1 exit /b 1
"%AA_CMAKE%" --build "%AA_BUILD%" --target install --parallel %AA_JOBS%
if errorlevel 1 exit /b 1
echo Portable application installed to %AA_OUTPUT%
exit /b 0
