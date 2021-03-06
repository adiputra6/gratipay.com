from __future__ import print_function, unicode_literals

import json

from aspen.utils import utcnow
from gratipay.testing import Harness


class TestTipsJson(Harness):

    def also_prune_variant(self, also_prune, tippees=1):

        now = utcnow()
        self.make_participant("test_tippee1", claimed_time=now)
        self.make_participant("test_tippee2", claimed_time=now)
        self.make_participant("test_tipper", claimed_time=now)

        data = [
            {'username': 'test_tippee1', 'platform': 'gratipay', 'amount': '1.00'},
            {'username': 'test_tippee2', 'platform': 'gratipay', 'amount': '2.00'}
        ]

        response = self.client.POST( '/test_tipper/tips.json'
                                   , body=json.dumps(data)
                                   , content_type='application/json'
                                   , auth_as='test_tipper'
                                    )

        assert response.code == 200
        assert len(json.loads(response.body)) == 2

        response = self.client.POST( '/test_tipper/tips.json?also_prune=' + also_prune
                                   , body=json.dumps([{ 'username': 'test_tippee2'
                                                      , 'platform': 'gratipay'
                                                      , 'amount': '1.00'
                                                       }])
                                   , content_type='application/json'
                                   , auth_as='test_tipper'
                                    )

        assert response.code == 200

        response = self.client.GET('/test_tipper/tips.json', auth_as='test_tipper')
        assert response.code == 200
        assert len(json.loads(response.body)) == tippees

    def test_get_response(self):
        now = utcnow()
        self.make_participant("test_tipper", claimed_time=now)

        response = self.client.GET('/test_tipper/tips.json', auth_as='test_tipper')

        assert response.code == 200
        assert len(json.loads(response.body)) == 0 # empty array

    def test_get_response_with_tips(self):
        now = utcnow()
        self.make_participant("test_tippee1", claimed_time=now)
        self.make_participant("test_tipper", claimed_time=now)

        response = self.client.POST( '/test_tippee1/tip.json'
                                   , {'amount': '1.00'}
                                   , auth_as='test_tipper'
                                    )

        assert response.code == 200
        assert json.loads(response.body)['amount'] == '1.00'

        response = self.client.GET('/test_tipper/tips.json', auth_as='test_tipper')
        data = json.loads(response.body)[0]

        assert response.code == 200
        assert data['username'] == 'test_tippee1'
        assert data['amount'] == '1.00'

    def test_post_bad_platform(self):
        now = utcnow()
        self.make_participant("test_tippee1", claimed_time=now)
        self.make_participant("test_tipper", claimed_time=now)

        response = self.client.POST( '/test_tipper/tips.json'
                                   , body=json.dumps([{ 'username': 'test_tippee1'
                                                 , 'platform': 'badname'
                                                 , 'amount': '1.00'
                                                  }])
                                   , auth_as='test_tipper'
                                   , content_type='application/json'
                                    )

        assert response.code == 200

        resp = json.loads(response.body)

        for tip in resp:
            assert 'error' in tip

    def test_gittip_as_platform_works(self):
        now = utcnow()
        self.make_participant("test_tippee1", claimed_time=now)
        self.make_participant("test_tipper", claimed_time=now)

        response = self.client.POST( '/test_tipper/tips.json'
                                   , body=json.dumps([{ 'username': 'test_tippee1'
                                                      , 'platform': 'gittip'
                                                      , 'amount': '1.00'
                                                       }])
                                   , auth_as='test_tipper'
                                   , content_type='application/json'
                                    )

        assert response.code == 200

        resp = json.loads(response.body)
        assert len(resp) == 1
        tip = resp[0]
        assert tip['platform'] == 'gittip'

    def test_also_prune_as_1(self):
        self.also_prune_variant('1')

    def test_also_prune_as_true(self):
        self.also_prune_variant('true')

    def test_also_prune_as_yes(self):
        self.also_prune_variant('yes')

    def test_also_prune_as_0(self):
        self.also_prune_variant('0', 2)
