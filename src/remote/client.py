import asyncio
import weakref

from aiter import map_aiter

from chiasim.utils.cbor_messages import reader_to_cbor_stream, xform_to_cbor_message

from .proxy import make_proxy


class RemoteError(Exception):
    pass


# TODO: this belongs in aiter

class NonceWatcher:
    """
    This class looks at (nonce, result) events coming out of an aiter called "message stream"
    and routes them to corresponding futures returned by "future_for_nonce". It's essentially
    an event router that uses a dictionary to route the events to the appropriate places.
    """

    def __init__(self, message_stream, initial_nonce=0):
        self._message_stream = message_stream
        self._nonce_to_future = weakref.WeakValueDictionary()
        self._initial_nonce = initial_nonce
        self._task = asyncio.ensure_future(self.run())

    def future_for_nonce(self, nonce):
        if self._task.done():
            raise ConnectionResetError()
        if nonce not in self._nonce_to_future:
            f = asyncio.Future()
            self._nonce_to_future[nonce] = f
        return self._nonce_to_future[nonce]

    async def run(self):
        async for nonce, result in self._message_stream:
            future = self._nonce_to_future.get(nonce)
            if future and not future.done():
                future.set_result(result)
        ex = ConnectionResetError()
        for k, f in self._nonce_to_future.items():
            if not f.done():
                f.set_exception(ex)

    def next_nonce(self):
        r = self._initial_nonce
        self._initial_nonce += 1
        return r


async def invoke_remote(method, remote, *args, **kwargs):
    """
    Send the given message to the remote and return the transformed
    response.
    """
    nonce_watcher, writer = remote.get("nonce_watcher"), remote.get("writer")
    nonce = nonce_watcher.next_nonce()
    msg = dict(c=method, n=nonce, q=kwargs)
    future = nonce_watcher.future_for_nonce(nonce)
    cbor_msg = xform_to_cbor_message(msg)
    writer.write(cbor_msg)

    _ = await future
    transformation = remote.get("signatures", {}).get(method)
    if transformation:
        _ = transformation(_)
    return _


def event_stream_to_nonce_result(event):
    """
    Convert the event into a nonce/result pair.
    """
    nonce = event.get("n")
    if "e" in event:
        r = RemoteError(event.get("e"))
    else:
        r = event.get("r")
    return nonce, r


def request_response_proxy(reader, writer, remote_signatures={}):
    """
    Create a proxy object that handles request/response for the given remote.
    You can optionally pass in signatures for automatic conversion of key
    values from bytes (or other cbor objects) to specific types.
    """
    nonce_watcher = NonceWatcher(map_aiter(event_stream_to_nonce_result, reader_to_cbor_stream(reader)))
    d = dict(reader=reader, writer=writer, signatures=remote_signatures, nonce_watcher=nonce_watcher)
    return make_proxy(invoke_remote, d)


def xform_dict(**kwargs):
    def transform(message):
        new_message = dict(message)
        for k, v in kwargs.items():
            new_message[k] = v(message[k])
        return new_message
    return transform
