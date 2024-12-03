import sqlite3

from flask_login import UserMixin
#DB_PATH = "test.db"  # для тестов
DB_PATH = "construction_system2222.db" # оригинад


class ActiveRecordBase:
    @staticmethod
    def connect():
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn


class Material(ActiveRecordBase):
    def __init__(self, id=None, name=None, quantity=None, price=None, manufacturer=None, supplier_id=None):
        self.id = id
        self.name = name
        self.quantity = quantity
        self.price = price
        self.manufacturer = manufacturer
        self.supplier_id = supplier_id

    @staticmethod
    def from_row(row):
        return Material(
            id=row["id"], name=row["name"], quantity=row["quantity"],
            price=row["price"], manufacturer=row["manufacturer"], supplier_id=row["supplier_id"]
        )

    @staticmethod
    def get_by_id(material_id):
        conn = Material.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM materials WHERE id = ?", (material_id,))
        row = cursor.fetchone()
        conn.close()
        return Material.from_row(row) if row else None

    @staticmethod
    def get_all():
        conn = Material.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM materials")
        rows = cursor.fetchall()
        conn.close()
        return [Material.from_row(row) for row in rows]

    def save(self):
        conn = self.connect()
        cursor = conn.cursor()
        if self.id:
            cursor.execute("""
                UPDATE materials 
                SET name = ?, quantity = ?, price = ?, manufacturer = ?, supplier_id = ?
                WHERE id = ?""",
                           (self.name, self.quantity, self.price, self.manufacturer, self.supplier_id, self.id)
                           )
        else:
            cursor.execute("""
                INSERT INTO materials (name, quantity, price, manufacturer, supplier_id)
                VALUES (?, ?, ?, ?, ?)""",
                           (self.name, self.quantity, self.price, self.manufacturer, self.supplier_id)
                           )
            self.id = cursor.lastrowid
        conn.commit()
        conn.close()

    def delete(material_id):
        conn = Material.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM materials WHERE id = ?", (material_id,))
        conn.commit()
        conn.close()


class ConstructionObject(ActiveRecordBase):
    def __init__(self, id=None, name=None, address=None, deadline=None, status=None):
        self.id = id
        self.name = name
        self.address = address
        self.deadline = deadline
        self.status = status

    @staticmethod
    def from_row(row):
        return ConstructionObject(
            id=row["id"], name=row["name"], address=row["address"],
            deadline=row["deadline"], status=row["status"]
        )

    @staticmethod
    def get_by_id(object_id):
        conn = ConstructionObject.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM construction_objects WHERE id = ?", (object_id,))
        row = cursor.fetchone()
        conn.close()
        return ConstructionObject.from_row(row) if row else None

    @staticmethod
    def get_all():
        conn = ConstructionObject.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM construction_objects")
        rows = cursor.fetchall()
        conn.close()
        return [ConstructionObject.from_row(row) for row in rows]

    def save(self):
        conn = self.connect()
        cursor = conn.cursor()
        if self.id:
            cursor.execute("""
                UPDATE construction_objects
                SET name = ?, address = ?, deadline = ?, status = ?
                WHERE id = ?""",
                           (self.name, self.address, self.deadline, self.status, self.id)
                           )
        else:
            cursor.execute("""
                INSERT INTO construction_objects (name, address, deadline, status)
                VALUES (?, ?, ?, ?)""",
                           (self.name, self.address, self.deadline, self.status)
                           )
            self.id = cursor.lastrowid
        conn.commit()
        conn.close()

    def delete(object_id):
        conn = ConstructionObject.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM construction_objects WHERE id = ?", (object_id,))
        conn.commit()
        conn.close()


class ReserveEstimate(ActiveRecordBase):
    def __init__(self, id=None, name=None, quantity=None, price=None, construction_object_id=None, supplier_id=None, missing_material=None,
                 missing_quantity=None, total_cost=None):
        self.id = id
        self.name = name
        self.quantity = quantity
        self.price = price
        self.construction_object_id = construction_object_id
        self.supplier_id = supplier_id
        self.missing_material = missing_material
        self.missing_quantity = missing_quantity
        self.total_cost = total_cost

    @staticmethod
    def from_row(row):
        return ReserveEstimate(
            id=row["id"], name=row["name"], quantity=row["quantity"], price=row["price"],
            construction_object_id=row["construction_object_id"], supplier_id=row["supplier_id"],
            missing_material=row["missing_material"], missing_quantity=row["missing_quantity"],
            total_cost=row["total_cost"]
        )

    @staticmethod
    def get_all():
        conn = ReserveEstimate.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reserve_estimates")
        rows = cursor.fetchall()
        conn.close()
        return [ReserveEstimate.from_row(row) for row in rows]

    @staticmethod
    def get_by_id(object_id):
        conn = ReserveEstimate.connect()
        cursor = conn.cursor()
        cursor = cursor.execute("SELECT * FROM reserve_estimates WHERE construction_object_id = ?", (object_id,))
        rows = cursor.fetchall()
        conn.close()
        return [ReserveEstimate.from_row(row) for row in rows]

    def save(self):
        conn = self.connect()
        cursor = conn.cursor()
        if self.id:
            cursor.execute("""
                UPDATE reserve_estimates 
                SET name = ?, quantity = ?, price = ?, construction_object_id = ?, supplier_id = ?, 
                    missing_material = ?, missing_quantity = ?, total_cost = ?
                WHERE id = ?""",
                           (self.name, self.quantity, self.price, self.construction_object_id, self.supplier_id,
                            self.missing_material, self.missing_quantity, self.total_cost, self.id)
                           )
        else:
            cursor.execute("""
                INSERT INTO reserve_estimates 
                (name, quantity, price, construction_object_id, supplier_id, missing_material, missing_quantity, total_cost)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                           (self.name, self.quantity, self.price, self.construction_object_id, self.supplier_id,
                            self.missing_material, self.missing_quantity, self.total_cost)
                           )
            self.id = cursor.lastrowid
        conn.commit()
        conn.close()

    def delete(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM reserve_estimates WHERE id = ?", (self.id,))
        conn.commit()
        conn.close()


class Workforce(ActiveRecordBase):
    def __init__(self, id=None, object_id=None, kval=None, workers=None, start_date=None, end_date=None):
        self.id = id
        self.object_id = object_id
        self.kval = kval
        self.workers = workers
        self.start_date = start_date
        self.end_date = end_date

    @staticmethod
    def from_row(row):
        return Workforce(
            id=row["id"], object_id=row["object_id"], kval=row["kval"],
            workers=row["workers"], start_date=row["start_date"], end_date=row["end_date"]
        )

    @staticmethod
    def get_all():
        conn = Workforce.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM workforce")
        rows = cursor.fetchall()
        conn.close()
        return [Workforce.from_row(row) for row in rows]

    @staticmethod
    def get_by_id(workforce_id):
        conn = Workforce.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM workforce WHERE object_id = ?", (workforce_id,))
        rows = cursor.fetchall()
        conn.close()
        return [Workforce.from_row(row) for row in rows]

    def save(self):
        conn = self.connect()
        cursor = conn.cursor()
        if self.id:
            cursor.execute("""
                UPDATE workforce 
                SET object_id = ?, kval = ?, workers = ?, start_date = ?, end_date = ?
                WHERE id = ?""",
                           (self.object_id, self.kval, self.workers, self.start_date, self.end_date, self.id)
                           )
        else:
            cursor.execute("""
                INSERT INTO workforce (object_id, kval, workers, start_date, end_date)
                VALUES (?, ?, ?, ?, ?)""",
                           (self.object_id, self.kval, self.workers, self.start_date, self.end_date)
                           )
            self.id = cursor.lastrowid
        conn.commit()
        conn.close()

    def delete(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM workforce WHERE id = ?", (self.id,))
        conn.commit()
        conn.close()


class Supplier(ActiveRecordBase):
    def __init__(self, id=None, name=None, contact_info=None, type_of_materials=None, address=None):
        self.id = id
        self.name = name
        self.contact_info = contact_info
        self.type_of_materials = type_of_materials
        self.address = address

    @staticmethod
    def from_row(row):
        return Supplier(
            id=row["id"], name=row["name"], contact_info=row["contact_info"],
            type_of_materials=row["type_of_materials"], address=row["address"]
        )

    @classmethod
    def get_by_id(cls, supplier_id):
        conn = Supplier.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM suppliers WHERE id = ?", (supplier_id,))
        row = cursor.fetchone()
        conn.close()
        return Supplier.from_row(row) if row else None

    @staticmethod
    def get_all():
        conn = Supplier.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM suppliers")
        rows = cursor.fetchall()
        conn.close()
        return [Supplier.from_row(row) for row in rows]

    def save(self):
        conn = self.connect()
        cursor = conn.cursor()
        if self.id:
            cursor.execute("""
                UPDATE suppliers 
                SET name = ?, contact_info = ?, type_of_materials = ?, address = ?
                WHERE id = ?""",
                           (self.name, self.contact_info, self.type_of_materials, self.address, self.id)
                           )
        else:
            cursor.execute("""
                INSERT INTO suppliers (name, contact_info, type_of_materials, address)
                VALUES (?, ?, ?, ?)""",
                           (self.name, self.contact_info, self.type_of_materials, self.address)
                           )
            self.id = cursor.lastrowid
        conn.commit()
        conn.close()

    def delete(supplier_id):
        conn = Supplier.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM suppliers WHERE id = ?", (supplier_id,))
        conn.commit()
        conn.close()


class Comment(ActiveRecordBase):

    def __init__(self, id=None, object_id=None, user=None, text=None):
        self.id = id
        self.object_id = object_id
        self.user = user
        self.text = text

    @staticmethod
    def from_row(row):
        return Comment(
            id=row[0], object_id=row[1], user=row[2], text=row[3]
        )

    def save(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO comments (object_id, user, text)
            VALUES (?, ?, ?)""",
                       (self.object_id, self.user, self.text)
                       )
        self.id = cursor.lastrowid
        conn.commit()
        conn.close()

    @classmethod
    def get_by_id(cls, object_id):
        print(f"object_id {object_id}")
        conn = Comment.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM comments WHERE object_id = ?", (object_id,))
        rows = cursor.fetchall()
        conn.close()
        return [Comment.from_row(row) for row in rows]


class PurchaseRequest(ActiveRecordBase):

    def __init__(self, id=None, material=None, quantity=None, price=None, supplier_id=None, status="Ожидает", request_date=None):
        self.id = id
        self.material = material
        self.quantity = quantity
        self.price = price
        self.supplier_id = supplier_id
        self.status = status
        self.request_date = request_date

    @staticmethod
    def from_row(row):
        return PurchaseRequest(
            id=row["id"], material=row["material"], quantity=row["quantity"],
            price=row["price"], supplier_id=row["supplier_id"], status=row["status"],
            request_date=row["request_date"]
        )

    def material(self):
        return Material.get_by_id(self.material)

    def save(self):
        conn = self.connect()
        cursor = conn.cursor()
        if self.id:
            cursor.execute("""
                UPDATE purchase_requests 
                SET material = ?, quantity = ?, price = ?, supplier_id = ?, status = ?, request_date = ?
                WHERE id = ?""",
                           (self.material, self.quantity, self.price, self.supplier_id, self.status, self.request_date, self.id)
                           )
        else:
            cursor.execute("""
                INSERT INTO purchase_requests(material, quantity, price, supplier_id, status, request_date)
                VALUES (?, ?, ?, ?, ?, ?)""",
                           (self.material, self.quantity, self.price, self.supplier_id, self.status, self.request_date)
                           )
            self.id = cursor.lastrowid
        conn.commit()
        conn.close()

    @staticmethod
    def get_all():
        conn = PurchaseRequest.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM purchase_requests")
        rows = cursor.fetchall()
        conn.close()
        return [PurchaseRequest.from_row(row) for row in rows]

    @classmethod
    def get_by_id(cls, request_id):
        conn = PurchaseRequest.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM purchase_requests WHERE id = ?", (request_id,))
        row = cursor.fetchone()
        conn.close()
        return PurchaseRequest.from_row(row) if row else None

    def delete(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM purchase_requests WHERE id = ?", (self.id,))
        conn.commit()
        conn.close()


class User(ActiveRecordBase, UserMixin):

    def __init__(self, id, username, password, desc):
        self.id = id
        self.username = username
        self.password = password
        self.desc = desc

    def get_id(self):
        """Метод для получения уникального идентификатора пользователя."""
        return self.id

    @staticmethod
    def from_row(row):
        if len(row) == 4:
            return User(
                id=row[0],
                username=row[1],
                password=row[2],
                desc=row[3]
            )
        return None

    @classmethod
    def get_by_id(cls, user_id):
        conn = User.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return User.from_row(row) if row else None

    @classmethod
    def get_by_username(cls, username):
        print(f"username2 {username}")
        conn = User.connect()
        cursor = conn.cursor()
        cursor = cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        print(row[0], row[1])
        conn.close()
        # Печатаем данные, полученные из базы
        print(f"Row from DB: {row[0], row[1], row[3]}")
        return User.from_row(row)
