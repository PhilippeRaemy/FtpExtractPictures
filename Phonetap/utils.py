from datetime import datetime
import json


class Tracer:
    def __init__(self, verbose, indent=None):
        self.indent = indent
        self.verbose = verbose
        self.start_time = datetime.now()

    def trace(self, *args, **kwargs):
        message = {'elapse': f'{(datetime.now() - self.start_time).total_seconds():.3f}'}
        if len(args) == 0:
            if kwargs:
                message.update(kwargs)
        else:
            txt = ' '.join((str(a) for a in args))
            if kwargs:
                message[txt] = kwargs
            else:
                message['':txt]

        print(json.dumps(message, indent=self.indent))


    def chat(self, *args, **kwargs):
        if self.verbose:
            self.trace(*args, **kwargs)
