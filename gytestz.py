"""
A module for running unit tests, etc. Mainly used for griffin / mythjiv, but it can also be used for other things. Comes preinstalled with griffin / mythjiv.
"""


def runfunctest(testfunc):
    """
    Runs a test function and says if it has an error. Also creates a tab in your browser with the error as the search.

    Args:
        testfunc (function): Test function to be checked
    """
    import sys, time, traceback, webbrowser
    print('------Session Started------')
    try:
        testfunc()
    except Exception as e:
        pass
        exceptiontype, exceptionmessage, line = sys.exc_info()
        exceptiontype = f'{exceptiontype}'.replace("<class '", '').replace("'>", '')
        ec = '---Exception caught---'
        et = f'Exception: {exceptiontype}: {exceptionmessage}'
        efc = f'File Exception Caught: {traceback.format_exc()[traceback.format_exc().rindex(" File ") + 1:traceback.format_exc().rindex(", line ")].replace("File ", "")}'
        lc = f'Line caught: {traceback.format_exc()[traceback.format_exc().rindex(" line ") + 1:traceback.format_exc().rindex(",")].replace("line ", "")}'
        dt = f'Date And Time Error Occured: {time.strftime("%m/%d/%Y %H:%M:%S")}'
        print(f'\033[31m \n{ec} \033[0m \n{dt}\n\033[31m{et} \033[0m \n{efc}\n{lc}\n')
        try:
            content = open('Exception_cache.che').read()
            open('Exception_cache.che', 'w').write(content + f'\n\n\n\n------Session Started------\n\n{ec}\n{dt}\n{et}\n{efc}\n{lc}\n\n------Session Ended------')
        except:
            open('Exception_cache.che', 'w').write(f'\n\n\n\n------Session Started------{ec}\n{dt}\n{et}\n{efc}\n{lc}\n\n------Session Ended------')
        time.sleep(1)
        webbrowser.open(f'https://www.google.com.tr/search?q={exceptiontype}: {exceptionmessage}'.replace(' ', '%20'))
    print('------Session Ended------')
        
        
def test_run_all_methods(testclass, reverse=False):
    """
    A function to test every method in a class. Uses runfunctest() to test the method.

    Args:
        testclass (class): Test class to be run. Must be initialized first.
        reverse (bool, optional): If set to true, reverses method order to be tested. Defaults to False.
    """
    print('------Running all methods------\n\n')
    methods = [method for method in dir(testclass) if callable(getattr(testclass, method)) if not method.startswith('_')]
    if reverse:
        pass
    else:
        methods.reverse()
    for method in methods:
        m = getattr(testclass, method)
        print(f'Running {m} in next session')
        runfunctest(m)
    print('\n\n------Ran all methods------')


def reset_cache():
    """
    Resets the cache from Exception_cache.che

    Raises:
        FileNotFoundError: Raised if Exception_cache.che is not created yet.
    """
    import os.path as path
    try:
        open(path.abspath('Exception_cache.che'))
        open(path.abspath('Exception_cache.che'), 'w').write('')
    except:
        raise FileNotFoundError('"Exception_cache.che" not initialized')
