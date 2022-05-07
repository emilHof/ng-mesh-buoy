import unittest

from mesh_handler import MeshHandler


class TestMeshHandler(unittest.TestCase):
    def test_make_path(self):
        graph = {
            "00": {"01": 1, "02": 3, "03": 4, "04": 8},
            "01": {"00": 1, "02": 2.5, "03": 3.5, "04": 7.5},
            "02": {"00": 3, "01": 2.5, "03": 6.7, "04": 4.6},
            "03": {"00": 4, "01": 3.5, "02": 6.7, "04": 13},
            "04": {"00": 8, "01": 7.5, "02": 5.6, "03": 13},
        }
        target = "04"
        expected = ["00", "02", "04"]

        mesh_handler = MeshHandler("00")
        mesh_handler.connection_graph(graph)

        actual = mesh_handler.find_path(target)

        self.assertEqual(actual, expected)
