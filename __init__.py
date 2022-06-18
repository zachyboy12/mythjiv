"""
A web framework to build the back-end.
"""
    

class API:
    """
    Creates an API.
    """
    
    
    def __init__(self) -> None:
        self.routes = None
    
    
    def route(self, route: str):
        """
        Routes app to the decorated function.

        Args:
            route (str): Route name for function to be wrapped to.
        """
        def decor(app):
            if self.routes is None:
                self.routes = {route: app}
            elif self.routes is not None:
                if self.routes.get(route, None) != None:
                    raise AssertionError('Such route exists.')
                self.routes[route] = app
        return decor
    
    
    def connect_route(self, route_function, route: str):
        """
        Routes app to the route_function. Clone of route, but not a decorator.

        Args:
            route_function (function): Function to connect to route.
            route (str): Route to be connected to route_function.
        """
        if self.routes is None:
                self.routes = {route: route_function}
        elif self.routes is not None:
            self.routes[route] = route_function
        
    
    
    def runserver(self, host='127.0.0.1', port=8000, html_404='Page not found. Maybe you mispelled the url?', frameworkname=None):
        """
        Makes SimpleServer serve forever.
        """
        import socket, logging, time, inspect

        if self.routes is None:
            raise ValueError('No routes registered.')
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
        server_socket.listen(1)
        requests = ''
        if frameworkname is None:
            pass
        else:
            print(f'% {frameworkname} %')
        print(f'Listening on: http://{host}:{port} ...')
        logging.warn('\033[93m CANNOT BE USED FOR PRODUCTION. USE A WSGI SERVER \033[0m')
        while True:
            try:
                client_connection, client_address = server_socket.accept()
                request = client_connection.recv(1024).decode()
                headers = request.split('\n')
                request_name = headers[0].split()[1]
                has_response = False
                requests += '\n' + request
                response = ''
                print(time.strftime('\033[93m[%m/%d/%Y %H:%M:%S] \033[0m- ') + request.split('\n')[0])
                for theroute in self.routes:
                    if request_name == theroute or request_name == theroute[0:-1] or request_name == theroute + '/':
                        has_response = True
                        response = f'HTTP/{self.routes.get(theroute, "")().HTTP_version} {self.routes.get(theroute, "")().status}\n\n{self.routes.get(theroute, "")().body}'
                    else:
                        continue
                if has_response == True:
                    pass
                else:
                    response = f'HTTP/{self.routes.get(theroute, "")().HTTP_version} {self.routes.get(theroute, "")().status}\n\n{html_404}'
                client_connection.sendall(response.encode())
                client_connection.close()
            except KeyboardInterrupt:
                break
        server_socket.close()
        return f'\nRequests:\n' + requests
    
    
class Myth(API):
    """
    Creates an API. Clone of the API class.
    """
    pass


class Template:
    """
    Creates a Template.
    """
    
    
    def __init__(self, myth_or_api, begin_tag='[% ', end_tag=' %]') -> None:
        self.context = myth_or_api.routes.get()()
        self.bt = begin_tag
        self.et = end_tag
        
        
    def render_values(self, names_and_values: dict):
        for name in names_and_values:
            tag = self.bt + name + self.et
            self.context.replace(tag, names_and_values.get(name, name))


class HTTPResponse:
    """
    Creates an HTTP response.
    """
    
    
    def __init__(self, body: str):
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
        self.database_content = []
        self.database_file = database_file
        for row in open(database_file).read().split('\n'):
            self.database_content.append(row.split(' '))
        
        
    def get_row(self, row_number: int) -> list:
        return self.database_content[row_number - 1]
    
    
    def get_column(self, row_number: int, column_number: int) -> str:
        return self.get_row(row_number)[column_number - 1]
    
    
    def update_row(self, row_number: int, update: str) -> None:
        content = open(self.database_file).read()
        open(self.database_file, 'w').write(content.replace(content.split('\n')[row_number - 1], update))
        self.database_content = []
        self.database_file = self.database_file
        for row in open(self.database_file).read().split('\n'):
            self.database_content.append(row.split(' '))
        
        
    def update_column(self, row_number: int, column_number: int, update: str) -> None:
        content = open(self.database_file).read()
        open(self.database_file, 'w').write(content.replace(content.split('\n')[row_number - 1][column_number - 1], update))
        self.database_content = []
        self.database_file = self.database_file
        for row in open(self.database_file).read().split('\n'):
            self.database_content.append(row.split(' '))
        
        
    def delete_row(self, row_number: int) -> None:
        self.update_row(row_number, '')
        
        
    def delete_column(self, row_number: int, column_number: int) -> None:
        self.update_column(row_number, column_number, '')
        
        
    def undo_all_changes(self):
        open(self.database_file).write(self.__original)
