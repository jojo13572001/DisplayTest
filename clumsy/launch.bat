pushd .

cd %~dp0

echo start clumsy.exe %*

taskkill /f /im clumsy.exe

start clumsy.exe %*

popd