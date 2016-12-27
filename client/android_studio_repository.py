#!/usr/bin/env python
from __future__ import print_function

import cherrypy
from json import dumps
from zipfile import ZipFile
from tempfile import mkstemp
from shutil import copyfileobj
from os import close, remove, walk
from cherrypy.lib.static import serve_file
from os.path import realpath, dirname, join, exists


import staticdirindex
import htmldir

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
    },
}

class AndroidStudioRepositoryMirror(object):
    @cherrypy.expose
    def default(self, *args, **kwargs):
        if not cherrypy.request.path_info.lower().startswith('/android'):
            raise cherrypy.HTTPError(404)

        resource_file = join(__script_directory__, 'site', cherrypy.request.path_info)
        if exists(resource_file):
            return serve_file(resource_file)

        raise cherrypy.HTTPError(404)

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    def index(self):
        return serve_file(join(__script_directory__, 'site', 'index.html'))

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    def get_source_table(self):
        table_rows = []

        if exists(join(__script_directory__, 'site', 'android')):
            for root, dirs, files in walk(join(__script_directory__, 'site', 'android')):
                for f in files:
                    if f.lower().endswith('.zip') or f.lower().endswith('.jar'):
                        archive_path = join(root, f)

                        properties = "None"

                        #with ZipFile(archive_path, 'r') as archive:
                        #    for name in archive.namelist():
                        #        if name.lower().endswith('source.properties'):
                        #            properties = archive.read(name)
                        #            break

                        table_rows.append([archive_path.replace(realpath(join(__script_directory__, 'site')), ''), properties])

        table_id = 1
        table_string = ''
        for tr in table_rows:
            popover_options = dict(content="<p>{0}</p>".format(tr[1]), placement="left", trigger="hover", html=True)
            table_string += '<tr>'
            table_string += '<td>{0}</td>'.format(tr[0])
            table_string += '<td><button id="source_properties_{0}" class="btn btn-info pull-right">Properties</button></td>'.format(table_id)
            table_string += '<script>$("#source_properties_{0}").popover({1})</script>'.format(table_id, dumps(popover_options))
            table_string += '</tr>'

            table_id += 1

        return table_string

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    def push_update(self, file):
        temp_file_descriptor, temp_file_path = mkstemp()
        close(temp_file_descriptor)
        try:
            with open(temp_file_path, 'wb+') as temp_file:
                copyfileobj(file.file, temp_file)

            with ZipFile(temp_file_path, 'r') as new_repo_zip:
                new_repo_zip.extractall(join(__script_directory__, 'site'))

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
