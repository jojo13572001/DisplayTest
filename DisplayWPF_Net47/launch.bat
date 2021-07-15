pushd .

cd %~dp0

echo start DisplayWPF.exe

taskkill /f /im DisplaySubprocess.exe

taskkill /f /im DisplayWPF.exe

start DisplayWPF.exe

popd