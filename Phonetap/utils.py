from datetime import datetime
import json


class Tracer:
    def __init__(self, verbose, indent=None, newline='\n', prefix='', padding=''):
        self.prefix = prefix
        self.newline = newline
        self.indent = indent
        self.verbose = verbose
        self.start_time = datetime.now()
        self.count = 0
        self.padding = padding

    def trace(self, *args, **kwargs):
        self.count += 1
        elapse = (datetime.now() - self.start_time).total_seconds()
        message = {'elapse[s]': f'{self.count}/{elapse :.3f}', 'pace[/s]': f'{self.count / elapse:.3f}'}
        if len(args) == 0:
            if kwargs:
                message.update(kwargs)
        else:
            txt = ' '.join((str(a) for a in args))
            if kwargs:
                message[txt] = kwargs
            else:
                message['':txt]

        print(self.prefix + json.dumps(message, indent=self.indent)+self.padding, end=self.newline)

    def chat(self, *args, **kwargs):
        if self.verbose:
            self.trace(*args, **kwargs)
