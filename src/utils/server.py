import asyncio

from aiter import push_aiter


async def start_server_aiter(port):
    aiter = push_aiter()
    server = await asyncio.start_server(client_connected_cb=lambda r, w: aiter.push((r, w)), port=port)
    aiter.task = asyncio.ensure_future(server.wait_closed()).add_done_callback(lambda f: aiter.stop())
    return server, aiter


async def start_unix_server_aiter(path):
    aiter = push_aiter()
    server = await asyncio.start_unix_server(client_connected_cb=lambda r, w: aiter.push((r, w)), path=path)
    aiter.task = asyncio.ensure_future(server.wait_closed()).add_done_callback(lambda f: aiter.stop())
    return server, aiter


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
