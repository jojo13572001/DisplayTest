// Copyright (C) <2015> Intel Corporation
//
// SPDX-License-Identifier: Apache-2.0

// Prepare for web server
var fs = require("fs");
var path = require("path");
var url = require('url');
var config = require('./config');
var account = require('./vendormodule');

var dirname = __dirname || path.dirname(fs.readlinkSync('/proc/self/exe'));
var httpsOptions = {
  key: fs.readFileSync(path.resolve(dirname, 'cert/key.pem')).toString(),
  cert: fs.readFileSync(path.resolve(dirname, 'cert/cert.pem')).toString()
};

var app = require('express')();
app.get('/displays/:id', function(req, res) {
  res.send({code:"831582076"});
});
app.post('/displays', function(req, res) {
  res.send({code:"831582076"});
});
app.get('/code/:id', function(req, res) {
  res.send("0000");
});

var server = app.listen(config.port.plain);
var servers = require("https").createServer(httpsOptions, app).listen(config.port.secured);
var controlServers = require("https").createServer(httpsOptions, app).listen(config.port.csecured);
var io = require('socket.io').listen(server);
var ios = require('socket.io').listen(servers);
var controlIos = require('socket.io').listen(controlServers);

var sessionMap = {};  // Key is uid, and value is session object.
var controlSessionMap = {};  // Key is uid, and value is session object.

// Check user's token from partner
function validateUser(token, successCallback, failureCallback){
  // TODO: Should check token first, replace this block when engagement with different partners.
  if(token){
    account.authentication(token,function(uid){
      successCallback(uid);
    },function(){
      console.log('Account system return false.');
      failureCallback(0);
    });
  }
  else
    failureCallback(0);
}

function disconnectClient(uid){
  if(sessionMap[uid]!==undefined){
    var session=sessionMap[uid];
    session.emit('server-disconnect');
    session.disconnect();
    console.log('Force disconnected '+uid);
  }
}

function createUuid(){
  return 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    var r = Math.random()*16|0, v = c === 'x' ? r : (r&0x3|0x8);
    return v.toString(16);
  });
}

function emitChatEvent(targetUid, eventName, message, successCallback, failureCallback){
  if(sessionMap[targetUid]){
    sessionMap[targetUid].emit(eventName,message);
    if(successCallback)
      successCallback();
  }
  else
    if(failureCallback)
      failureCallback(2201);
}

function authorization(socket, next){
  var query=url.parse(socket.request.url,true).query;
  var token=query.token;
  var clientVersion=query.clientVersion;
  var clientType=query.clientType;
  switch(clientVersion){
    case '4.2':
    case '4.2.1':
    case '4.3':
    case '4.3.1':
      // socket.user stores session related information.
      if(token){
        validateUser(token, function(uid){  // Validate user's token successfully.
          socket.user={id:uid};
          console.log(uid+' authentication passed.');
        },function(error){
            // Invalid login.
            console.log('Authentication failed.');
            next();
        });
      }else{
        socket.user=new Object();
        socket.user.id=createUuid()+'@anonymous';
        console.log('Anonymous user: '+socket.user.id);
      }
      next();
      break;
    default:
      next(new Error('2103'));
      console.log('Unsupported client. Client version: '+query.clientVersion);
      break;
  }
}

function onConnection(socket){
  // Disconnect previous session if this user already signed in.
  var uid=socket.user.id;
  disconnectClient(uid);
  sessionMap[uid]=socket;
  socket.emit('server-authenticated',{uid:uid});  // Send current user's id to client.
  console.log('A new client has connected. Online user number: '+Object.keys(sessionMap).length);

  socket.on('disconnect',function(){
    if(socket.user){
      var uid=socket.user.id;
      // Delete session
      if(socket===sessionMap[socket.user.id]){
        delete sessionMap[socket.user.id];
      }
      console.log(uid+' has disconnected. Online user number: '+Object.keys(sessionMap).length);
    }
  });

  // Forward events
  var forwardEvents=['owt-message'];
  for (var i=0;i<forwardEvents.length;i++){
    socket.on(forwardEvents[i],(function(i){
      return function(data, ackCallback){
        data.from=socket.user.id;
        var to=data.to;
        delete data.to;
        emitChatEvent(to,forwardEvents[i],data,function(){
          if(ackCallback)
            ackCallback();
        },function(errorCode){
          if(ackCallback)
            ackCallback(errorCode);
        });
      };
    })(i));
  }
}

function listen(io) {
  io.use(authorization);
  io.on('connection',onConnection);
}

listen(io);
listen(ios);

var webSocket, windowsSocket;
function onControlConnection(socket){
    var query=url.parse(socket.request.url,true).query;
    if (query["socketCustomEvent"] != null){
      windowsSocket = socket;
      console.log("Windows Socket " + query["socketCustomEvent"]);
      windowsSocket.uid = query["socketCustomEvent"];

      socket.on(windowsSocket.uid, (data) => {
        if (data["action"] === "connect"){
           webSocket.emit("share", {"success":true});
        }
        else if (data["action"] === "denied" || data["action"] === "blocked"){
           webSocket.emit("share", {"success":false});
        }
        else if (data["action"] === "getstatreport"){
           console.log("server receive stats report reply");
           webSocket.emit("stats", {"success":true, "data":data});
        }
      });
    }
    else {
      console.log("Web Socket " + socket.id);
      webSocket = socket;
      webSocket.uid = socket.id;

      socket.on("share", (data) => {
        console.log("server receive web otp " + data.otp)
        windowsSocket.emit(windowsSocket.uid, {"messageFor":windowsSocket.uid, "userid":webSocket.uid, "otp":data.otp});
      });

      socket.on("stats", (data) => {
        console.log("server receive stats report request " + data.action);
        windowsSocket.emit(windowsSocket.uid, {"messageFor":windowsSocket.uid, "userid":webSocket.uid, "action":data.action});
      });

      socket.on("stop", (data) => {
        console.log("server receive stop request")
        windowsSocket.emit(windowsSocket.uid, {"messageFor":windowsSocket.uid, "userid":webSocket.uid, "action":data.action});
      });
    }
}
controlIos.on('connection',onControlConnection);

// Signaling server only allowed to be connected with Socket.io.
// If a client try to connect it with any other methods, server returns 405.
/*app.get('*', function(req, res, next) {
  res.send(405, 'WebRTC signaling server. Please connect it with Socket.IO.');
});*/

console.info('Signal server Listening port: ' + config.port.plain + '/' + config.port.secured);
console.info('Control server Listening port: ' + (config.port.csecured))
console.info('Otp server Listening port: ' + (config.port.csecured))
