import unittest
from unittest.mock import MagicMock, patch
from table_module import PurchaseRequestTable


class TestPurchaseRequestTable(unittest.TestCase):
    def setUp(self):
        self.patcher_save = patch('table_module.PurchaseRequestTable.save', new=MagicMock())
        self.patcher_get_by_id = patch('table_module.PurchaseRequestTable.get_by_id', new=MagicMock())
        self.patcher_delete = patch('table_module.PurchaseRequestTable.delete', new=MagicMock())

        self.mock_save = self.patcher_save.start()
        self.mock_get_by_id = self.patcher_get_by_id.start()
        self.mock_delete = self.patcher_delete.start()

    def tearDown(self):
        self.patcher_save.stop()
        self.patcher_get_by_id.stop()
        self.patcher_delete.stop()

    def test_save_valid_request(self):
        item = "Steel Beams"
        quantity = 20
        price = 123
        supplier_id = 1
        status = "Ожидает"
        request_date = "2024-12-31"
        PurchaseRequestTable.save(item, quantity, price, supplier_id, status, request_date)
        self.mock_save.assert_called_once_with(item, quantity, price, supplier_id, status, request_date)

    def test_get_by_id_valid(self):
        request_id = 1
        mock_request = {"id": request_id, "item": "Steel Beams"}
        self.mock_get_by_id.return_value = mock_request
        result = PurchaseRequestTable.get_by_id(request_id)
        self.mock_get_by_id.assert_called_once_with(request_id)
        self.assertEqual(result, mock_request)


if __name__ == "__main__":
    unittest.main()
