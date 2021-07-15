pushd .

cd %~dp0

echo start clumsy.exe %1 %2

taskkill /f /im clumsy.exe

start clumsy.exe %1 %2

popd