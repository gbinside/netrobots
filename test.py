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


if __name__ == '__main__':
    unittest.main()