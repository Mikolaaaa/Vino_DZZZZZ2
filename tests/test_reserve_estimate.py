import unittest
from unittest.mock import MagicMock, patch
from table_module import ReserveEstimateTable


class TestReserveEstimateTable(unittest.TestCase):
    def setUp(self):
        self.patcher_save = patch('table_module.ReserveEstimateTable.save', new=MagicMock())
        self.patcher_get_by_id = patch('table_module.ReserveEstimateTable.get_by_id', new=MagicMock())
        self.patcher_get_all = patch('table_module.ReserveEstimateTable.get_all', new=MagicMock())
        self.patcher_delete = patch('table_module.ReserveEstimateTable.delete', new=MagicMock())

        self.mock_save = self.patcher_save.start()
        self.mock_get_by_id = self.patcher_get_by_id.start()
        self.mock_get_all = self.patcher_get_all.start()

    def tearDown(self):
        self.patcher_save.stop()
        self.patcher_get_by_id.stop()
        self.patcher_get_all.stop()
        self.patcher_delete.stop()

    def test_save_valid_reserve(self):
        name = "Test Reserve"
        quantity = 50
        price = 343
        construction_object_id = 1
        supplier_id = 1
        missing_material = 1
        missing_quantity = 1
        total_cost = 124000
        ReserveEstimateTable.save(
            name, quantity, price, construction_object_id, supplier_id, missing_material, missing_quantity, total_cost
        )
        self.mock_save.assert_called_once_with(
            name, quantity, price, construction_object_id, supplier_id, missing_material,
            missing_quantity, total_cost,
        )

    def test_get_by_id_valid(self):
        reserve_id = 1
        mock_reserve = {"id": reserve_id, "name": "Test Reserve"}
        self.mock_get_by_id.return_value = mock_reserve
        result = ReserveEstimateTable.get_by_id(reserve_id)
        self.mock_get_by_id.assert_called_once_with(reserve_id)
        self.assertEqual(result, mock_reserve)


if __name__ == "__main__":
    unittest.main()
