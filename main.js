const py = require('./py');

py.hello_world('Lord Stark').then(msg => {
  console.log(msg);
});

py.__stop__();
