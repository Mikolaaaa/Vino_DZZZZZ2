import unittest
from unittest.mock import MagicMock, patch
from table_module import CommentTable


class TestCommentTable(unittest.TestCase):
    def setUp(self):
        self.patcher_save = patch('table_module.CommentTable.save', new=MagicMock())
        self.patcher_get_by_id = patch('table_module.CommentTable.get_by_id', new=MagicMock())
        self.patcher_delete = patch('table_module.CommentTable.delete', new=MagicMock())

        self.mock_save = self.patcher_save.start()
        self.mock_get_by_id = self.patcher_get_by_id.start()

    def tearDown(self):
        self.patcher_save.stop()
        self.patcher_get_by_id.stop()
        self.patcher_delete.stop()

    def test_save_valid_comment(self):
        text = "Test Comment"
        user_id = 1
        project_id = 2
        CommentTable.save(text, user_id, project_id)
        self.mock_save.assert_called_once_with(text, user_id, project_id)


if __name__ == "__main__":
    unittest.main()
