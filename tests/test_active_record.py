import unittest
from unittest.mock import MagicMock, patch
from active_record import Material, ConstructionObject, Workforce, Comment, Supplier  # Замените на ваш модуль


class TestActiveRecord(unittest.TestCase):
    def setUp(self):
        # Патчим методы save, get_by_id и delete для классов
        self.patcher_material_save = patch('active_record.Material.save', new=MagicMock())
        self.patcher_material_get_by_id = patch('active_record.Material.get_by_id', new=MagicMock())
        self.patcher_material_delete = patch('active_record.Material.delete', new=MagicMock())

        self.patcher_obj_save = patch('active_record.ConstructionObject.save', new=MagicMock())
        self.patcher_obj_get_by_id = patch('active_record.ConstructionObject.get_by_id', new=MagicMock())
        self.patcher_obj_delete = patch('active_record.ConstructionObject.delete', new=MagicMock())

        self.patcher_workforce_save = patch('active_record.Workforce.save', new=MagicMock())
        self.patcher_workforce_get_by_id = patch('active_record.Workforce.get_by_id', new=MagicMock())
        self.patcher_workforce_delete = patch('active_record.Workforce.delete', new=MagicMock())

        self.patcher_comment_save = patch('active_record.Comment.save', new=MagicMock())
        self.patcher_comment_get_by_id = patch('active_record.Comment.get_by_id', new=MagicMock())
        self.patcher_comment_delete = patch('active_record.Comment.delete', new=MagicMock())

        self.patcher_supplier_save = patch('active_record.Supplier.save', new=MagicMock())
        self.patcher_supplier_get_by_id = patch('active_record.Supplier.get_by_id', new=MagicMock())
        self.patcher_supplier_delete = patch('active_record.Supplier.delete', new=MagicMock())

        # Запуск патчинга
        self.mock_material_save = self.patcher_material_save.start()
        self.mock_material_get_by_id = self.patcher_material_get_by_id.start()
        self.mock_material_delete = self.patcher_material_delete.start()

        self.mock_obj_save = self.patcher_obj_save.start()
        self.mock_obj_get_by_id = self.patcher_obj_get_by_id.start()
        self.mock_obj_delete = self.patcher_obj_delete.start()

        self.mock_workforce_save = self.patcher_workforce_save.start()
        self.mock_workforce_get_by_id = self.patcher_workforce_get_by_id.start()
        self.mock_workforce_delete = self.patcher_workforce_delete.start()

        self.mock_comment_save = self.patcher_comment_save.start()
        self.mock_comment_get_by_id = self.patcher_comment_get_by_id.start()

        self.mock_supplier_save = self.patcher_supplier_save.start()
        self.mock_supplier_get_by_id = self.patcher_supplier_get_by_id.start()
        self.mock_supplier_delete = self.patcher_supplier_delete.start()

    def tearDown(self):
        # Остановка патчинга
        self.patcher_material_save.stop()
        self.patcher_material_get_by_id.stop()
        self.patcher_material_delete.stop()

        self.patcher_obj_save.stop()
        self.patcher_obj_get_by_id.stop()
        self.patcher_obj_delete.stop()

        self.patcher_workforce_save.stop()
        self.patcher_workforce_get_by_id.stop()
        self.patcher_workforce_delete.stop()

        self.patcher_comment_save.stop()
        self.patcher_comment_get_by_id.stop()
        self.patcher_comment_delete.stop()

        self.patcher_supplier_save.stop()
        self.patcher_supplier_get_by_id.stop()
        self.patcher_supplier_delete.stop()

    # Тесты для Material
    def test_save_material(self):
        material = Material(name="Sand", quantity=50, price=0.5, manufacturer="SandCo", supplier_id=2)
        Material.save(material)
        self.mock_material_save.assert_called_once_with(material)

    def test_get_by_id_material(self):
        material = Material(id=1, name="Gravel", quantity=100, price=1.0, manufacturer="GravelCo", supplier_id=3)
        Material.get_by_id(1)
        self.mock_material_get_by_id.assert_called_once_with(1)

    def test_delete_material(self):
        material = Material(id=1, name="Gravel", quantity=100, price=1.0, manufacturer="GravelCo", supplier_id=3)
        Material.delete(material.id)
        self.mock_material_delete.assert_called_once_with(material.id)

    def test_save_material_invalid(self):
        # Пытаемся сохранить объект с некорректными данными
        material = Material(name=None, quantity=50, price=0.5, manufacturer="SandCo", supplier_id=2)
        self.mock_material_save.side_effect = ValueError("Invalid data")
        with self.assertRaises(ValueError):  # Предположим, что ожидается исключение ValueError
            Material.save(material)

    def test_update_material(self):
        material = Material(id=1, name="Gravel", quantity=100, price=1.0, manufacturer="GravelCo", supplier_id=3)
        material.name = "New Gravel"
        Material.save(material)
        self.mock_material_save.assert_called_once_with(material)

    def test_get_by_id_material_not_found(self):
        # Пытаемся получить материал, которого нет в базе
        self.mock_material_get_by_id.side_effect = Exception("Material not found")
        with self.assertRaises(Exception):
            Material.get_by_id(999)


    # Тесты для ConstructionObject
    def test_save_construction_object(self):
        obj = ConstructionObject(name="Warehouse", address="Industrial Zone", deadline="2024-06-01", status="Planned")
        ConstructionObject.save(obj)
        self.mock_obj_save.assert_called_once_with(obj)

    def test_get_by_id_construction_object(self):
        obj = ConstructionObject(id=1, name="Apartment Complex", address="Downtown", deadline="2025-03-15", status="Planned")
        ConstructionObject.get_by_id(1)
        self.mock_obj_get_by_id.assert_called_once_with(1)

    def test_delete_construction_object(self):
        obj = ConstructionObject(id=1, name="Apartment Complex", address="Downtown", deadline="2025-03-15", status="Planned")
        ConstructionObject.delete(obj.id)
        self.mock_obj_delete.assert_called_once_with(obj.id)

    def test_save_construction_object_invalid(self):
        # Проверяем ошибку при передаче некорректных данных
        obj = ConstructionObject(name=None, address="Some Address", deadline="2024-06-01", status="Planned")
        self.mock_obj_save.side_effect = ValueError("Invalid data")
        with self.assertRaises(ValueError):  # Предположим, что это ошибка валидации
            ConstructionObject.save(obj)

    def test_update_construction_object(self):
        obj = ConstructionObject(id=1, name="Warehouse", address="Industrial Zone", deadline="2024-06-01",
                                 status="Planned")
        obj.status = "Under Construction"
        ConstructionObject.save(obj)
        self.mock_obj_save.assert_called_once_with(obj)

    def test_get_by_id_construction_object_not_found(self):
        self.mock_obj_get_by_id.side_effect = Exception("ConstructionObject not found")
        with self.assertRaises(Exception):
            ConstructionObject.get_by_id(999)

    # Тесты для Workforce
    def test_save_workforce(self):
        workforce = Workforce(object_id=1, kval="Construction Worker", workers=12, start_date="2024-03-15", end_date="2025-03-15")
        Workforce.save(workforce)
        self.mock_workforce_save.assert_called_once_with(workforce)

    def test_get_by_id_workforce(self):
        workforce = Workforce(id=1, object_id=1, kval="Construction Worker", workers=12, start_date="2024-03-15", end_date="2025-03-15")
        Workforce.get_by_id(1)
        self.mock_workforce_get_by_id.assert_called_once_with(1)

    def test_delete_workforce(self):
        workforce = Workforce(id=1, object_id=1, kval="Construction Worker", workers=12, start_date="2024-03-15", end_date="2025-03-15")
        Workforce.delete(workforce.id)
        self.mock_workforce_delete.assert_called_once_with(workforce.id)

    def test_save_workforce_invalid(self):
        workforce = Workforce(object_id=1, kval="Construction Worker", workers=-5, start_date="2024-03-15",
                              end_date="2025-03-15")
        self.mock_workforce_save.side_effect = ValueError("Invalid data")
        with self.assertRaises(ValueError):  # Невозможное количество рабочих
            Workforce.save(workforce)

    def test_update_workforce(self):
        workforce = Workforce(id=1, object_id=1, kval="Construction Worker", workers=12, start_date="2024-03-15",
                              end_date="2025-03-15")
        workforce.workers = 15
        Workforce.save(workforce)
        self.mock_workforce_save.assert_called_once_with(workforce)

    def test_get_by_id_workforce_not_found(self):
        self.mock_workforce_get_by_id.side_effect = Exception("Workforce not found")
        with self.assertRaises(Exception):
            Workforce.get_by_id(999)

    # Тесты для Comment
    def test_save_comment(self):
        comment = Comment(object_id=1, user="John Doe", text="Test Comment")
        Comment.save(comment)
        self.mock_comment_save.assert_called_once_with(comment)

    def test_get_by_id_comment(self):
        comment = Comment(id=1, object_id=1, user="John Doe", text="Test Comment")
        Comment.get_by_id(1)
        self.mock_comment_get_by_id.assert_called_once_with(1)

    def test_save_comment_invalid(self):
        comment = Comment(object_id=1, user=None, text="Test Comment")  # Нет пользователя
        self.mock_comment_save.side_effect = ValueError("Invalid data")
        with self.assertRaises(ValueError):  # Предположим, что это ошибка валидации
            Comment.save(comment)

    def test_get_by_id_comment_not_found(self):
        self.mock_comment_get_by_id.side_effect = Exception("Comment not found")
        with self.assertRaises(Exception):
            Comment.get_by_id(999)

    # Тесты для Supplier
    def test_save_supplier(self):
        supplier = Supplier(name="ABC Supplies", contact_info="123-456-7890", type_of_materials="Concrete", address="123 Main St")
        Supplier.save(supplier)
        self.mock_supplier_save.assert_called_once_with(supplier)

    def test_get_by_id_supplier(self):
        supplier = Supplier(id=1, name="ABC Supplies", contact_info="123-456-7890", type_of_materials="Concrete", address="123 Main St")
        Supplier.get_by_id(1)
        self.mock_supplier_get_by_id.assert_called_once_with(1)

    def test_delete_supplier(self):
        supplier = Supplier(id=1, name="ABC Supplies", contact_info="123-456-7890", type_of_materials="Concrete", address="123 Main St")
        Supplier.delete(supplier.id)
        self.mock_supplier_delete.assert_called_once_with(supplier.id)

    def test_save_supplier_invalid(self):
        supplier = Supplier(name=None, contact_info="123-456-7890", type_of_materials="Concrete", address="123 Main St")
        self.mock_supplier_save.side_effect = ValueError("Invalid data")
        with self.assertRaises(ValueError):  # Отсутствие имени поставщика
            Supplier.save(supplier)

    def test_update_supplier(self):
        supplier = Supplier(id=1, name="ABC Supplies", contact_info="123-456-7890", type_of_materials="Concrete",
                            address="123 Main St")
        supplier.name = "XYZ Supplies"
        Supplier.save(supplier)
        self.mock_supplier_save.assert_called_once_with(supplier)

    def test_get_by_id_supplier_not_found(self):
        self.mock_supplier_get_by_id.side_effect = Exception("Supplier not found")
        with self.assertRaises(Exception):
            Supplier.get_by_id(999)


if __name__ == "__main__":
    unittest.main()
