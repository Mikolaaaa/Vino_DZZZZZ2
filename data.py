import sqlite3
from init_db import DB_PATH
from flask_login import UserMixin


# --- Работа с данными ---
class ConstructionObject:
    _table_name = "construction_objects"

    def __init__(self, id=None, name=None, address=None, deadline=None, status="Осмотр объекта"):
        self.id = id
        self.name = name
        self.address = address
        self.deadline = deadline
        self.status = status

    @classmethod
    def find(cls, object_id):
        """Находит объект по его ID."""
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute(f"SELECT * FROM {cls._table_name} WHERE id = ?", (object_id,))
            row = cursor.fetchone()
            if row:
                return cls(*row)
            return None

    def save(self):
        with sqlite3.connect(DB_PATH) as conn:
            if self.id is None:
                cursor = conn.execute(f"""
                    INSERT INTO {self._table_name} (name, address, deadline, status)
                    VALUES (?, ?, ?, ?)
                """, (self.name, self.address, self.deadline, self.status))
                self.id = cursor.lastrowid
            else:
                conn.execute(f"""
                    UPDATE {self._table_name}
                    SET name = ?, address = ?, deadline = ?, status = ?
                    WHERE id = ?
                """, (self.name, self.address, self.deadline, self.status, self.id))

    @classmethod
    def all(cls):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute(f"SELECT * FROM {cls._table_name}")
            return [cls(*row) for row in cursor.fetchall()]

    def delete(self):
        """Удаляет объект из базы данных по его ID."""
        if self.id is None:
            raise ValueError("Невозможно удалить объект без ID.")

        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(f"DELETE FROM {self._table_name} WHERE id = ?", (self.id,))
            # Устанавливаем id в None, чтобы объект стал "удаленным"
            self.id = None


class User(UserMixin):
    def __init__(self, id, username, password, desc):
        self.id = id
        self.username = username
        self.password = password
        self.desc = desc

    @classmethod
    def find_by_id(cls, user_id):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute("SELECT id, username, password, desc FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                return cls(*row)
        return None

    @classmethod
    def find_by_username(cls, username):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute("SELECT id, username, password, desc FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            if row:
                return cls(*row)
        return None


class ReserveEstimate:
    _table_name = "reserve_estimates"

    def __init__(self, id=None, name=None, quantity=0, price=0.0, construction_object_id=None, supplier_id=None, missing_material=None, missing_quantity=0, total_cost=0.0):
        self.id = id
        self.name = name
        self.quantity = quantity
        self.price = price
        self.construction_object_id = construction_object_id
        self.supplier_id = supplier_id
        self.missing_material = missing_material
        self.missing_quantity = missing_quantity
        self.total_cost = total_cost

    def save(self):
        with sqlite3.connect(DB_PATH) as conn:
            if self.id is None:
                cursor = conn.execute(f"""
                    INSERT INTO {self._table_name} (name, quantity, price, construction_object_id, supplier_id, missing_material, missing_quantity, total_cost)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (self.name, self.quantity, self.price, self.construction_object_id, self.supplier_id, self.missing_material, self.missing_quantity, self.total_cost))
                self.id = cursor.lastrowid
            else:
                conn.execute(f"""
                    UPDATE {self._table_name} 
                    SET name = ?, quantity = ?, price = ?, construction_object_id = ?, supplier_id = ?, missing_material = ?, missing_quantity = ?, total_cost = ?
                    WHERE id = ?
                """, (self.name, self.quantity, self.price, self.construction_object_id, self.supplier_id, self.missing_material, self.missing_quantity, self.total_cost, self.id))

    @classmethod
    def find_by_object(cls, object_id):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute(f"SELECT * FROM {cls._table_name} WHERE construction_object_id = ?", (object_id,))
            return [cls(*row) for row in cursor.fetchall()]




class Estimate:
    _table_name = "estimates"

    def __init__(self, id=None, object_id=None, materials=None, labor_hours=0, total_cost=0, material_type=None,
                 price=None):
        self.id = id
        self.object_id = object_id
        self.materials = materials if materials is not None else []  # Список материалов
        self.labor_hours = labor_hours
        self.total_cost = total_cost
        self.material_type = material_type
        self.price = price

    def save(self):
        with sqlite3.connect(DB_PATH) as conn:
            # Преобразуем списки в строки
            materials_str = ','.join(map(str, self.materials))  # Преобразуем список материалов в строку
            material_types_str = ','.join(map(str, self.material_type))  # Преобразуем список типов материалов в строку

            # Если объект еще не существует, создаем новый
            if self.id is None:
                cursor = conn.execute(f"""
                    INSERT INTO {self._table_name} (object_id, materials, labor_hours, total_cost, material_type)
                    VALUES (?, ?, ?, ?, ?)
                """, (self.object_id, materials_str, self.labor_hours, self.total_cost, material_types_str))
                self.id = cursor.lastrowid
            else:
                # Если объект уже существует, обновляем его
                conn.execute(f"""
                    UPDATE {self._table_name} 
                    SET object_id = ?, materials = ?, labor_hours = ?, total_cost = ?, material_type = ?
                    WHERE id = ?
                """, (self.object_id, materials_str, self.labor_hours, self.total_cost, material_types_str, self.id))

    @classmethod
    def find_by_object(cls, object_id):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute(f"SELECT * FROM {cls._table_name} WHERE object_id = ?", (object_id,))
            row = cursor.fetchone()
            if row:
                materials = row[2].split(',')  # Преобразуем строку обратно в список
                material_type = row[5].split(",")  # Преобразуем строку обратно в список
                return cls(row[0], row[1], materials, row[3], row[4], material_type)
            return None


class Comment:
    _table_name = "comments"

    def __init__(self, id=None, object_id=None, user=None, text=None):
        self.id = id
        self.object_id = object_id
        self.user = user
        self.text = text

    def save(self):
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(f"""
                INSERT INTO {self._table_name} (object_id, user, text)
                VALUES (?, ?, ?)
            """, (self.object_id, self.user, self.text))

    @classmethod
    def find_by_object(cls, object_id):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute(f"SELECT * FROM {cls._table_name} WHERE object_id = ?", (object_id,))
            return [cls(*row) for row in cursor.fetchall()]


class Workforce:
    _table_name = "workforce"

    def __init__(self, id=None, object_id=None, kval=0, workers=0, start_date=None, end_date=None):
        self.id = id
        self.object_id = object_id
        self.kval = kval
        self.workers = workers
        self.start_date = start_date
        self.end_date = end_date

    def save(self):
        with sqlite3.connect(DB_PATH) as conn:
            if self.id is None:
                cursor = conn.execute(f"""
                    INSERT INTO {self._table_name} (object_id, kval, workers, start_date, end_date)
                    VALUES (?, ?, ?, ?, ?)
                """, (self.object_id, self.kval, self.workers, self.start_date, self.end_date))
                self.id = cursor.lastrowid
            else:
                conn.execute(f"""
                    UPDATE {self._table_name}
                    SET kval = ?, workers = ?, start_date = ?, end_date = ?
                    WHERE id = ?
                """, (self.kval, self.workers, self.start_date, self.end_date, self.id))

    @classmethod
    def find_by_object(cls, object_id):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute(f"SELECT * FROM {cls._table_name} WHERE object_id = ?", (object_id,))
            row = cursor.fetchone()
            if row:
                return cls(*row)
            return None

    @classmethod
    def find_all_by_object(cls, object_id):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute(f"SELECT * FROM {cls._table_name} WHERE object_id = ?", (object_id,))
            return [cls(*row) for row in cursor.fetchall()]

    def delete(self):
        """Удаляет бригаду из базы данных по ее ID."""
        if self.id is None:
            raise ValueError("Невозможно удалить бригаду без ID.")

        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(f"DELETE FROM {self._table_name} WHERE id = ?", (self.id,))
            self.id = None


class Supplier:
    _table_name = "suppliers"

    def __init__(self, id=None, name=None, contact_info=None, type_of_materials=None, address=None):
        self.id = id
        self.name = name
        self.contact_info = contact_info
        self.type_of_materials = type_of_materials
        self.address = address


    @classmethod
    def find(cls, supplier_id):
        """Находит поставщика по его ID."""
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute(f"SELECT * FROM {cls._table_name} WHERE id = ?", (supplier_id,))
            row = cursor.fetchone()
            if row:
                return cls(*row)
            return None

    @classmethod
    def all(cls):
        """Возвращает всех поставщиков."""
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute(f"SELECT * FROM {cls._table_name}")
            return [cls(*row) for row in cursor.fetchall()]

    def save(self):
        """Сохраняет информацию о поставщике в базе данных (вставка или обновление)."""
        with sqlite3.connect(DB_PATH) as conn:
            if self.id is None:
                cursor = conn.execute(f"""
                    INSERT INTO {self._table_name} (name, contact_info, type_of_materials, address )
                    VALUES (?, ?, ?, ?)
                """, (self.name, self.contact_info, self.type_of_materials, self.address))
                self.id = cursor.lastrowid
            else:
                conn.execute(f"""
                    UPDATE {self._table_name}
                    SET name = ?, contact_info = ?, address = ?, type_of_materials = ?
                    WHERE id = ?
                """, (self.name, self.contact_info, self.address, self.type_of_materials, self.id))

    def delete(self):
        """Удаляет поставщика из базы данных по его ID."""
        if self.id is None:
            raise ValueError("Невозможно удалить поставщика без ID.")

        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(f"DELETE FROM {self._table_name} WHERE id = ?", (self.id,))
            self.id = None


class PurchaseRequest:
    _table_name = "purchase_requests"

    def __init__(self, id=None, material=None, quantity=None, price=None, supplier_id=None, status="Ожидает", request_date=None):
        self.id = id
        self.material = material
        self.quantity = quantity
        self.price = price
        self.supplier_id = supplier_id
        self.status = status
        self.request_date = request_date

    def material(self):
        return Material.find(self.material)

    def save(self):
        with sqlite3.connect(DB_PATH) as conn:
            if self.id is None:
                cursor = conn.execute(f"""
                    INSERT INTO {self._table_name} (material, quantity, price, supplier_id, status, request_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (self.material, self.quantity, self.price, self.supplier_id, self.status, self.request_date))
                self.id = cursor.lastrowid
            else:
                conn.execute(f"""
                    UPDATE {self._table_name}
                    SET material = ?, quantity = ?, price = ?, supplier_id = ?, status = ?, request_date = ?
                    WHERE id = ?
                """, (self.material, self.quantity, self.price, self.supplier_id, self.status, self.request_date, self.id))

    @classmethod
    def all(cls):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute(f"SELECT * FROM {cls._table_name}")
            return [cls(*row) for row in cursor.fetchall()]

    @classmethod
    def find(cls, request_id):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute(f"SELECT * FROM {cls._table_name} WHERE id = ?", (request_id,))
            row = cursor.fetchone()
            if row:
                return cls(*row)
            return None

    def delete(self):
        if self.id is None:
            raise ValueError("Невозможно удалить запрос без ID.")

        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(f"DELETE FROM {self._table_name} WHERE id = ?", (self.id,))
            self.id = None


class Material:
    _table_name = "materials"

    def __init__(self, id=None, name=None, quantity=None, price=None, manufacturer=None, supplier_id=None):
        self.id = id
        self.name = name
        self.quantity = quantity
        self.price = price
        self.supplier_id = supplier_id
        self.manufacturer = manufacturer

    @classmethod
    def find(cls, material_id):
        """Находит материал по его ID."""
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute(f"SELECT * FROM {cls._table_name} WHERE id = ?", (material_id,))
            row = cursor.fetchone()
            if row:
                return cls(*row)
            return None

    @classmethod
    def all(cls):
        """Возвращает все материалы."""
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute(f"SELECT * FROM {cls._table_name}")
            return [cls(*row) for row in cursor.fetchall()]

    @classmethod
    def get_by_supplier(cls, supplier_id):
        """Возвращает все материалы, поставленные определенным поставщиком."""
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute(f"SELECT * FROM {cls._table_name} WHERE supplier_id = ?", (supplier_id,))
            return [cls(*row) for row in cursor.fetchall()]

    def save(self):
        """Сохраняет материал в базе данных (вставка или обновление)."""
        with sqlite3.connect(DB_PATH) as conn:
            if self.id is None:
                cursor = conn.execute(f"""
                    INSERT INTO {self._table_name} (name, quantity, price, manufacturer, supplier_id)
                    VALUES (?, ?, ?, ?, ?)
                """, (self.name, self.quantity, self.price, self.manufacturer, self.supplier_id))
                self.id = cursor.lastrowid
            else:
                conn.execute(f"""
                    UPDATE {self._table_name}
                    SET name = ?, quantity = ?, price = ?, supplier_id = ?, manufacturer = ?
                    WHERE id = ?
                """, (self.name, self.quantity, self.price, self.supplier_id, self.manufacturer, self.id))

    def delete(self):
        """Удаляет материал из базы данных по его ID."""
        if self.id is None:
            raise ValueError("Невозможно удалить материал без ID.")

        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(f"DELETE FROM {self._table_name} WHERE id = ?", (self.id,))
            self.id = None
