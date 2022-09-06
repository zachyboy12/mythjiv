"""
A web framework to build the back-end.
"""
from __future__ import print_function  # Allow print to be a function in older versions
import re, inspect, types, os  # Import neccessary built-in modules


class HTTPResponse:
    
    
    """
    Creates an HTTP response.
    """
    
    
    def __init__(self, body='', content_type='text/html', HTTP_version='HTTP/1.1', charset='utf-8'):
        # Set neccessary attributes
        self.body = body
        self.content_type = f'{content_type}; charset={charset}'
        self.HTTP_version = HTTP_version
        self.content_length = len(body)


class Myth:
    
    
    """
    A class for creating an API.
    """
        
    
    def __init__(self) -> None:
        self.routes = None  # Default is None
        
        
    def connect_route(self, route: str, app):
        """
        Adds a route.

        Args:
            route (str): The route of where the app is supposedly called.
            app (function): The app to be routed.
        """
        if self.routes == None:  # If there's no routes
            self.routes = {route: app}  # Set it now to an empty dictionary with a key and a value which is the route and the app
            if route[-1] == '/':  # If the last index is a /
                self.routes[route[0:-1]] = app  # Set self.routes[route[0:-1]] (which is the route without the last index) is app
            else:  # If the last index isn't a /
                if route[0] != '/' and route[-1] != '/':  # Check if the first index is not a / and the last index of route is not a /
                    self.routes['/' + route + '/'] = app  # Set / + the route + a / to the app
                    self.routes['/' + route] = app  # Set / + the route to the app
                else:  # If that's not true
                    self.routes[route + '/'] = app  # Let route + a / equal to the app
                if route[0] != '/' and route[-1] == '/':  # If the first index of the route is not a slash and the last index is a /
                    self.routes['/' + route] = app  # a / + the route is the app
                    self.routes['/' + route + '/'] = app  # / + route + another / is the app
        else:  # Pick off from here. frgot to comment from here lol
            if route in self.routes:
                raise AssertionError(f'Route "{route}" can only be used once.')
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
        The decorator version of connect_route.

        Args:
            route (str): The route to the app.
        """
        def wrapper(app):  # Make a wrapper
            self.connect_route(route, app)  # Connect the route
        return wrapper  # Return a wrapper so to use this function as a decorator
        
        
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
        
        
    def map_regex(self, pattern):
        for route, handler in list(self.routes.items()):  # Loop thru all key and value pairs in all the routes
            match = re.search(route, pattern)
            if match:  # If a match was found
                return route, handler, match.groups()  # match.groups -> The magic
        return None
        
        
    def wsgi_app(self, request, response):
        """
        The WSGI app.

        Args:
            request (dict): The request of the client.
            response (function): The response of the server.

        Returns:
            list: The WSGI response.
        """
        request['path'] = request['PATH_INFO']  # Alias
        request['query string'] = {}  # Dict version for the query string. I chose to go from scratch
        for qstr in request['QUERY_STRING'].split('&'):  # For every part of the query string in the query string split by a '&'
            try:
                key, value = qstr.split('=')  # The key and the value is qstr split by an equal sign
                request['query string'][key] = value  # Set key to value
            except:
                continue  # Continue if error
        response('200 OK', headers=[
            (
                'Content-Type', 'text/html'  # Sending HTML
            )
        ])
        try:
            if isinstance(self.routes[request['PATH_INFO']], types.FunctionType):  # If it's a function
                handler = self.routes[request['PATH_INFO']](request)  # Notice I only call the handler once
                # Configure content type, content length, and the server protocol
                request['CONTENT_TYPE'] = str(handler.content_type)
                request['CONTENT_LENGTH'] = str(handler.content_length)
                request['SERVER_PROTOCOL'] = str(handler.HTTP_version)
                return [bytes(str(handler.body).encode())]  # Return handler's body
            elif inspect.isclass(self.routes[request['PATH_INFO']]):  # If it's a class
                obj = self.routes[request['PATH_INFO']](request)  # Get the object
                # Get attributes if possible
                try:
                    request['CONTENT_TYPE'] = obj.content_type
                except:
                    request['CONTENT_TYPE'] = 'text/html; charset=utf-8'
                try:
                    request['CONTENT_LENGTH'] = obj.content_length
                except:
                    pass
                try:
                    request['SERVER_PROTOCOL'] = obj.HTTP_version
                except:
                    request['SERVER_PROTOCOL'] = 'HTTP/1.1'
                try:
                    obj.request
                except:
                    obj.request = request
                try:
                    return [bytes(str(getattr(obj, request['REQUEST_METHOD'].lower())().body).encode())]  # Try to return the appropriate handler
                except AttributeError:
                    return [b'']
        except KeyError:  # If no handler was found
            regex_map = self.map_regex(request['PATH_INFO'])  # Get the regex and map it (aka try to get handler of regex)
            # Get the condition that proves regex did not map
            try:
                condition = not regex_map[2]
            except:
                condition = not regex_map
            if condition:  # If regex didn't map
                # 404 EVERYONE!
                handler = self.default_404_handler(request)
                request['CONTENT_TYPE'] = 'text/html'
                request['CONTENT_LENGTH'] = len(str(handler.body))
                return [bytes(str(handler.body).encode())]
            else:  # If regex maps
                # Get regex handler and PARTY!
                handler = regex_map[1](request, *regex_map[2])
                request['CONTENT_TYPE'] = str(handler.content_type)
                request['CONTENT_LENGTH'] = str(handler.content_length)
                request['SERVER_PROTOCOL'] = str(handler.HTTP_version)
                return [bytes(str(handler.body).encode())]
        except Exception as e:  # If there's an exception
            # 500 SERVER ERROR!!!
            handler = self.default_exception_handler(request, e)
            request['CONTENT_TYPE'] = 'text/html'
            request['CONTENT_LENGTH'] = len(str(handler.body))
            return [bytes(str(handler.body).encode())]
        
        
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
        
            
            
class Router:
    
    
    def __init__(self) -> None:
        self.__configurer = Myth()  # A new, invisible web app to connect routes
        
        
    def bind_route(self, pattern: str, app):
        self.__configurer.connect_route(pattern, app)
        
        
    def link_route(self, pattern: str):
        def inner(app):
            self.bind_route(pattern, app)
        return inner
    
    
    def configure_myth(self, myth: Myth):
        myth.routes = self.__configurer.routes  # Set the Myth's route to the invisible web app's routes
        
        
class ORM:
    
    
    def __init__(self, path: str) -> None:
        self.db_path = path  # The path to the database
        self.changes = 0  # Commit times
        if os.path.exists(self.db_path):  # If the file exists
            source_file = open(self.db_path)
            src = source_file.read().splitlines()  # Get contents
            source_file.close()
            lines = src[1:]  # Lines of the source minus the headers at the top
            try:
                titles = ''.join(src[0]).split(',')  # Get titles
            except:
                self.__db = {}  # Nothing's there
                return None  # Exit out from function
            db = {}  # Set db to empty dict
            frame = []  # Current row
            current_index = 0  # Title number
            for title in titles:
                for line in lines:
                    try:
                        frame += [line.split(',')[current_index]]  # Set frame to the current_index index of line split by a comma
                    except:
                        continue
                if title == '':  # If the title is nothing
                    pass
                else:
                    db[title] = frame  # Set the title to the row (aka frame)
                frame = []  # Empty frame
                current_index += 1  # Increment current_index
            self.__db = db  # Set self.__db to db
        else:  # If it doesn't exist
            source_file = open(self.db_path, 'w')  # Open file and do nothing -> Results in empty file
            source_file.close()
            self.__db = {}
            
            
    class DISH:
        
        
        class Error:
            
            
            """
            Raise DISH Error, with original format style.
            DISH Errors' format can be controlled. Ex.: More traceback? Edit self.message
            To actually raise the error, call self.send
            
            Args:
                file (str): Absolute file path where exception originated.
                line_number (int, str): Line where exception occured.
                message (str): Details about the exception.
            """
            
            
            def __init__(self, file: str, line_number: int | str, message: str) -> None:
                self.message = f'File "{file}", Line {line_number}:\n\tDISH Error -> {message}'
                self.traceback_layers = 1
                
                
            def add_traceback(self, error: str | type):
                lines = str(error).splitlines()
                first_line = lines[0]
                second_line = lines[1]
                traceback_tabbing_first_line = '\t' * self.traceback_layers
                traceback_tabbing_second_line = traceback_tabbing_first_line + '\t'
                self.message += f'\n{traceback_tabbing_first_line}{first_line}\n{traceback_tabbing_second_line}{second_line}'
                self.traceback_layers += 1
            
            
            def send(self):
                """
                Send error.

                Raises:
                    SystemExit: To kill everything. 
                """
                print(self.message)
                raise SystemExit(1)
            
            
            def __str__(self) -> str:
                return self.message
            
            
            def __repr__(self) -> str:
                return self.__str__()
        
        
    def execute(self, lines: str, file=inspect.stack()[1].filename):
        """
        Execute DISH code to edit data from Python.

        Args:
            lines (str): The lines to execute.

        Returns:
            list: Values you got because of the get statement.
        """
        values = []
        for line_number, rawline in enumerate(lines.splitlines()):
            if rawline.replace(' ', '') == '':
                continue
            line = rawline.strip().split(' ')
            for index, section in enumerate(line):
                section = section.lower()
                try:
                    if section.startswith('$'):
                        break
                except IndexError:
                    pass
                try:
                    if section == 'add' and line[-4].lower() == 'to' and line[-2].lower() == 'in':
                        key = line[-3]
                        value = ' '.join(line[index + 1:-4])
                        if line[-1] == 'end':
                            position = len(self.__db[key])
                        elif line[-1] == 'beginning':
                            position = 0
                        else:
                            position = int(line[-1]) - 1
                        self.__db[key].insert(position, value)
                        break
                except IndexError:
                    pass
                try:
                    if section == 'delete' and line[-2].lower() == 'from':
                        key = line[-1]
                        value = ' '.join(line[index + 1:-2]).split(',')
                        for item in reversed(value):
                            self.__db[key].pop(int(item) - 1)
                        break
                except IndexError:
                    pass
                try:
                    if section == 'create' and line[index + 1].lower() == 'row':
                        self.__db[line[index + 2]] = []
                        break
                except IndexError:
                    pass
                try:
                    if section == 'delete' and line[index + 1].lower() == 'row':
                        key = line[-1]
                        del self.__db[key]
                        break
                except IndexError:
                    pass
                try:
                    if section == 'get' and line[2].lower() == 'from':
                        key = ' '.join(line[3:]).replace(' ', '').split(',')
                        value = line[1]
                        new_value = []
                        if value == '*':
                            for row in key:
                                new_value.append(self.__db[row])
                        else:
                            for row in key:
                                for index in value:
                                    new_value.append(self.__db[row][int(index) - 1])
                        if len(new_value) == 1:
                            values.append(new_value[0])
                        else:
                            values.append(new_value)
                        break
                except IndexError:
                    pass
                try:
                    if section == 'append' and line[-2].lower() == 'to':
                        key = line[-1]
                        value = ' '.join(line[1:-2])
                        self.execute(f'add {value} to {key} in end')
                        break
                except IndexError:
                    pass
                try:
                    if section == 'unshift' and line[-2].lower() == 'to':
                        key = line[-1]
                        value = ' '.join(line[1:-2])
                        self.execute(f'add {value} to {key} in beginning')
                        break
                except IndexError:
                    pass
                try:
                    if section == 'order' and line[-2].lower() == 'by':
                        key = ' '.join(line[1:-2]).split(',')
                        value = line[-1]
                        if value == 'ascending':
                            for rowname in key:
                                self.__db[rowname] = sorted(self.__db[rowname])
                        elif value == 'descending':
                            for rowname in key:
                                self.__db[rowname] = sorted(self.__db[rowname], reverse=True)
                        break
                except IndexError:
                    pass
                try:
                    if section == 'evaluate':
                        if ''.join(line[1:]).replace('+', '').replace('-', '').replace('*', '').replace('/', '').isdigit():
                            values.append(eval(' '.join(line[1:])))
                        break
                except IndexError:
                    pass
                try:
                    if section == 'clear':
                        self.__db.clear()
                        break
                    else:
                        self.DISH.Error(file, line_number + 1, 'Invalid Syntax.').send()
                except IndexError:
                    self.DISH.Error(file, line_number + 1, 'Invalid Syntax.').send()
        if not values:
            return self
        else:
            if len(values) == 1:
                return values[0]
            else:
                return values

                    
    def commit(self):
        """
        Commit the changes.
        """
        if not self.__db:
            open(self.db_path, 'w').close()
        keys = list(self.__db.keys())
        values = list(self.__db.values())
        changes = ','.join(keys) + '\n'
        for index, value in enumerate(','.join(map(str, values)).split(',')):
            for row in values:
                try:
                    changes += row[index] + ','
                except:
                    break
            changes += '\n'
        changes = "\n".join([ll.rstrip() for ll in changes.splitlines() if ll.strip()])  # Take off empty lines
        file = open(self.db_path, 'w')
        file.write(open(self.db_path).read() + changes)
        file.close()
        self.changes += 1
        return self
            
        
    def __str__(self) -> str:
        return str(self.__db)
    
    
    def __getitem__(self, key):
        return self.__db.get(key, None)
    
    
    def __setitem__(self, key, value):
        self.__db[key] = value


class Template:
    
    
    def __init__(self, path: str) -> None:
        self.path = path
    
    
    def render(self, context: dict):
        """
        Renders the values to the given file path.

        Args:
            path (str): The path to the template.
            context (dict): The names of the values to be replaced and the values to replace the names.
        """
        filecontext = open(self.path).read()
        for name in context:
            filecontext = filecontext.replace('[% ' + name + ' %]', context.get(name, None))
        open(self.path, 'w').write(filecontext)
        
        
    def for_loop(self, start: int, end: int, start_insert: int, times: int):
        """
        Does a for loop.

        Args:
            path (str): The path to the template.
            start (int): The line number to begin for for looping.
            end (int): The ending line number to begin for for looping.
            start_insert (int): The beginning line number to insert results of for loop.
            times (int): How many times it is supposedly for looped.
        """
        listforlooplines = open(self.path).read().split('\n')[start - 1:end]
        forlooplines = ''
        for forloopline in listforlooplines:
            forlooplines += forloopline + '\n'
        l_t_i = start_insert - 1
        forlist = [filecontent.split(' ') for filecontent in open(self.path).read().split('\n')]
        for i in range(times - 1):
            forlist.insert(l_t_i, [forlooplines + '\n'])
            l_t_i += 1
        paper = ''
        for line in forlist:
            for column in line:
                paper += column + ' '
            paper += '\n'
        open(self.path, 'w').write(''.join(paper))
        
        
    def __str__(self) -> str:
        return open(self.path).read()
