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
        self.assertEqual(json.loads(rv.data), {'size': [1000, 1000], 'robots': [], 'missiles': {}, 'explosions': {},
                                       'radar': {}, 'kdr': {}})

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
        self.assertEqual(robot, {u'name': u'GUNDAM2', u'hp': 100, u'winner': False, u'dead': False, u'max_speed': 27,
                                 u'y': 500, u'x': 250, u'speed': 0, u'heading': 0, u'reloading': False})

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
        assert robot == {u'name': u'GUNDAM3', u'hp': 100, u'winner': False, u'dead': False, u'max_speed': 27,
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
        token1 = data['token']

        rv = self.app.post('/v1/robot/', data=dict(
            name='GUNDAM2'
        ))
        data = json.loads(rv.data)
        token2 = data['token']

        rv = self.app.post('/v1/robot/', data=dict(
            name='GUNDAM3'
        ))
        data = json.loads(rv.data)
        token3 = data['token']

        rv = self.app.post('/v1/robot/', data=dict(
            name='GUNDAM4'
        ))
        data = json.loads(rv.data)
        token4 = data['token']

        rv = self.app.put('/v1/robot/' + token1 + '/scan', data=dict(
            degree=315,
            resolution=10
        ))
        assert rv.status_code == 200
        data = json.loads(rv.data)
        assert 'status' in data
        assert data['status'] == 'OK'
        assert 'distance' in data
        assert int(data['distance']) == 353

        rv = self.app.put('/v1/robot/' + token1 + '/scan', data=dict(
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

    def test_cannon_2(self):
        app.app.game_board.reinit()
        rv = self.app.post('/v1/robot/', data=dict(
            name='GUNDAM1'
        ))
        token1 = json.loads(rv.data)['token']

        rv = self.app.post('/v1/robot/', data=dict(
            name='GUNDAM2'
        ))
        token2 = json.loads(rv.data)['token']

        rv = self.app.post('/v1/robot/', data=dict(
            name='GUNDAM3'
        ))
        token3 = json.loads(rv.data)['token']

        rv = self.app.post('/v1/robot/', data=dict(
            name='GUNDAM4'
        ))
        token4 = json.loads(rv.data)['token']

        rv = self.app.put('/v1/robot/' + token1 + '/cannon', data=dict(
            degree=0,
            distance=500
        ))

    def test_get_board(self):
        app.app.game_board.reinit()
        rv = self.app.post('/v1/robot/', data=dict(
            name='GUNDAM1'
        ))

        rv = self.app.get('/v1/board/')
        data = json.loads(rv.data)
        self.assertEqual(data, {u'radar': {}, u'missiles': {}, u'robots': [
            {u'name': u'GUNDAM1', u'hp': 100, u'winner': False, u'dead': False, u'reloading': False, u'max_speed': 27,
             u'y': 500, u'x': 250, u'speed': 0, u'heading': 0}], u'explosions': {}, u'size': [1000, 1000], u'kdr':{}})

    def test_delete_robot(self):
        app.app.game_board.reinit()
        rv = self.app.post('/v1/robot/', data=dict(
            name='GUNDAM'
        ))

        data = json.loads(rv.data)
        token = data['token']
        self.assertEqual(data['status'],'OK')

        rv = self.app.delete('/v1/robot/'+token)

        data = json.loads(rv.data)
        self.assertEqual(data['status'],'OK')
        self.assertEqual(data['name'],'GUNDAM')

        rv = self.app.post('/v1/robot/', data=dict(
            name='GUNDAM'
        ))

        data = json.loads(rv.data)
        self.assertEqual(data['status'],'OK')

if __name__ == '__main__':
    unittest.main()