const { format, loggers, transports } = require('winston');
const options = {
    console: {
            format: format.combine(format.splat(),
                format.json()),
    }
};

loggers.add('my-logger', {
    transports: [
        new transports.Console(options.console)
    ],
    exitOnError: false
})
