import argparse
import asyncio
import json
import sys

from chiasim.utils.log import init_logging
from chiasim.remote.client import request_response_proxy


def main(args=sys.argv):
    parser = argparse.ArgumentParser(
        description="Chia client."
    )

    parser.add_argument("-p", "--port", help="remote port", default=9868)
    parser.add_argument("host", help="remote host")
    parser.add_argument("function", help="function")
    parser.add_argument(
        "arguments", help="arguments (as json)", type=json.loads)

    args = parser.parse_args(args=args[1:])

    init_logging()

    run = asyncio.get_event_loop().run_until_complete

    reader, writer = run(asyncio.open_connection(args.host, args.port))
    ledger_api = request_response_proxy(reader, writer)

    r = run(getattr(ledger_api, args.function)(**args.arguments))
    print(r)


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
