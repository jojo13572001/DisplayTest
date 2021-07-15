pushd .

cd %~dp0

for %%I in (.) do set CurrDirName=%%~nxI

call pip install -r %~dp0/../requirements.txt

cd %~dp0/../

call python -m %CurrDirName%

popd