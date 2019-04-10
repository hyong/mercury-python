# -*- coding: utf-8 -*-
#
# Copyright 2018-2019 Accenture Technology
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import time
from mercury.platform import Platform
from mercury.system.models import EventEnvelope
from mercury.system.po import PostOffice


class Hi:

    @staticmethod
    def hello(headers: dict, body: any):
        # singleton function signature (headers: dict, body: any)
        Platform().log.info(str(headers) + ", " + str(body))
        return body


def hello(headers: dict, body: any, instance: int):
    # regular function signature (headers: dict, body: any, instance: int)
    Platform().log.info("#"+str(instance)+" "+str(headers)+" "+str(body))
    # to set status, headers and body, return them in an event envelope
    result = EventEnvelope().set_header('hello', 'world').set_body(body)
    for h in headers:
        result.set_header(h, headers[h])
    return result


def main():
    platform = Platform()
    # you can register a method of a class
    platform.register('hello.world.1', Hi().hello, 5)
    # or register a function
    platform.register('hello.world.2', hello, 10)

    po = PostOffice()
    # send asynchronously. Note that key-values in the headers will be encoded as str
    po.send('hello.world.1', headers={'one': 1}, body='hello world one')
    po.send('hello.world.2', headers={'two': 2}, body='hello world two')

    # make a RPC request
    try:
        result = po.request('hello.world.2', 2.0, headers={'some_key': 'some_value'}, body='test message')
        if isinstance(result, EventEnvelope):
            print('Received RPC response:')
            print("HEADERS =", result.get_headers(), ", BODY =", result.get_body(),
                  ", STATUS =",  result.get_status(),
                  ", EXEC =", result.get_exec_time(), ", ROUND TRIP =", result.get_round_trip(), "ms")
    except TimeoutError as e:
        print("Exception: ", str(e))

    # connect to the network
    platform.connect_to_cloud()
    # wait until connected
    while not platform.is_cloud_connected():
        try:
            time.sleep(0.1)
        except KeyboardInterrupt:
            # this allows us to stop the application while waiting for cloud connection
            platform.stop()
            return

    for i in range(10):
        po.broadcast("hello.world.2", body=str(i)+" this is a broadcast message from "+platform.get_origin())
    #
    # this will keep the main thread running in the background
    # so we can use Control-C or KILL signal to stop the application
    platform.run_forever()


if __name__ == '__main__':
    main()

