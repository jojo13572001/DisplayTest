@echo off

pushd .

cd %~dp0/owt-server-p2p

call npm install

cd %~dp0/DisplayWPF_Net47

set STAGE_PRODUCTION=%1
set APP_VERSION=%~2
if "%STAGE_PRODUCTION%"=="stage" (set DOWNLOAD_URL=https://myviewboardstorage.s3-us-west-2.amazonaws.com/uploads/Display_Stage/)
if "%STAGE_PRODUCTION%"=="production" (set DOWNLOAD_URL=https://myviewboardstorage.s3-us-west-2.amazonaws.com/uploads/Display/)

rem echo downloading latest myViewBoard Display...

rem echo download url "%DOWNLOAD_URL%%APP_VERSION%"
rem call certutil.exe -urlcache -split -f "%DOWNLOAD_URL%%APP_VERSION%" "%APP_VERSION%"

rem call %cd%/7-Zip/7z.exe x "%APP_VERSION%"
rem if errorlevel 1 goto :error

rem call %cd%/7-Zip/7z.exe x disk1.cab
rem if errorlevel 1 goto :error

call pip install -r %~dp0/requirements.txt

cd %~dp0/pytest

call pytest --doctest-modules --junitxml=junit/test-results.xml --cov=. --cov-report=xml

goto :exit

:error
popd
echo Last command failed with error code: %errorlevel%

:exit
popd
exit /b %errorlevel%