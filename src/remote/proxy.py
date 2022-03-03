
def make_proxy(make_invocation_f, context=None):
    """
    This function creates a "proxy" object that turns all its attributes
    into callables that simply invoke "make_invocation_f" with the name
    of the attribute and the given context.

    This is so you can create a proxy, then do something like

    proxy.call_my_function(foo, bar)

    and it will actually do

    make_invocation_f("call_my_function", context, foo, bar)

    so the make_invocation_f can actually do a remote procedure call.
    """

    class Proxy:
        @classmethod
        def __getattribute__(self, attr_name):
            def invoke(*args, **kwargs):
                return make_invocation_f(attr_name, context, *args, **kwargs)
            return invoke

    return Proxy()
