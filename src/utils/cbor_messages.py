import asyncio
import logging
import struct

import cbor

log = logging.getLogger(__name__)


async def reader_to_cbor_stream(reader):
    """
    Turn a reader into a generator that yields cbor messages.
    """
    while True:
        try:
            message_size_blob = await reader.readexactly(4)
            message_size, = struct.unpack(">L", message_size_blob)
            blob = await reader.readexactly(message_size)
            message = cbor.loads(blob)
            log.debug("got msg %s", message)
            yield message
        except (IOError, asyncio.IncompleteReadError):
            log.info("EOF stream %s", reader)
            break
        except ValueError:
            log.info("badly formatted cbor from stream %s", reader)
            break
        except Exception as ex:
            log.exception("unknown error in stream %s", reader)
            break


def transform_to_streamable(d):
    """
    Drill down through dictionaries and lists and transform objects with "bytes()" to bytes.
    """
    if hasattr(d, "__bytes__"):
        return bytes(d)
    if d is None or isinstance(d, (str, bytes, int)):
        return d
    if isinstance(d, dict):
        new_d = {}
        for k, v in d.items():
            new_d[transform_to_streamable(k)] = transform_to_streamable(v)
        return new_d
    return [transform_to_streamable(_) for _ in d]


def xform_to_cbor_message(msg):
    msg_blob = cbor.dumps(transform_to_streamable(msg))
    length_blob = struct.pack(">L", len(msg_blob))
    return length_blob + msg_blob


"""
Copyright 2019 Chia Network Inc

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
