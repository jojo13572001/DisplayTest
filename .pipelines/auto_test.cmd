@echo off

pushd .
cd %~dp0/../owt-server-p2p
call npm install
popd

call pip install -r requirements.txt

call pytest --doctest-modules --junitxml=junit/test-results.xml --cov=. --cov-report=xml