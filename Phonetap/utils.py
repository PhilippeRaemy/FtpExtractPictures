from datetime import datetime
import json


class Tracer:
    def __init__(self, verbose, indent=None):
        self.indent = indent
        self.verbose = verbose
        self.start_time = datetime.now()

    def trace(self, *args, **kwargs):
        print(json.dumps({'e': f'{(datetime.now() - self.start_time).total_seconds():.3f}',
                          'm': args[0] if len(args) == 1 and not kwargs
                          else ' '.join(str(args)) if not kwargs
                          else kwargs if not args
                          else {' '.join(str(args)): kwargs}}, indent=self.indent))

    def chat(self, *args, **kwargs):
        if self.verbose:
            self.trace(*args, **kwargs)
