require('./logger');
const http = require('http');
const {loggers} = require('winston');
const logger = loggers.get('my-logger');

const requestListener = function (req, res) {
    logger.info("Received request");
    res.writeHead(200);
    res.end('This is a storage service');
}

const server = http.createServer(requestListener);
const http_io = require( "socket.io" )( server );

http_io.on( "connection", function( httpsocket ) {
    httpsocket.on( 'python-message', function( fromPython ) {
        logger.info("%o", fromPython);
        httpsocket.broadcast.emit( 'message', fromPython );
    });
});

server.listen(3000);