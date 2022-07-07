"""
A web framework to build the back-end.
"""
from __future__ import print_function
import time as __time
def __override(param): 
    raise AssertionError('Cannot access function; it is illegal.')
__time.sleep = __override


class HTTPResponse:
    """
    Creates an HTTP response.
    """
    
    
    def __init__(self, body, content_type='text/html', HTTP_version='HTTP/1.1', charset='utf-8'):
        self.body = body
        self.content_type = f'{content_type}; charset={charset}'
        self.HTTP_version = HTTP_version
        self.content_length = len(body)


class Myth:
    """
    A class for creating an API.
    """
        
    
    def __init__(self) -> None:
        self.routes = None
        
        
    def connect_route(self, route: str, app):
        """
        Adds a route.

        Args:
            route (str): The route of where the app is supposedly called.
            app (function): The app to be routed.
        """
        if self.routes == None:
            self.routes = {route: app}
            if route[-1] == '/':
                self.routes[route[0:-1]] = app
            else:
                if route[0] != '/' and route[-1] != '/':
                    self.routes['/' + route + '/'] = app
                    self.routes['/' + route] = app
                else:
                    self.routes[route + '/'] = app
                if route[0] != '/' and route[-1] == '/':
                    self.routes['/' + route] = app
                    self.routes['/' + route + '/'] = app
        else:
            if route in self.routes:
                raise AssertionError(f'Route ({route}) can only be used once.')
            self.routes[route] = app
            if route[-1] == '/':
                self.routes[route[0:-1]] = app
            else:
                if route[0] != '/' and route[-1] != '/':
                    self.routes['/' + route + '/'] = app
                    self.routes['/' + route] = app
                else:
                    self.routes[route + '/'] = app
            if route[0] != '/' and route[-1] == '/':
                self.routes['/' + route] = app
                self.routes['/' + route[0:-1]] = app
                    
    
    
    def route(self, route: str):
        """
        The decorator version of add_route.

        Args:
            route (str): The route to the app.
        """
        def wrapper(app):
            self.connect_route(route, app)
        return wrapper
        
        
    def default_exception_handler(self, request, exception='?'):
        """
        The defualt exception handler. It could be overriden.

        Args:
            request (dict): The request parameters.
            exception (str, optional): The exception which was caught. Defaults to a question mark.

        Returns:
            HTTPResponse: Class for handling HTTP responses.
        """
        return HTTPResponse('An internal error occured; a ' + str(exception) + ' error.')
    
    
    def default_404_handler(self, request):
        """
        The default 404 not found handler. It could be overriden.

        Args:
            request (dict): The request parameters.

        Returns:
            HTTPResponse: Class for handling HTTP responses.
        """
        return HTTPResponse('URL not found: ' + request['PATH_INFO'])
    
    
    def configure_exception_handler(self, new_handler):
        """
        Changes the default_exception_handler() to the new_handler().

        Args:
            new_handler (function): The new handler to be the default exception handler.
        """
        self.default_exception_handler = new_handler
        
        
    def configure_404_handler(self, new_handler):
        """
        Changes the default_404_handler() to the new_handler().

        Args:
            new_handler (function): The new handler to be the default 404 handler.
        """
        self.default_404_handler = new_handler
        
        
    def wsgi_app(self, request, response):
        """
        The WSGI app.

        Args:
            request (dict): The request of the client.
            response (function): The response of the server.

        Returns:
            list: The WSGI response.
        """
        from time import strftime
        request['wsgi.multithread'] = True
        request['wsgi.multiprocess'] = True
        request['environ.keys'] = len(request.keys())
        request['request.date&time'] = strftime('%d/%m/%y %I:%M:%S')
        request['mythjiv.wsgi.app'] = self.wsgi_app
        request['mythjiv.root.attrs'] = dir(self)
        request['mythjiv.root.illegal'] = ['time.sleep', 'input']
        if request['PATH_INFO'] == '/favicon.ico':
            pass
        else:
            try:
                request['mythjiv.root.current_appname'] = self.routes[request['PATH_INFO']]
                request['mythjiv.root.current_appcontent'] = self.routes[request['PATH_INFO']](request).body
            except:
                pass
        response('200 OK', headers=[])
        try:
            request['CONTENT_TYPE'] = str(self.routes[request['PATH_INFO']](request).content_type)
            request['CONTENT_LENGTH'] = str(self.routes[request['PATH_INFO']](request).content_length)
            request['SERVER_PROTOCOL'] = str(self.routes[request['PATH_INFO']](request).HTTP_version)
            return [bytes(str(self.routes[request['PATH_INFO']](request).body).encode())]
        except KeyError:
            request['CONTENT_TYPE'] = 'text/html'
            request['CONTENT_LENGTH'] = len(str(self.default_404_handler(request).body))
            return [bytes(str(self.default_404_handler(request).body).encode())]
        except Exception as e:
            request['CONTENT_TYPE'] = 'text/html'
            request['CONTENT_LENGTH'] = len(str(self.default_exception_handler(request, e).body))
            return [bytes(str(self.default_exception_handler(request, exception=e).body).encode())]
        
        
    def runserver(self, host='localhost', port=8000, poll_seconds=0):
        """
        Runs a simple WSGI server. Note that this cannot be used for production. Use a real WSGI server.

        Args:
            host (str, optional): Host to bind. Defaults to 'localhost'.
            port (int, optional): Port to bind. Defaults to 8000.
            poll_seconds (float, optional): The amount of time the server rests. Defaults to 0.
        """
        from wsgiref.simple_server import make_server
        print('Serving on http://' + host + ':' + str(port) + ' ...')
        server = make_server(host, port, self.wsgi_app)
        try:
            server.serve_forever(poll_seconds)
        except KeyboardInterrupt:
            server.shutdown()


class DISHED:
    
    
    """
    Creates a DISHED object for storing and getting data.
    
    Args:
        database_file (str): The database file to get and store data to.
    """
    
    
    def __init__(self, database_file: str) -> None:
        self.__l = []
        self.__databasefile = database_file
        
        
    def get_layer(self, layer_number: int):
        """
        Gets a line in the database file.

        Args:
            layer_number (int): The line number.

        Returns:
            list: The line as a list with the columns as the items.
        """
        return self.__l[layer_number - 1]
    
    
    def get_item(self, row: int, column: int):
        """
        Gets a column in the database file.

        Args:
            row (int): The line number.
            column (int): The column number.

        Returns:
            Any: The column value.
        """
        return self.get_layer(row)[column - 1]
        
        
    def add_layer(self, layer_number: int, layer: list):
        """
        Adds a line in the database file.

        Args:
            layer_number (int): The line number.
            layer (list): The line to add as a list.
        """
        self.__l.insert(layer_number - 1, layer)
        
        
    def add_item(self, layer_number: int, column: int, item):
        """
        Adds an item to a line.

        Args:
            layer_number (int): The line number.
            column (int): The column number.
            item (Any): The item to add.
        """
        self.__l[layer_number - 1].insert(column - 1, item)
        
        
    def remove_layer(self, layer_number: int):
        """
        Removes a line.

        Args:
            layer_number (int): The line number.
        """
        del self.__l[layer_number - 1]
        
        
    def remove_item(self, layer_number: int, column: int):
        """
        Removes an item in a line.

        Args:
            layer_number (int): The line number.
            column (int): The column number.
        """
        del self.__l[layer_number - 1][column - 1]
        
        
    def get(self):
        """
        Gets the unsaved changes.

        Returns:
            str: The unsaved changes (as a string).
        """
        side_num = 0
        full = ''
        for side in self.__l:
            side_num += 1
            full += str(side)
        return full
    
    
    def empty_DISHED_object(self):
        """
        Removes all unsaved changes and all contents in the database.
        """
        self.__l = []
        open(self.__databasefile, 'w').write('')
        
        
    def get_database(self):
        """
        Gets the saved changes in the database.

        Returns:
            str: The database contents.
        """
        return open(self.__databasefile).read()
    
    
    def save_changes(self, replace_db_contents=True):
        """
        Saves the changes.

        Args:
            replace_db_contents (bool, optional): A parameter asking if the unsaved changes is to be added to the database contents or to replace the database contents. Defaults to True.

        Raises:
            FileNotFoundError: If the database isn't created yet.
        """
        try:
            open(self.__databasefile)
        except:
            raise FileNotFoundError('No database found matched "' + self.__databasefile + '".')
        content = ''
        for layer in self.__l:
            for item in layer:
                content += item + ' '
            content += '\n'
        added = ''
        if replace_db_contents is True:
            pass
        else:
            added = self.get_database()
        open(self.__databasefile, 'w').write(added + content)


def render_values(filepath: str, names_and_values: dict):
    """
    Renders the values to the given file path.

    Args:
        filepath (str): The path to the template.
        names_and_values (dict): The names of the values to be replaced and the values to replace the names.
    """
    filecontext = open(filepath).read()
    for name in names_and_values:
        filecontext = filecontext.replace('[% ' + name + ' %]', names_and_values.get(name))
    open(filepath, 'w').write(filecontext)
    
    
def for_loop(filepath: str, beginning_line_to_forloop: int, ending_line_to_forloop: int, line_to_insert: int, times: int):
    """
    Does a for loop.

    Args:
        filepath (str): The path to the template.
        beginning_line_to_forloop (int): The line number to begin for looping.
        ending_line_to_forloop (int): The ending line number to begin for looping.
        line_to_insert (int): The beginning line number to insert.
        times (int): How many times it is supposedly for looped.
    """
    listforlooplines = open(filepath).read().split('\n')[beginning_line_to_forloop - 1:ending_line_to_forloop]
    forlooplines = ''
    for forloopline in listforlooplines:
        forlooplines += forloopline + '\n'
    l_t_i = line_to_insert - 1
    forlist = [filecontent.split(' ') for filecontent in open(filepath).read().split('\n')]
    for i in range(times):
        forlist.insert(l_t_i, [forlooplines + '\n'])
        l_t_i += 1
    paper = ''
    for line in forlist:
        for column in line:
            paper += column + ' '
        paper += '\n'
    open(filepath, 'w').write(''.join(paper))
    
    
def if_statement(filepath: str, line_number: int):
    """
    Does an if statement.

    Args:
        filepath (str): The path to the template.
        line_number (int): The line number pointing to the tag with the condition.
    """
    line = open(filepath).read()
