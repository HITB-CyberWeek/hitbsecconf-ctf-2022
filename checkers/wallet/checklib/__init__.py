import enum
import functools
import logging
import signal
import sys

import requests


class StatusCode(enum.Enum):
    OK = 101
    CORRUPT = 102
    MUMBLE = 103
    DOWN = 104
    ERROR = 110

    def __str__(self):
        return "%s (%d)" % (self._name_, self.value)


class exception_wrapper:
    def __init__(self, code):
        # TODO (andgein): add ignorable exceptions. I.e. NotImplementedError should be ignored and raised for
        # the CHECKER_ERROR status
        self.exit_code = code

    def __call__(self, fn):
        code = self.exit_code

        @functools.wraps(fn)
        def wrapper(self, *args, **kwargs):
            try:
                fn(self, *args, **kwargs)
            except Exception as e:
                logging.info('Caught exception: %s', e)
                logging.exception(e)

                if isinstance(e, requests.exceptions.RequestException):
                    logging.debug('It\'s exception from module `requests`')

                self.exit(code, str(e))
            else:
                self.exit(StatusCode.OK)

        return wrapper


class Checker:
    def __init__(self, set_interrupt_signal_handlers=True):
        logging.basicConfig(format='%(asctime)-15s [%(levelname)s] %(message)s',
                            level=logging.DEBUG)
        if set_interrupt_signal_handlers:
            self._set_signal_handlers()

    def _signal_handler(self, signum, frame):
        logging.warning("Received signal: %s at %s, line %s", signum,
                        frame.f_code, frame.f_lineno)
        sys.stdout.flush()
        sys.stderr.flush()
        self.exit(StatusCode.ERROR)

    def _set_signal_handlers(self):
        for signal_name in ['SIGTERM', 'SIGINT', 'SIGABRT', 'CTRL_C_EVENT',
                            'CTRL_BREAK_EVENT']:
            if hasattr(signal, signal_name):
                try:
                    signal.signal(getattr(signal, signal_name),
                                  self._signal_handler)
                except ValueError:
                    pass

    def check(self, address):
        raise NotImplementedError()

    def put(self, address, flag_id, flag, vuln):
        raise NotImplementedError()

    def get(self, address, flag_id, flag, vuln):
        raise NotImplementedError()

    def info(self):
        raise NotImplementedError()

    def exit(self, code: StatusCode, message: str = ''):
        if message != '':
            logging.info('Exit with code %s and message "%s"', code, message)
            print(message)
        else:
            logging.info('Exit with code %s', code)

        sys.exit(code.value)

    def mumble_if_false(self, statement, public_message='Invalid content', private_message=''):
        self.exit_with_error_if_false(statement, StatusCode.MUMBLE, public_message, private_message)

    def corrupt_if_false(self, statement, public_message='Can\'t find previously installed flag on the service',
                         private_message=''):
        self.exit_with_error_if_false(statement, StatusCode.CORRUPT, public_message, private_message)

    def exit_with_error_if_false(self, statement, status_code: StatusCode, public_message='Invalid content',
                                 private_message=''):
        if not statement:
            if private_message != '':
                logging.error(private_message)
            self.exit(status_code, public_message)

    @exception_wrapper(StatusCode.DOWN)
    def run_command(self, function, arguments):
        if len(arguments) == 0:
            logging.info('Run "%s" without arguments', function.__name__)
        else:
            logging.info('Run "%s" with arguments %s', function.__name__, arguments)
        function(*arguments)

    @exception_wrapper(StatusCode.ERROR)
    def run(self, args=None):
        if args is None:
            args = sys.argv[1:]

        args.extend([''] * 4)

        try:
            command, address, flag_id, flag, vuln_id = args[:5]
        except ValueError:
            self.exit(StatusCode.ERROR, 'Invalid arguments: %r' % (sys.argv[1:], ))
            return

        # For backward compatibility
        if vuln_id == '':
            vuln_id = '1'

        vuln_id = int(vuln_id)

        commands = {'info': {'method': self.info,
                             'arguments': []},
                    'check': {'method': self.check,
                              'arguments': [address]},
                    'put': {'method': self.put,
                            'arguments': [address, flag_id, flag, vuln_id]},
                    'get': {'method': self.get,
                            'arguments': [address, flag_id, flag, vuln_id]}
                    }

        if command not in commands:
            self.exit(StatusCode.ERROR, 'Invalid command: %s' % command)

        self.pre_run_command_hook(command, commands[command]['arguments'])

        self.run_command(commands[command]['method'],
                         commands[command]['arguments'])

    def pre_run_command_hook(self, command, arguments):
        """ Implement pre_run_command_hook() in your checker to run some code before info(), check(), put() or get() """
        pass


class CheckerException(Exception):
    pass
