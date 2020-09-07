# This file does two things:
# - Generate index.js file to be used in javascript.
# - Listens to a TCP socket.
#

import os
import zerorpc
import inspect
from . import main


# Create index.js file
dirpath = os.path.dirname(os.path.realpath(__file__))
index_js = open(f'{dirpath}/index.js', 'w')
index_js.write('''
/* AUTO GENERATED. DO NOT CHANGE ANYTHING IN THIS FILE */
''')


# TCP server, to be intiated.
server = None


# Terminates the server.
def __stop__():
    server.stop()


# Create a dictionary of exported methods.
methods = main.exports + [__stop__]
method_dict = {m.__name__: m for m in methods}


# Initiate TCP server.
server = zerorpc.Server(method_dict)


# Look for an open port and bind the server to it.
port = None
for p in range(4101, 4199):
    try:
        server.bind(f'tcp://0.0.0.0:{p}')
        port = p
        break
    except Exception:
        continue


# In case of no free-port, exit.
if not port:
    print('Failed to allocate a port.')
    exit(1)


# Create the client-interface for javascript in index.js.
index_js.write('''
const zerorpc = require('zerorpc');
const util = require('util');

function _call_python(f, ...args) {
  const client = new zerorpc.Client();
  client.connect("tcp://127.0.0.1:%s");
  client.invokeAsync = util.promisify(client.invoke);
  return client.invokeAsync(f, ...args).then(ret => {
    client.close();
    return ret;
  });
}

''' % port)


# Create the bridges from javascript to exported py-functions.
for method in methods:
    args = inspect.getargspec(method).args
    args = ', '.join(args)
    stmt = 'module.exports.{0} = ({1}) => _call_python(\'{0}\', {1});\n'.format(method.__name__, args)
    index_js.writelines([stmt])


# Close the file-pointer
index_js.flush()
index_js.close()


# Start the server.
server.run()
