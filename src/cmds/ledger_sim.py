import argparse
import asyncio
import logging
import sys

from aiter import map_aiter

from chiasim.ledger import ledger_api
from chiasim.remote.api_server import api_server
from chiasim.storage import RAM_DB
from chiasim.utils.log import init_logging
from chiasim.utils.server import start_server_aiter

log = logging.getLogger(__name__)


def run_ledger_api(server, aiter):
    db = RAM_DB()
    INITIAL_BLOCK_HASH = bytes(([0] * 31) + [1])
    ledger = ledger_api.LedgerAPI(INITIAL_BLOCK_HASH, db)
    rws_aiter = map_aiter(lambda rw: dict(reader=rw[0], writer=rw[1], server=server), aiter)
    return api_server(rws_aiter, ledger)


def ledger_command(args):
    server, aiter = asyncio.get_event_loop().run_until_complete(start_server_aiter(args.port))
    log.info("listening on %s", args.port)
    return run_ledger_api(server, aiter)


def main(args=sys.argv):
    parser = argparse.ArgumentParser(
        description="Chia ledger simulator."
    )
    parser.add_argument("-p", "--port", help="remote port", default=9868)
    parser.set_defaults(func=ledger_command)

    args = parser.parse_args(args=args[1:])

    init_logging()

    run = asyncio.get_event_loop().run_until_complete

    tasks = set()

    tasks.add(asyncio.ensure_future(args.func(args)))

    run(asyncio.wait(tasks))


if __name__ == "__main__":
    main()


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
