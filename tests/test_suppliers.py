import unittest
from unittest.mock import MagicMock, patch
from table_module import SupplierTable


class TestSupplierTable(unittest.TestCase):
    def setUp(self):
        # Патчим методы класса SupplierTable
        self.patcher_save = patch('table_module.SupplierTable.save', new=MagicMock())
        self.patcher_get_by_id = patch('table_module.SupplierTable.get_by_id', new=MagicMock())
        self.patcher_get_all = patch('table_module.SupplierTable.get_all', new=MagicMock())
        self.patcher_delete = patch('table_module.SupplierTable.delete', new=MagicMock())

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

    def test_save_valid_supplier(self):
        name = "Test Supplier"
        contact_info = "test@example.com"
        type_of_materials = "Construction"
        address = "123 Test Street"
        SupplierTable.save(name=name, contact_info=contact_info, type_of_materials=type_of_materials, address=address)
        self.mock_save.assert_called_once_with(
            name=name, contact_info=contact_info, type_of_materials=type_of_materials, address=address
        )

    def test_save_invalid_supplier(self):
        name = ""  # Пустое имя
        contact_info = "test@example.com"
        type_of_materials = "Construction"
        address = "123 Test Street"
        self.mock_save.side_effect = ValueError("Invalid data")
        with self.assertRaises(ValueError):
            SupplierTable.save(name=name, contact_info=contact_info, type_of_materials=type_of_materials, address=address)

    def test_get_by_id_valid(self):
        supplier_id = 1
        mock_supplier = {"id": supplier_id, "name": "Test Supplier"}
        self.mock_get_by_id.return_value = mock_supplier
        result = SupplierTable.get_by_id(supplier_id)
        self.mock_get_by_id.assert_called_once_with(supplier_id)
        self.assertEqual(result, mock_supplier)

    def test_get_all(self):
        mock_suppliers = [{"id": 1, "name": "Test Supplier"}]
        self.mock_get_all.return_value = mock_suppliers
        result = SupplierTable.get_all()
        self.mock_get_all.assert_called_once()
        self.assertEqual(result, mock_suppliers)

    def test_delete_valid(self):
        supplier_id = 1
        SupplierTable.delete(supplier_id)
        self.mock_delete.assert_called_once_with(supplier_id)


if __name__ == "__main__":
    unittest.main()
