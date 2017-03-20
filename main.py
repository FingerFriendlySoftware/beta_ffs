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
from endpoints_proto_datastore.ndb import EndpointsDateProperty
from datetime import date
from datetime import datetime

# class MainHandler(webapp2.RequestHandler):
#     def get(self):
#         self.response.write('Hello world!')
#
# app = webapp2.WSGIApplication([
#     ('/', MainHandler)
# ], debug=True)

class Patient(EndpointsModel):
    name = ndb.StringProperty()
    user = EndpointsUserProperty(required=True, raise_unauthorized=True)
    date_of_birth = EndpointsDateProperty()
    age = ndb.IntegerProperty()

    def calculate_age(self):
        today = date.today()
        birthday = self.date_of_birth
        self.age = today.year - birthday.year - ((today.month, today.day) < (birthday.month , birthday.day))

    def _pre_put_hook(self):
        if self.date_of_birth:
            self.calculate_age()



class Address(EndpointsModel):
    _message_fields_schema = ('id', 'street_line', 'city', 'state', 'zipcode')

    street_line = ndb.StringProperty()
    city = ndb.StringProperty()
    state = ndb.StringProperty()# TODO add dictionary with state abrivaitions
    zipcode = ndb.StringProperty()  # dont make int breaks TODO add zip dictionary maybe optional statedeclarition
    # TODO add parent
    # TODO possibly add primary flag
    # TODO geographically add address and vise versa


class Drug(EndpointsModel):
    _message_fields_schema = ('id', 'name', 'contradictions', 'dose_in_strength',
                              'package', 'image', 'directions')
    name = ndb.StringProperty()
    contradictions= ndb.StringProperty(repeated=True)  # may need to move removed
    dose_in_strength = ndb.StringProperty()
    package = ndb.TextProperty()
    image = ndb.BlobProperty()
    directions = ndb.TextProperty()


class Medication(EndpointsModel):
    _message_fields_schema = ('id', 'drug', 'refill_date', 'dose_quantity',
                              'count', 'lot_number', 'over_riding_directions')
    drug = ndb.StructuredProperty(Drug)
    refill_date = ndb.DateProperty()
    dose_quantity = ndb.StringProperty()
    count = ndb.IntegerProperty()
    over_riding_directions= ndb.TextProperty()
    lot_number = ndb.StringProperty()

class PhoneNumber(EndpointsModel):
    _message_fields_schema = ('id', 'area_code', 'primary', 'extension')
    area_code = ndb.StringProperty()
    primary = ndb.StringProperty()
    extension = ndb.StringProperty()


class DoctorStub(EndpointsModel):
    _message_fields_schema = ('id','name', 'profession', 'picture', 'address_book',
                              'number_book')
    name = ndb.StringProperty()
    profession = ndb.StringProperty()# TODO add allowable values
    picture = ndb.BlobProperty(indexed=False) # TODO actually make work DONT FUCKING USE
    address_book = ndb.StructuredProperty(Address, repeated=True)
    number_book = ndb.StructuredProperty(PhoneNumber, repeated=True)

class DiagnosisCode(EndpointsModel):
    _message_fields_schema = ('id', 'code_first_stem', 'code_second_stem', 'code_type', 'description')
    code_first_stem = ndb.StringProperty()  # TODO convert codes in data so can search by value
    code_second_stem = ndb.StringProperty()  # TODO combine in alias property keep seperate for
                                             # more robust indexing(search for subcodes or global more easily)
    code_type = ndb.StringProperty(choices=['DSMIV', 'ICD10', 'ICD9'])
    description = ndb.TextProperty()

class Diagnosis(EndpointsModel):
    _message_fields_schema = ('id', 'code', 'diagnosis_date', 'diagnosed_by')
    code = ndb.StructuredProperty(DiagnosisCode)
    diagnosis_date = ndb.DateProperty()
    diagnosed_by = ndb.StructuredProperty(DoctorStub)



class Appointment(EndpointsModel):
    _message_fields_schema = ('id', 'appointment_date', 'appointment_time', 'location', 'with_whom')
    appointment_date = ndb.DateProperty()
    appointment_time = ndb.TimeProperty()
    location = ndb.StructuredProperty(Address)
    with_whom = ndb.StructuredProperty(DoctorStub)


class InsurancePlan(EndpointsModel): # TODO expand InsurancePlan
    _message_fields_schema = ('id', 'company', 'insurance_type')
    company = ndb.StringProperty()
    insurance_type = ndb.StringProperty()


class Insurance(EndpointsModel):
    _message_fields_schema = ('id', 'member_name', 'relation', 'member_id', 'group_number',
                              'contract_type', 'plan')

    member_name = ndb.StringProperty()
    relation = ndb.StringProperty() # TODO add chocies
    member_id = ndb.StringProperty()
    group_number = ndb.StringProperty()
    contract_type = ndb.StringProperty()
    plan = ndb.StructuredProperty(InsurancePlan)



# TODO class emergency_contact maybe just make list in user



# TODO class provider




# TODO move models and api to seperate files
#################################################################



@endpoints.api(name='library', version='v1.0',
               allowed_client_ids=('237046111297-f7jpslg152jqau9alqkvmkpfqilkv4qr',),
               audiences=['237046111297-f7jpslg152jqau9alqkvmkpfqilkv4qr.apps.googleusercontent.com',])
class LibraryApi(remote.Service):
    @Patient.method(
                    request_fields=('name', 'date_of_birth'),
                    name='patient.insert',
                    path='patient')
    def insert_patient(self,patient):
        if patient.date_of_birth: # TODO find a better way
            if patient.date_of_birth.year <1900:
                raise endpoints.BadRequestException('date <= 1900')
        patient.put()
        return patient

    @Patient.query_method(user_required=True,
                          query_fields=['name'],
                          name='patient.query',
                          path='patient')
    def query_patient(self,query):
        return query


#######################################################################################

    @Address.method(request_fields=('street_line', 'city', 'state', 'zipcode'),
                    user_required=True,
                    name='address.insert',
                    path='address')
    def insert_address(self,address):
        address.put()
        return address

    @Address.query_method(user_required=True,
                          query_fields=['street_line', 'city', 'state', 'zipcode'],
                          name='address.query',
                          path='address')
    def query_address(self,query):
        return query


##############################################################################################
    @Appointment.method(request_fields=('appointment_date', 'appointment_time',
                                        'location', 'with_whom'),
                        user_required=True,
                        name='appointment.insert',
                        path='appointment')
    def insert_appointment(self, address):
        address.put()
        return address

    @Appointment.query_method(user_required=True,
                              query_fields=['appointment_date', 'appointment_time'],
                              name='appointment.query',
                              path='appointment')
    def query_appointment(self, query):
        return query


###############################################################################################
    @Medication.method(request_fields=('drug', 'refill_date', 'dose_quantity',
                                       'count', 'lot_number','over_riding_directions'),
                       user_required=True,
                       name='medication.insert',
                       path='medication')
    def insert_medication(self, Medication):
        Medication.put()
        return Medication

    @Medication.query_method(user_required=True,
                             query_fields=['refill_date', 'dose_quantity', 'count', 'lot_number'],
                             name='medicationquery',
                             path='medication')
    def query_medication(self, query):
        return query


 #################################################################################################

    @Drug.method(request_fields=('name', 'contradictions', 'dose_in_strength', 'package',
                                 'image', 'directions'),
                 user_required=True,
                 name='drug.insert',
                 path='drug')
    def insert_drug(self, Drug):
        Drug.put()
        return Drug

    @Drug.query_method(user_required=True,
                       query_fields=['name', 'contradictions', 'dose_in_strength'],
                       name='drug.query',
                       path='drug')
    def query_drug(self, query):
        return query

#############################################################################################

    @DiagnosisCode.method(request_fields=('code_first_stem', 'code_second_stem','code_type','description'),
                          user_required=True,
                          name='diagnosis_code.insert',
                          path='diagnosis_code')
    def insert_diagnosis_code(self, diagnosis_code):
        diagnosis_code.put()
        return diagnosis_code

    @DiagnosisCode.query_method(user_required=True,
                                query_fields=['code_first_stem', 'code_second_stem', 'code_type'],
                                name='diagnosis_code.query',
                                path='diagnosis_code')
    def query_diagnosis_code(self, query):
        return query

#########################################################################################################

    @Diagnosis.method(request_fields=('code', 'diagnosis_date', 'diagnosed_by'),
                      user_required=True,
                      name='diagnosis.insert',
                      path='diagnosis')
    def insert_diagnosis(self, diagnosis):
        diagnosis.put()
        return diagnosis

    @Diagnosis.query_method(user_required=True,
                            query_fields=['diagnosis_date'],
                            name='diagnosis.query',
                            path='diagnosis')
    def query_diagnosis(self, query):
        return query

#########################################################################################################

    @Insurance.method(request_fields=('member_name', 'relation', 'member_id', 'group_number',
                                      'contract_type', 'plan'),
                      user_required=True,
                      name='insurance.insert',
                      path='insurance')
    def insert_insurance(self, insurance):
        insurance.put()
        return insurance

    @Insurance.query_method(user_required=True,
                            query_fields=['member_name', 'relation', 'member_id', 'group_number',
                                          'contract_type'],
                            name='insurance.query',
                            path='insurance')
    def query_insurance(self, query):
        return query


#########################################################################################################

    @InsurancePlan.method(request_fields=('company', 'insurance_type'),
                          user_required=True,
                          name='insurance_plan.insert',
                          path='insurance_plan')
    def insert_insurance(self, insurance):
        insurance.put()
        return insurance

    @InsurancePlan.query_method(user_required=True,
                                query_fields=['company', 'insurance_type'],
                                name='insurance_plan.query',
                                path='insurance_plan')
    def query_insurance_plan(self, query):
        return query


#########################################################################################################

    @PhoneNumber.method(request_fields=('area_code', 'primary', 'extension'),
                        user_required=True,
                        name='phone_number.insert',
                        path='phone_number')
    def insert_phone_number(self, phone_number):
        phone_number.put()
        return phone_number

    @PhoneNumber.query_method(user_required=True,
                              query_fields=['area_code', 'primary', 'extension'],
                              name='phone_number.query',
                              path='phone_number')
    def query_phone_number(self, query):
        return query


#########################################################################################################

    @DoctorStub.method(request_fields=('name', 'profession', 'picture', 'address_book',
                                       'number_book'),
                       user_required=True,
                       name='doctor_stub.insert',
                       path='doctor_stub')
    def insert_doctor_stub(self, doctor_stub):
        doctor_stub.put()
        return doctor_stub

    @DoctorStub.query_method(user_required=True,
                             query_fields=['name', 'profession'],
                             name='doctor_stub.query',
                             path='doctor_stub')
    def query_doctor_stub(self, query):
        return query


# creates aplication
temp= endpoints.api_server([LibraryApi], restricted=False)

application = temp
