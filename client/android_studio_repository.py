#!/usr/bin/env python
from __future__ import print_function

import cherrypy
from zipfile import ZipFile
from tempfile import mkstemp
from os import close, remove
from shutil import copyfileobj
from cherrypy.lib.static import serve_file
from os.path import realpath, dirname, join, exists

__script_directory__ = dirname(realpath(__file__))

__config__ = {
    'global' : {
        'server.max_request_body_size'  : 0,
    },
    '/assets' : {
        'tools.staticdir.on'        : True,
        'tools.staticdir.dir'       : join(__script_directory__, 'site', 'assets')
    },
    '/icon.ico' : {
        'tools.staticfile.on'       : True,
        'tools.staticfile.filename' : join(__script_directory__, 'site', 'assets', 'favicon.ico')
    }
}

class AndroidStudioRepositoryMirror(object):
    @cherrypy.expose
    def default(self):
        raise cherrypy.HTTPError(404)

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    def index(self):
        return serve_file(join(__script_directory__, 'site', 'index.html'))

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    def get_source_table(self):
        return """
                <tr>
                  <td>Otto</td>
                  <td>@mdo</td>
                </tr>
                <tr>
                  <td>Thornton</td>
                  <td>@fat</td>
                </tr>
                <tr>
                  <td>3</td>
                  <td>@twitter</td>
                </tr>
        """

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    def push_update(self, file):
        temp_file_descriptor, temp_file_path = mkstemp()
        close(temp_file_descriptor)
        try:
            with open(temp_file_path, 'wb+') as temp_file:
                copyfileobj(file.file, temp_file)

            with ZipFile(temp_file_path, 'r') as new_repo_zip:
                new_repo_zip.extractall(__script_directory__)

        finally:
            remove(temp_file_path)

if __name__ == "__main__":
    cherrypy.tree.mount(AndroidStudioRepositoryMirror(), '', __config__)
    # Unmount the default server so we can setup our own custom ones
    cherrypy.server.unsubscribe()

    http_server = cherrypy._cpserver.Server()
    http_server.socket_port = 80
    http_server.socket_host = '0.0.0.0'
    http_server.thread_pool = 25
    http_server.max_request_body_size = 0
    http_server.socket_timeout = 60
    http_server.subscribe()

    https_server = cherrypy._cpserver.Server()
    https_server.socket_port = 443
    https_server.socket_host = '0.0.0.0'
    https_server.thread_pool = 25
    https_server.max_request_body_size = 0
    https_server.socket_timeout = 60
    https_server.ssl_private_key = join(__script_directory__, 'androidstudiorepomirror.key')
    https_server.ssl_certificate = join(__script_directory__, 'androidstudiorepomirror.crt')
    if exists(https_server.ssl_private_key) and exists(https_server.ssl_certificate):
        https_server.subscribe()

    cherrypy.engine.start()
    cherrypy.engine.block()
