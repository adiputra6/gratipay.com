from __future__ import print_function, unicode_literals

import json
import datetime
from decimal import Decimal

import pytz
from gittip.testing import Harness
from gittip.testing.client import TestClient


class Tests(Harness):

    def make_participant(self, *a, **kw):
        kw['claimed_time'] = datetime.datetime.now(pytz.utc)
        return Harness.make_participant(self, *a, **kw)

    def test_anonymous_gets_receiving(self):
        alice = self.make_participant('alice', last_bill_result='')
        self.make_participant('bob')

        alice.set_tip_to('bob', '1.00')

        data = json.loads(TestClient().get('/bob/public.json').body)

        self.assertEquals(data['receiving'], '1.00')

    def test_anonymous_does_not_get_my_tip(self):
        alice = self.make_participant('alice', last_bill_result='')
        self.make_participant('bob')

        alice.set_tip_to('bob', '1.00')

        data = json.loads(TestClient().get('/bob/public.json').body)

        self.assertEquals(data.has_key('my_tip'), False)

    def test_anonymous_gets_giving(self):
        alice = self.make_participant('alice', last_bill_result='')
        self.make_participant('bob')

        alice.set_tip_to('bob', '1.00')

        data = json.loads(TestClient().get('/alice/public.json').body)

        self.assertEquals(data['giving'], '1.00')

    def test_anonymous_gets_null_giving_if_user_anonymous(self):
        alice = self.make_participant( 'alice'
                                     , last_bill_result=''
                                     , anonymous=True
                                      )
        self.make_participant('bob')
        alice.set_tip_to('bob', '1.00')
        data = json.loads(TestClient().get('/alice/public.json').body)

        self.assertEquals(data['giving'], None)

    def test_anonymous_does_not_get_goal_if_user_regifts(self):
        self.make_participant('alice', last_bill_result='', goal=0)
        data = json.loads(TestClient().get('/alice/public.json').body)
        self.assertEquals(data.has_key('goal'), False)

    def test_anonymous_gets_null_goal_if_user_has_no_goal(self):
        self.make_participant('alice', last_bill_result='')
        data = json.loads(TestClient().get('/alice/public.json').body)
        self.assertEquals(data['goal'], None)

    def test_anonymous_gets_user_goal_if_set(self):
        self.make_participant('alice', last_bill_result='', goal=1)
        data = json.loads(TestClient().get('/alice/public.json').body)
        self.assertEquals(data['goal'], '1.00')

    def test_authenticated_user_gets_their_tip(self):
        alice = self.make_participant('alice', last_bill_result='')
        self.make_participant('bob')

        alice.set_tip_to('bob', '1.00')

        raw = TestClient().get('/bob/public.json', user='alice').body

        data = json.loads(raw)

        self.assertEquals(data['receiving'], '1.00')
        self.assertEquals(data['my_tip'], '1.00')

    def test_authenticated_user_doesnt_get_other_peoples_tips(self):
        alice = self.make_participant('alice', last_bill_result='')
        bob = self.make_participant('bob', last_bill_result='')
        carl = self.make_participant('carl', last_bill_result='')
        self.make_participant('dana')

        alice.set_tip_to('dana', '1.00')
        bob.set_tip_to('dana', '3.00')
        carl.set_tip_to('dana', '12.00')

        raw = TestClient().get('/dana/public.json', user='alice').body

        data = json.loads(raw)

        self.assertEquals(data['receiving'], '16.00')
        self.assertEquals(data['my_tip'], '1.00')

    def test_authenticated_user_gets_zero_if_they_dont_tip(self):
        self.make_participant('alice', last_bill_result='')
        bob = self.make_participant('bob', last_bill_result='')
        self.make_participant('carl')

        bob.set_tip_to('carl', '3.00')

        raw = TestClient().get('/carl/public.json', user='alice').body

        data = json.loads(raw)

        self.assertEquals(data['receiving'], '3.00')
        self.assertEquals(data['my_tip'], '0.00')

    def test_authenticated_user_gets_self_for_self(self):
        alice = self.make_participant('alice', last_bill_result='')
        self.make_participant('bob')

        alice.set_tip_to('bob', '3.00')

        raw = TestClient().get('/bob/public.json', user='bob').body

        data = json.loads(raw)

        self.assertEquals(data['receiving'], '3.00')
        self.assertEquals(data['my_tip'], 'self')
