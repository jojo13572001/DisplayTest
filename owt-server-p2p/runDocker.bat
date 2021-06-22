pushd .
cd %~dp0
CALL docker image prune -a -f
CALL docker build -t jojo13572001/owt-server-p2p:1.0 --no-cache .
CALL docker rm -f owt-server-p2p
CALL docker run -it --rm -v %~dp0:/usr/src/app/owt-server-p2p -p 8095:8095 -p 8096:8096 -p 8097:8097 -p 8098:8098 --name=owt-server-p2p --privileged jojo13572001/owt-server-p2p:1.0 bash -c "./launch.sh"
popd