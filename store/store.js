const http = require('http');

const requestListener = function (req, res) {
    res.writeHead(200);
    res.end('This is a storage service');
}

const server = http.createServer(requestListener);
const http_io = require( "socket.io" )( server );

http_io.on( "connection", function( httpsocket ) {
    httpsocket.on( 'python-message', function( fromPython ) {
        console.log("I received", fromPython)
        httpsocket.broadcast.emit( 'message', fromPython );
    });
});

server.listen(3000);