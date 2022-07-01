"""
A web framework to build the back-end.
"""


class Myth:
        
    
    def __init__(self) -> None:
        self.routes = None
        
        
    def add_route(self, route: str, app):
        def ignore(request):
            class HTTPResponseDummy:
                def __init__(self) -> None:
                    self.body = ''
            return HTTPResponseDummy()
        if self.routes == None:
            self.routes = {route: app, '/favicon.ico': ignore}
            self.routes[route[0:-1]] = app
        else:
            if route in self.routes:
                raise AssertionError(f'Route ({route}) can only be used once.')
            self.routes[route] = app
            if route[-1] == '/':
                self.routes[route[0:-1]] = app
            else:
                self.routes[route + '/'] = app
    
    
    def route(self, route: str):
        def wrapper(app):
            self.add_route(route, app)
        return wrapper
        
        
    def defult_exception_handler(self, request, exception='?'):
        class DummyHTTPResponse:
            """
            Creates a dummy HTTP response.
            """
            def __init__(self, body: str):
                self.body = body
                self.HTTP_version = '1.1'
                self.status = '200 OK'
        return DummyHTTPResponse('An internal error occured; a ' + str(exception) + ' error.')
    
    
    def defult_404_handler(self, request):
        class DummyHTTPResponse:
            """
            Creates a dummy HTTP response.
            """
            def __init__(self, body: str):
                self.body = body
                self.HTTP_version = '1.1'
                self.status = '200 OK'
        return DummyHTTPResponse('URL not found: ' + request['PATH_INFO'])
    
    
    def configure_exception_handler(self, new_handler):
        self.defult_exception_handler = new_handler
        
        
    def configure_404_handler(self, new_handler):
        self.defult_404_handler = new_handler
        
        
    def runserver(self, host='localhost', port=8000, poll_seconds=0.0):
        from wsgiref.simple_server import make_server
        def app(environment, start_response):
            start_response('200 OK', headers=[])
            try:
                return [bytes(str(self.routes[environment['PATH_INFO']](environment).body).encode())]
            except KeyError:
                return [bytes(str(self.defult_404_handler(environment).body).encode())]
            except Exception as e:
                return [bytes(str(self.defult_exception_handler(environment, exception=e).body).encode())]
        print('Serving on http://' + host + ':' + str(port) + ' ...')
        server = make_server(host, port, app)
        try:
            server.serve_forever(poll_seconds)
        except:
            server.shutdown()


class HTTPResponse:
    """
    Creates an HTTP response.
    """
    
    
    def __init__(self, body):
        self.body = body
        self.HTTP_version = '1.1'
        self.status = '200 OK'


class Database:
    """
    Initializes link between the database and the program.
    """
    
    
    def __init__(self, database_file: str) -> None:
        try:
            open(database_file)
        except:
            raise FileNotFoundError('Database file does not exist.')
        self.__original = open(database_file).read()
        self.__database_content = []
        self.database_file = database_file
        for row in open(database_file).read().split('\n'):
            self.__database_content.append(row.split(' '))
        
        
    def get_row(self, row_number: int) -> list:
        return self.__database_content[row_number - 1]
    
    
    def get_column(self, row_number: int, column_number: int) -> str:
        return self.get_row(row_number)[column_number - 1]
    
    
    def update_row(self, row_number: int, update: str) -> None:
        content = open(self.database_file).read()
        open(self.database_file, 'w').write(content.replace(content.split('\n')[row_number - 1], update))
        self.__database_content = []
        self.database_file = self.database_file
        for row in open(self.database_file).read().split('\n'):
            self.__database_content.append(row.split(' '))
        
        
    def update_column(self, row_number: int, column_number: int, update: str) -> None:
        content = open(self.database_file).read()
        open(self.database_file, 'w').write(content.replace(content.split('\n')[row_number - 1][column_number - 1], update))
        self.__database_content = []
        self.database_file = self.database_file
        for row in open(self.database_file).read().split('\n'):
            self.__database_content.append(row.split(' '))
        
        
    def delete_row(self, row_number: int) -> None:
        self.update_row(row_number, '')
        
        
    def delete_column(self, row_number: int, column_number: int) -> None:
        self.update_column(row_number, column_number, '')
        
        
    def undo_all_changes(self):
        open(self.database_file).write(self.__original)
        
        
    def get_all(self):
        return self.__database_content


class TemplateEnvironment:
    
    
    def __init__(self, response: HTTPResponse, begin_tag='[& ', end_tag=' &]') -> None:
        self.response = response
        self.begin_tag = begin_tag
        self.end_tag = end_tag
        
        
    def render_values(self, names_and_values: dict):
        for name in names_and_values:
            self.response.body = self.response.body.replace(self.begin_tag + name + self.end_tag, names_and_values.get(name))
