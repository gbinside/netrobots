import unittest
import json
import app


class AppTestCase(unittest.TestCase):
    def setUp(self):
        app.app.config['TESTING'] = True
        self.app = app.app.test_client()

    def tearDown(self):
        pass

    def test_empty_board(self):
        app.app.game_board.reinit()
        rv = self.app.get('/v1/board/')
        assert json.loads(rv.data) == {'size': [1000, 1000], 'robots': {}, 'missiles': [], 'explosions': []}

    def test_new_robot(self):
        app.app.game_board.reinit()
        rv = self.app.post('/v1/robot/', data=dict(
            name='GUNDAM'
        ))
        data = json.loads(rv.data)
        assert 'status' in data
        assert data['status'] == 'OK'
        assert 'token' in data
        rv = self.app.post('/v1/robot/', data=dict(
            name='GUNDAM'
        ))
        data = json.loads(rv.data)
        assert 'status' in data
        assert data['status'] == 'KO'
        assert 'token' not in data

    def test_robot_status(self):
        app.app.game_board.reinit()
        rv = self.app.post('/v1/robot/', data=dict(
            name='GUNDAM2'
        ))
        data = json.loads(rv.data)
        token = data['token']
        rv = self.app.get('/v1/robot/' + token)
        data = json.loads(rv.data)
        assert 'status' in data
        assert data['status'] == 'OK'
        assert 'robot' in data
        robot = data['robot']
        assert robot == {u'name': u'GUNDAM2', u'hp': 100, u'winner': False, u'dead': False, u'max_speed': 100,
                         u'y': 500, u'x': 250, u'speed': 0, u'heading': 0, u'reloading': False}

        rv = self.app.post('/v1/robot/', data=dict(
            name='GUNDAM3'
        ))
        data = json.loads(rv.data)
        token = data['token']
        rv = self.app.get('/v1/robot/' + token)
        data = json.loads(rv.data)
        assert 'status' in data
        assert data['status'] == 'OK'
        assert 'robot' in data
        robot = data['robot']
        assert robot == {u'name': u'GUNDAM3', u'hp': 100, u'winner': False, u'dead': False, u'max_speed': 100,
                         u'y': 500, u'x': 750, u'speed': 0, u'heading': 180, u'reloading': False}

    def test_drive(self):
        app.app.game_board.reinit()
        rv = self.app.post('/v1/robot/', data=dict(
            name='GUNDAM2'
        ))
        data = json.loads(rv.data)
        token = data['token']
        rv = self.app.put('/v1/robot/' + token + '/drive', data=dict(
            speed=50,
            degree=90
        ))
        assert rv.status_code == 200
        data = json.loads(rv.data)
        assert 'status' in data
        assert data['status'] == 'OK'
        assert 'robot' in data
        assert data['done']

        rv = self.app.put('/v1/robot/' + token + '/drive', data=dict(
            speed=50,
            degree=90
        ))
        assert rv.status_code == 406
        data = json.loads(rv.data)
        assert 'status' in data
        assert data['status'] == 'KO'
        assert 'robot' in data
        assert not data['done']

    def test_scan(self):
        app.app.game_board.reinit()
        rv = self.app.post('/v1/robot/', data=dict(
            name='GUNDAM2'
        ))
        data = json.loads(rv.data)
        token = data['token']
        rv = self.app.put('/v1/robot/' + token + '/scan', data=dict(
            degree=90,
            resolution=90
        ))
        assert rv.status_code == 200
        data = json.loads(rv.data)
        assert 'status' in data
        assert data['status'] == 'OK'
        assert 'distance' in data
        assert data['distance'] == 0

        rv = self.app.put('/v1/robot/' + token + '/scan', data=dict(
            degree=90,
            resolution=90
        ))
        assert rv.status_code == 406
        data = json.loads(rv.data)
        assert 'status' in data
        assert data['status'] == 'KO'
        assert 'distance' in data

    def test_cannon(self):
        app.app.game_board.reinit()
        rv = self.app.post('/v1/robot/', data=dict(
            name='GUNDAM2'
        ))
        data = json.loads(rv.data)
        token = data['token']
        rv = self.app.put('/v1/robot/' + token + '/cannon', data=dict(
            degree=50,
            distance=100
        ))
        assert rv.status_code == 200
        data = json.loads(rv.data)
        assert 'status' in data
        assert data['status'] == 'OK'
        assert 'robot' in data
        assert data['done']
        assert data['robot']['reloading']

        rv = self.app.put('/v1/robot/' + token + '/cannon', data=dict(
            degree=50,
            distance=100
        ))
        assert rv.status_code == 406
        data = json.loads(rv.data)
        assert 'status' in data
        assert data['status'] == 'KO'
        assert 'robot' in data
        assert not data['done']

    def test_scan_2(self):
        app.app.game_board.reinit()
        rv = self.app.post('/v1/robot/', data=dict(
            name='GUNDAM1'
        ))
        data = json.loads(rv.data)
        token = data['token']

        rv = self.app.post('/v1/robot/', data=dict(
            name='GUNDAM2'
        ))

        rv = self.app.put('/v1/robot/' + token + '/scan', data=dict(
            degree=0,
            resolution=10
        ))
        assert rv.status_code == 200
        data = json.loads(rv.data)
        assert 'status' in data
        assert data['status'] == 'OK'
        assert 'distance' in data
        assert data['distance'] == 500

    def test_scan_3(self):
        app.app.game_board.reinit()
        rv = self.app.post('/v1/robot/', data=dict(
            name='GUNDAM1'
        ))
        data = json.loads(rv.data)
        token = data['token']

        self.app.post('/v1/robot/', data=dict(
            name='GUNDAM2'
        ))

        self.app.post('/v1/robot/', data=dict(
            name='GUNDAM3'
        ))

        self.app.post('/v1/robot/', data=dict(
            name='GUNDAM4'
        ))

        rv = self.app.put('/v1/robot/' + token + '/scan', data=dict(
            degree=315,
            resolution=10
        ))
        assert rv.status_code == 200
        data = json.loads(rv.data)
        assert 'status' in data
        assert data['status'] == 'OK'
        assert 'distance' in data
        assert int(data['distance']) == 353

        rv = self.app.put('/v1/robot/' + token + '/endturn')
        assert rv.status_code == 200

        rv = self.app.put('/v1/robot/' + token + '/scan', data=dict(
            degree=45,
            resolution=10
        ))
        assert rv.status_code == 200
        data = json.loads(rv.data)
        assert 'status' in data
        assert data['status'] == 'OK'
        assert 'distance' in data
        assert int(data['distance']) == 353

    def test_drive_2(self):
        app.app.game_board.reinit()
        rv = self.app.post('/v1/robot/', data=dict(
            name='GUNDAM'
        ))
        data = json.loads(rv.data)
        token = data['token']
        rv = self.app.put('/v1/robot/' + token + '/drive', data=dict(
            speed=50,
            degree=30
        ))
        assert rv.status_code == 200
        data = json.loads(rv.data)
        assert 'status' in data
        assert data['status'] == 'OK'
        assert 'robot' in data
        assert data['done']

        rv = self.app.put('/v1/robot/' + token + '/endturn')
        assert rv.status_code == 200

        rv = self.app.get('/v1/robot/' + token)
        assert rv.status_code == 200
        data = json.loads(rv.data)
        assert 'status' in data
        assert data['status'] == 'OK'
        assert int(data['robot']['x']) == 284
        assert int(data['robot']['y']) == 520

        rv = self.app.put('/v1/robot/' + token + '/endturn')
        assert rv.status_code == 200

        rv = self.app.get('/v1/robot/' + token)
        assert rv.status_code == 200
        data = json.loads(rv.data)
        assert 'status' in data
        assert data['status'] == 'OK'
        assert int(data['robot']['x']) == 327
        assert int(data['robot']['y']) == 545

    def test_drive_3(self):
        app.app.game_board.reinit()
        rv = self.app.post('/v1/robot/', data=dict(
            name='GUNDAM'
        ))
        data = json.loads(rv.data)
        token = data['token']
        rv = self.app.put('/v1/robot/' + token + '/drive', data=dict(
            speed=100,
            degree=0
        ))
        assert rv.status_code == 200
        data = json.loads(rv.data)
        assert 'status' in data
        assert data['status'] == 'OK'
        assert 'robot' in data
        assert data['done']

        rv = self.app.put('/v1/robot/' + token + '/endturn')
        assert rv.status_code == 200

        rv = self.app.get('/v1/robot/' + token)
        assert rv.status_code == 200
        data = json.loads(rv.data)
        assert 'status' in data
        assert data['status'] == 'OK'
        assert int(data['robot']['x']) == 290
        assert int(data['robot']['y']) == 500

        rv = self.app.put('/v1/robot/' + token + '/endturn')
        assert rv.status_code == 200

        rv = self.app.get('/v1/robot/' + token)
        assert rv.status_code == 200
        data = json.loads(rv.data)
        assert 'status' in data
        assert data['status'] == 'OK'
        assert int(data['robot']['x']) == 370
        assert int(data['robot']['y']) == 500

        rv = self.app.put('/v1/robot/' + token + '/endturn')
        assert rv.status_code == 200

        rv = self.app.get('/v1/robot/' + token)
        assert rv.status_code == 200
        data = json.loads(rv.data)
        assert 'status' in data
        assert data['status'] == 'OK'
        assert int(data['robot']['x']) == 470
        assert int(data['robot']['y']) == 500

    def test_drive_4_collision_with_border(self):
        app.app.game_board.reinit()
        rv = self.app.post('/v1/robot/', data=dict(
            name='GUNDAM'
        ))
        data = json.loads(rv.data)
        token = data['token']
        rv = self.app.put('/v1/robot/' + token + '/drive', data=dict(
            speed=100,
            degree=180
        ))

        self.app.put('/v1/robot/' + token + '/endturn')
        rv = self.app.get('/v1/robot/' + token)
        data = json.loads(rv.data)
        assert int(data['robot']['x']) == 210
        assert int(data['robot']['y']) == 500

        self.app.put('/v1/robot/' + token + '/endturn')
        rv = self.app.get('/v1/robot/' + token)
        data = json.loads(rv.data)
        assert int(data['robot']['x']) == 130
        assert int(data['robot']['y']) == 500

        self.app.put('/v1/robot/' + token + '/endturn')
        rv = self.app.get('/v1/robot/' + token)
        data = json.loads(rv.data)
        assert int(data['robot']['x']) == 30
        assert int(data['robot']['y']) == 500

        self.app.put('/v1/robot/' + token + '/endturn')
        rv = self.app.get('/v1/robot/' + token)
        data = json.loads(rv.data)
        assert int(data['robot']['x']) == 0
        assert int(data['robot']['y']) == 500
        assert int(data['robot']['speed']) == 0
        assert int(data['robot']['hp']) == 98

    def test_drive_5_collision_with_border(self):
        app.app.game_board.reinit()
        rv = self.app.post('/v1/robot/', data=dict(
            name='GUNDAM'
        ))
        data = json.loads(rv.data)
        token = data['token']
        rv = self.app.put('/v1/robot/' + token + '/drive', data=dict(
            speed=100,
            degree=210
        ))

        self.app.put('/v1/robot/' + token + '/endturn')
        rv = self.app.get('/v1/robot/' + token)
        data = json.loads(rv.data)
        assert int(data['robot']['x']) == 215
        assert int(data['robot']['y']) == 480

        self.app.put('/v1/robot/' + token + '/endturn')
        rv = self.app.get('/v1/robot/' + token)
        data = json.loads(rv.data)
        assert int(data['robot']['x']) == 146
        assert int(data['robot']['y']) == 440

        self.app.put('/v1/robot/' + token + '/endturn')
        rv = self.app.get('/v1/robot/' + token)
        data = json.loads(rv.data)
        assert int(data['robot']['x']) == 59
        assert int(data['robot']['y']) == 390

        self.app.put('/v1/robot/' + token + '/endturn')
        rv = self.app.get('/v1/robot/' + token)
        data = json.loads(rv.data)
        assert int(data['robot']['x']) == 0
        assert int(data['robot']['y']) == 355
        assert int(data['robot']['speed']) == 0
        assert int(data['robot']['hp']) == 98

    def test_drive_6_collision_with_border(self):
        app.app.game_board.reinit()
        rv = self.app.post('/v1/robot/', data=dict(
            name='GUNDAM'
        ))
        data = json.loads(rv.data)
        token = data['token']
        self.app.put('/v1/robot/' + token + '/drive', data=dict(
            speed=100,
            degree=30
        ))

        rv = self.app.get('/v1/robot/' + token)
        data = json.loads(rv.data)
        while int(data['robot']['hp']) == 100:
            self.app.put('/v1/robot/' + token + '/endturn')
            rv = self.app.get('/v1/robot/' + token)
            data = json.loads(rv.data)
        assert int(data['robot']['x']) == 1000
        assert int(data['robot']['y']) == 933
        assert int(data['robot']['speed']) == 0
        assert int(data['robot']['hp']) == 98

        self.app.put('/v1/robot/' + token + '/drive', data=dict(
            speed=100,
            degree=135
        ))
        while int(data['robot']['hp']) == 98:
            self.app.put('/v1/robot/' + token + '/endturn')
            rv = self.app.get('/v1/robot/' + token)
            data = json.loads(rv.data)
        assert int(data['robot']['x']) == 933
        assert int(data['robot']['y']) == 1000
        assert int(data['robot']['speed']) == 0
        assert int(data['robot']['hp']) == 96

        self.app.put('/v1/robot/' + token + '/drive', data=dict(
            speed=100,
            degree=240
        ))
        while int(data['robot']['hp']) == 96:
            self.app.put('/v1/robot/' + token + '/endturn')
            rv = self.app.get('/v1/robot/' + token)
            data = json.loads(rv.data)
        assert int(data['robot']['x']) == 355
        assert int(data['robot']['y']) == 0
        assert int(data['robot']['speed']) == 0
        assert int(data['robot']['hp']) == 94

    def test_drive_7_break(self):
        app.app.game_board.reinit()
        rv = self.app.post('/v1/robot/', data=dict(
            name='GUNDAM'
        ))
        data = json.loads(rv.data)
        token = data['token']
        rv = self.app.put('/v1/robot/' + token + '/drive', data=dict(
            speed=100,
            degree=0
        ))

        data = json.loads(rv.data)
        while int(data['robot']['speed']) < 100:
            rv = self.app.put('/v1/robot/' + token + '/endturn')
            data = json.loads(rv.data)

        assert int(data['robot']['speed']) == 100
        rv = self.app.put('/v1/robot/' + token + '/drive', data=dict(
            speed=0,
            degree=0
        ))
        assert rv.status_code == 200

        self.app.put('/v1/robot/' + token + '/endturn')
        rv = self.app.get('/v1/robot/' + token)
        data = json.loads(rv.data)
        assert int(data['robot']['speed']) == 70

        self.app.put('/v1/robot/' + token + '/endturn')
        rv = self.app.get('/v1/robot/' + token)
        data = json.loads(rv.data)
        assert int(data['robot']['speed']) == 40

        self.app.put('/v1/robot/' + token + '/endturn')
        rv = self.app.get('/v1/robot/' + token)
        data = json.loads(rv.data)
        assert int(data['robot']['speed']) == 10

        self.app.put('/v1/robot/' + token + '/endturn')
        rv = self.app.get('/v1/robot/' + token)
        data = json.loads(rv.data)
        assert int(data['robot']['speed']) == 0

    def test_cannon_2(self):
        app.app.game_board.reinit()
        rv = self.app.post('/v1/robot/', data=dict(
            name='GUNDAM1'
        ))
        token1 = json.loads(rv.data)['token']

        self.app.post('/v1/robot/', data=dict(
            name='GUNDAM2'
        ))
        token2 = json.loads(rv.data)['token']

        self.app.post('/v1/robot/', data=dict(
            name='GUNDAM3'
        ))
        token3 = json.loads(rv.data)['token']

        self.app.post('/v1/robot/', data=dict(
            name='GUNDAM4'
        ))
        token4 = json.loads(rv.data)['token']

        rv = self.app.put('/v1/robot/' + token1 + '/cannon', data=dict(
            degree=0,
            distance=500
        ))
        for token in (token1, token2, token3, token4):
            self.app.put('/v1/robot/' + token + '/endturn')
        for token in (token1, token2, token3, token4):
            self.app.put('/v1/robot/' + token + '/endturn')

        rv = self.app.get('/v1/robot/' + token2)
        data = json.loads(rv.data)
        assert int(data['robot']['hp']) == 90

        rv = self.app.put('/v1/robot/' + token1 + '/cannon', data=dict(
            degree=45,
            distance=340
        ))
        assert rv.status_code == 200
        for token in (token1, token2, token3, token4):
            self.app.put('/v1/robot/' + token + '/endturn')
        rv = self.app.get('/v1/robot/' + token3)
        data = json.loads(rv.data)
        assert int(data['robot']['hp']) == 95

        for token in (token1, token2, token3, token4):
            self.app.put('/v1/robot/' + token + '/endturn')

        rv = self.app.put('/v1/robot/' + token1 + '/cannon', data=dict(
            degree=315,
            distance=315
        ))
        assert rv.status_code == 200
        for token in (token1, token2, token3, token4):
            self.app.put('/v1/robot/' + token + '/endturn')
        rv = self.app.get('/v1/robot/' + token4)
        data = json.loads(rv.data)
        assert int(data['robot']['hp']) == 97




if __name__ == '__main__':
    unittest.main()