#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
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
import webapp2
import endpoints
from google.appengine.ext import ndb
from protorpc import remote

from endpoints_proto_datastore.ndb import EndpointsModel

# class MainHandler(webapp2.RequestHandler):
#     def get(self):
#         self.response.write('Hello world!')
#
# app = webapp2.WSGIApplication([
#     ('/', MainHandler)
# ], debug=True)

class Task(EndpointsModel):
    name = ndb.StringProperty(required=True)
    owner = ndb.StringProperty()

@endpoints.api(name='tasks', version='vGDL',
               description='API for task method')
class TaskApi(remote.Service):

    @Task.method(name = 'task.insert',
                 path = 'task',
                 http_method = 'POST')#this part is not needed as POST is default
    def insert_task(self,task):
        task.put()
        return task

    @Task.query_method(name = 'task.list',
                 path = 'task',
                 http_method = 'GET')#this part is not needed as GET is default
    def list_tasks(self,query):
        return query


# creates aplication
application = endpoints.api_server([TaskApi])