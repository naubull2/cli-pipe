import time
from functools import update_wrapper, wraps

import click
from pathos.multiprocessing import ProcessingPool as Pool


@click.group(chain=True)
def cli():
    """Pipeline any following sub commands in the given order, lazily processing each data.
    """
    pass


@cli.result_callback()
def process_commands(processors):
    """This result callback is invoked with an iterable of all the chained
    subcommands.  As in this example each subcommand returns a function
    we can chain them together to feed one into the other, similar to how
    a pipe on unix works.
    """
    # Start with an empty iterable.
    stream = ()
    start_time = time.time()
    # Pipe it through all stream processors.
    for processor in processors:
        stream = processor(stream)

    # Evaluate the stream and throw away the items.
    for _ in stream:
        pass
    print(f"{(time.time()-start_time) * 1000} msecs taken!")


def processor(f):
    """Helper decorator to rewrite a function so that it returns another
    function from it.
    """

    def new_func(*args, **kwargs):
        def processor(stream):
            return f(stream, *args, **kwargs)

        return processor

    return update_wrapper(new_func, f)


def generator(f):
    """Similar to the func:`processor` but passes through old values
    unchanged and does not pass through the values as parameter.
    """
    @processor
    def new_func(stream, *args, **kwargs):
        yield from stream
        yield from f(*args, **kwargs)

    return update_wrapper(new_func, f)


def parallel(num_process, initializer=None):
    def decorator(func):
        @wraps(func)
        def wrapper(iterable):
            pool = Pool(num_process)
            if initializer is not None:
                pool.map(initializer, range(num_process))
            results = pool.imap(func, iterable)
            for result in results:
                yield result
        return wrapper
    return decorator
