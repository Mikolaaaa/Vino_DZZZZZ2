import unittest
from unittest.mock import MagicMock, patch
from table_module import MaterialTable


class TestMaterialTable(unittest.TestCase):
    def setUp(self):
        # Патчим методы класса MaterialTable
        self.patcher_save = patch('table_module.MaterialTable.save', new=MagicMock())
        self.patcher_get_by_id = patch('table_module.MaterialTable.get_by_id', new=MagicMock())
        self.patcher_get_all = patch('table_module.MaterialTable.get_all', new=MagicMock())
        self.patcher_delete = patch('table_module.MaterialTable.delete', new=MagicMock())

        # Начинаем патчинг
        self.mock_save = self.patcher_save.start()
        self.mock_get_by_id = self.patcher_get_by_id.start()
        self.mock_get_all = self.patcher_get_all.start()
        self.mock_delete = self.patcher_delete.start()

    def tearDown(self):
        # Останавливаем патчинг
        self.patcher_save.stop()
        self.patcher_get_by_id.stop()
        self.patcher_get_all.stop()
        self.patcher_delete.stop()

    def test_save_valid_material(self):
        name = "Test Material"
        quantity = 100
        price = 50.0
        manufacturer = "Test Manufacturer"
        supplier_id = 1
        MaterialTable.save(name, quantity, price, manufacturer, supplier_id)
        self.mock_save.assert_called_once_with(name, quantity, price, manufacturer, supplier_id)

    def test_save_invalid_material(self):
        name = ""  # Пустое имя
        quantity = 100
        price = 50.0
        manufacturer = "Test Manufacturer"
        supplier_id = 1
        self.mock_save.side_effect = ValueError("Invalid data")
        with self.assertRaises(ValueError):
            MaterialTable.save(name, quantity, price, manufacturer, supplier_id)

    def test_get_by_id_valid(self):
        material_id = 1
        mock_material = {"id": material_id, "name": "Test Material"}
        self.mock_get_by_id.return_value = mock_material
        result = MaterialTable.get_by_id(material_id)
        self.mock_get_by_id.assert_called_once_with(material_id)
        self.assertEqual(result, mock_material)

    def test_get_all(self):
        mock_materials = [{"id": 1, "name": "Test Material"}]
        self.mock_get_all.return_value = mock_materials
        result = MaterialTable.get_all()
        self.mock_get_all.assert_called_once()
        self.assertEqual(result, mock_materials)

    def test_delete_valid(self):
        material_id = 1
        MaterialTable.delete(material_id)
        self.mock_delete.assert_called_once_with(material_id)


if __name__ == "__main__":
    unittest.main()
