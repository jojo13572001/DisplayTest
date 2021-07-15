pushd .

cd %~dp0

echo start node peerserver.js

taskkill /f /im node.exe

start node peerserver.js

popd