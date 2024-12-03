import unittest
from unittest.mock import MagicMock, patch
from table_module import ConstructionObjectTable


class TestConstructionObjectTable(unittest.TestCase):
    def setUp(self):
        # Патчим методы класса ConstructionObjectTable
        self.patcher_save = patch('table_module.ConstructionObjectTable.save', new=MagicMock())
        self.patcher_get_by_id = patch('table_module.ConstructionObjectTable.get_by_id', new=MagicMock())
        self.patcher_get_all = patch('table_module.ConstructionObjectTable.get_all', new=MagicMock())
        self.patcher_delete = patch('table_module.ConstructionObjectTable.delete', new=MagicMock())

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

    def test_save_valid_data(self):
        name = "Test Object"
        address = "123 Test Street"
        deadline = "2024-12-31"
        ConstructionObjectTable.save(name, address, deadline)
        self.mock_save.assert_called_once_with(name, address, deadline)

    def test_save_invalid_data(self):
        name = ""  # Пустое имя
        address = "123 Test Street"
        deadline = "2024-12-31"
        self.mock_save.side_effect = ValueError("Invalid data")
        with self.assertRaises(ValueError):
            ConstructionObjectTable.save(name, address, deadline)

    def test_get_by_id_valid(self):
        object_id = 1
        mock_object = {"id": object_id, "name": "Test Object"}
        self.mock_get_by_id.return_value = mock_object
        result = ConstructionObjectTable.get_by_id(object_id)
        self.mock_get_by_id.assert_called_once_with(object_id)
        self.assertEqual(result, mock_object)

    def test_get_all(self):
        mock_objects = [{"id": 1, "name": "Test Object"}]
        self.mock_get_all.return_value = mock_objects
        result = ConstructionObjectTable.get_all()
        self.mock_get_all.assert_called_once()
        self.assertEqual(result, mock_objects)

    def test_delete_valid(self):
        object_id = 1
        ConstructionObjectTable.delete(object_id)
        self.mock_delete.assert_called_once_with(object_id)


if __name__ == "__main__":
    unittest.main()
