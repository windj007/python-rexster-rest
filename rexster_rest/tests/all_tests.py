import unittest
from rexster_rest import RexsterClient


class TestClient(unittest.TestCase):
    def setUp(self):
        self.client = RexsterClient('http://localhost:8182', 'graph')

    def test_add_vertex(self):
        init_cnt = len(self.client.vertices().get())
        v = self.client.create_vertex(a = 123,  b = 'qwe').get()
        print repr(v)
        vs = self.client.vertices().get()
        print repr(vs)
        self.assertEqual(len(vs) - init_cnt, 1)
        self.client.delete_vertex(v['_id']).get()
        self.assertEqual(len(self.client.vertices().get()), init_cnt)


if __name__ == '__main__':
    unittest.main()
