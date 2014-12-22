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
        app.board.init()
        rv = self.app.get('/v1/board/')
        assert json.loads(rv.data) == {'size': [1000, 1000], 'robots': [], 'missiles': [], 'explosions': []}

    def test_new_robot(self):
        app.board.init()
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
        print robot
        assert robot['name'] == 'GUNDAM2'


if __name__ == '__main__':
    unittest.main()