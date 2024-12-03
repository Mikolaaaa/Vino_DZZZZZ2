import unittest
from unittest.mock import MagicMock, patch
from table_module import WorkforceTable


class TestWorkforceTable(unittest.TestCase):
    def setUp(self):
        self.patcher_save = patch('table_module.WorkforceTable.save', new=MagicMock())
        self.patcher_get_all = patch('table_module.WorkforceTable.get_all', new=MagicMock())
        self.patcher_delete = patch('table_module.WorkforceTable.delete', new=MagicMock())

        self.mock_save = self.patcher_save.start()
        self.mock_get_all = self.patcher_get_all.start()

    def tearDown(self):
        self.patcher_save.stop()
        self.patcher_get_all.stop()
        self.patcher_delete.stop()

    def test_save_valid_workforce(self):
        name = "John Doe"
        role = "Engineer"
        workers = 12
        start_date = "2024-12-31"
        end_date = "2025-12-31"
        WorkforceTable.save(name, role, workers, start_date, end_date)
        self.mock_save.assert_called_once_with(name, role, workers, start_date, end_date)


if __name__ == "__main__":
    unittest.main()
