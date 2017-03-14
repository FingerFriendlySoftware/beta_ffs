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

# TODO learn to spell @zachary_rothberg
import webapp2
import endpoints
from google.appengine.ext import ndb
from protorpc import remote
from endpoints_proto_datastore.ndb import EndpointsAliasProperty
from endpoints_proto_datastore.ndb import EndpointsModel
from endpoints_proto_datastore.ndb import EndpointsUserProperty
# class MainHandler(webapp2.RequestHandler):
#     def get(self):
#         self.response.write('Hello world!')
#
# app = webapp2.WSGIApplication([
#     ('/', MainHandler)
# ], debug=True)

class Task(EndpointsModel):
    name = ndb.StringProperty(required=True)
    stress_level = ndb.IntegerProperty(required=True)
    difficulty = ndb.IntegerProperty(choices=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    time = ndb.DateTimeProperty(auto_now_add=True)
    description = ndb.TextProperty()
    owner = EndpointsUserProperty(required= True, raise_unauthorized= True)


class Patient(EndpointsModel):
    _message_fields_schema = ('id', 'user', 'address', 'medications', 'doctors',
                              'diagnosis_codes', 'appointments', 'name', 'date_of_birth', 'age',
                              'emergency_contacts', 'phone_number', 'insurance')
    user = EndpointsUserProperty(required=True, raise_unauthorized=True)


class Address(EndpointsModel):
    street_line = ndb.StringProperty()
    city = ndb.StringProperty()
    state = ndb.StringProperty()# TODO add dictionary with state abrivaitions
    zipcode = ndb.IntegerProperty() # TODO add zip dictionary maybe optional statedeclarition
    # TODO add parent and ID
    # TODO possibly add primary flag


class Medication(EndpointsModel):
    drug = ndb.StringProperty() # TODO consider making it a property or class
    refill_date = ndb.DateProperty()
    contradictions = ndb.TextProperty()
    dose = ndb.StringProperty()# TODO combine with drug
    count = ndb.IntegerProperty()

class ICD10DiagnosisCode(EndpointsModel):
    code_first_stem = ndb.StringProperty()# TODO convert codes in data so can search by value
    code_second_stem = ndb.StringProperty()# TODO combine in alias property keep seperate for
                                           #  more robust indexing(search for subcodes or global more esally)


# TODO move modles and api to seperate files
#################################################################
@endpoints.api(name='tasks', version='vGDL',
               description='API for task method')
class TaskApi(remote.Service):

    @Task.method(
                 request_fields=('name','stress_level', 'difficulty', 'description'), # forces customization? #must be tuple
                 name = 'task.insert',
                 path = 'task',
                 http_method = 'POST')#this part is not needed as POST is default
    def insert_task(self,task):
        task.put()
        return task

    @Task.query_method(user_required=True,
                name = 'task.list',
                 path = 'task',
                use_projection=True,
                 http_method = 'GET')#this part is not needed as GET is default
    def list_tasks(self,query):
        return query

# creates aplication
application = endpoints.api_server([TaskApi])