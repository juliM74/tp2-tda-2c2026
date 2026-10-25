import unittest

from tp2_2 import main, actualizar_servidor
from tp2_1 import main as edificios

class TestFestivalParteA(unittest.TestCase):
    def test_ejemplo_del_enunciado_factible(self):
        bandas = [("B1", 6), ("B2", 4)]
        servidores = [("S1", 5), ("S2", 6)]
        plataformas = [("P1", 5), ("P2", 5)]
        bs = [("B1", "S1"), ("B1", "S2"), ("B2", "S2")]
        sp = [("S1", "P1"), ("S2", "P1"), ("S2", "P2")]

        posible, flujo_max, asignacion = main(bandas, servidores, plataformas, bs, sp)

        self.assertTrue(posible)
        self.assertEqual(flujo_max, 10)


class TestFestivalParteB(unittest.TestCase):
    def test_disminuir_servidor_vuelve_infactible(self):
        bandas = [("B1", 6), ("B2", 4)]
        servidores = [("S1", 5), ("S2", 6)]
        plataformas = [("P1", 5), ("P2", 5)]
        bs = [("B1", "S1"), ("B1", "S2"), ("B2", "S2")]
        sp = [("S1", "P1"), ("S2", "P1"), ("S2", "P2")]

        posible, flujo_max, _ = main(bandas, servidores, plataformas, bs, sp)
        self.assertTrue(posible)
        self.assertEqual(flujo_max, 10)

        posible2, flujo_max2, _ = actualizar_servidor("S2", 4)

        self.assertFalse(posible2)
        self.assertEqual(flujo_max2, 9)


class TestEdificios(unittest.TestCase):
    def test_un_edificio_visible(self):
        self.assertEqual(edificios(1, 1), 1)

    def test_tres_edificios_dos_visibles(self):
        # [1, 3, 2], [2, 1, 3], [2, 3, 1]
        self.assertEqual(edificios(3, 2), 3)

    def test_todos_visibles_solo_orden_creciente(self):
        self.assertEqual(edificios(5, 5), 1)
        self.assertEqual(edificios(10, 10), 1)


if __name__ == "__main__":
    unittest.main()
