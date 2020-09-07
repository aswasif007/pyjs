const py = require('./py');

async function main() {
  const msg = await py.hello_world('Lord Stark');
  console.log(msg);
}

main();
py.__stop__();
