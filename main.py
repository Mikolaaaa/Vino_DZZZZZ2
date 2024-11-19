from flask import Flask, request, jsonify, render_template, redirect, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"

DB_PATH = "construction_system.db"


# --- Инициализация базы данных ---
def initialize_database():
    with sqlite3.connect(DB_PATH) as conn:
        # Таблица для поставщиков
        conn.execute("""
            CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                address TEXT,
                contact_info TEXT
            )
        """)

        # Таблица для объектов
        conn.execute("""
            CREATE TABLE IF NOT EXISTS construction_objects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                address TEXT NOT NULL,
                deadline TEXT NOT NULL,
                status TEXT NOT NULL
            )
        """)

        # Таблица для материалов
        conn.execute("""
            CREATE TABLE IF NOT EXISTS materials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                construction_object_id INTEGER,
                supplier_id INTEGER,
                FOREIGN KEY (construction_object_id) REFERENCES construction_objects(id) ON DELETE SET NULL,
                FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE SET NULL
            )
        """)

        # Таблица для смет
        conn.execute("""
            CREATE TABLE IF NOT EXISTS estimates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                object_id INTEGER NOT NULL,
                materials TEXT NOT NULL,  -- Здесь хранится список ID материалов
                labor_hours INTEGER NOT NULL,
                total_cost REAL NOT NULL,
                material_type TEXT NOT NULL,
                FOREIGN KEY (object_id) REFERENCES construction_objects (id) ON DELETE CASCADE
            )
        """)

        # Таблица для комментариев
        conn.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                object_id INTEGER NOT NULL,
                user TEXT NOT NULL,
                text TEXT NOT NULL,
                FOREIGN KEY (object_id) REFERENCES construction_objects (id) ON DELETE CASCADE
            )
        """)

        # Таблица для рабочей силы
        conn.execute("""
            CREATE TABLE IF NOT EXISTS workforce (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                object_id INTEGER NOT NULL,
                labor_hours INTEGER NOT NULL,
                workers INTEGER NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                FOREIGN KEY (object_id) REFERENCES construction_objects (id) ON DELETE CASCADE
            )
        """)

    print("База данных и таблицы инициализированы.")


# --- Работа с данными ---
class ConstructionObject:
    _table_name = "construction_objects"

    def __init__(self, id=None, name=None, address=None, deadline=None, status="Pending"):
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


class Estimate:
    _table_name = "estimates"

    def __init__(self, id=None, object_id=None, materials=None, labor_hours=0, total_cost=0, material_type=None, price=None):
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

    def __init__(self, id=None, object_id=None, labor_hours=0, workers=0, start_date=None, end_date=None):
        self.id = id
        self.object_id = object_id
        self.labor_hours = labor_hours
        self.workers = workers
        self.start_date = start_date
        self.end_date = end_date

    def save(self):
        with sqlite3.connect(DB_PATH) as conn:
            if self.id is None:
                cursor = conn.execute(f"""
                    INSERT INTO {self._table_name} (object_id, labor_hours, workers, start_date, end_date)
                    VALUES (?, ?, ?, ?, ?)
                """, (self.object_id, self.labor_hours, self.workers, self.start_date, self.end_date))
                self.id = cursor.lastrowid
            else:
                conn.execute(f"""
                    UPDATE {self._table_name}
                    SET labor_hours = ?, workers = ?, start_date = ?, end_date = ?
                    WHERE id = ?
                """, (self.labor_hours, self.workers, self.start_date, self.end_date, self.id))

    @classmethod
    def find_by_object(cls, object_id):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute(f"SELECT * FROM {cls._table_name} WHERE object_id = ?", (object_id,))
            row = cursor.fetchone()
            if row:
                return cls(*row)
            return None


class Supplier:
    _table_name = "suppliers"

    def __init__(self, id=None, name=None, contact_info=None, address=None):
        self.id = id
        self.name = name
        self.contact_info = contact_info
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
                    INSERT INTO {self._table_name} (name, contact_info, address)
                    VALUES (?, ?, ?)
                """, (self.name, self.contact_info, self.address))
                self.id = cursor.lastrowid
            else:
                conn.execute(f"""
                    UPDATE {self._table_name}
                    SET name = ?, contact_info = ?, address = ?
                    WHERE id = ?
                """, (self.name, self.contact_info, self.address, self.id))

    def delete(self):
        """Удаляет поставщика из базы данных по его ID."""
        if self.id is None:
            raise ValueError("Невозможно удалить поставщика без ID.")

        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(f"DELETE FROM {self._table_name} WHERE id = ?", (self.id,))
            self.id = None


class Material:
    _table_name = "materials"

    def __init__(self, id=None, name=None, quantity=None, price=None, construction_object_id=None, supplier_id=None):
        self.id = id
        self.name = name
        self.quantity = quantity
        self.price = price
        self.construction_object_id = construction_object_id
        self.supplier_id = supplier_id

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
    def get_by_construction_object(cls, object_id):
        """Возвращает все материалы для конкретного объекта строительства по его ID."""
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute(f"SELECT * FROM {cls._table_name} WHERE construction_object_id = ?", (object_id,))
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
                    INSERT INTO {self._table_name} (name, quantity, price, construction_object_id, supplier_id)
                    VALUES (?, ?, ?, ?, ?)
                """, (self.name, self.quantity, self.price, self.construction_object_id, self.supplier_id))
                self.id = cursor.lastrowid
            else:
                conn.execute(f"""
                    UPDATE {self._table_name}
                    SET name = ?, quantity = ?, price = ?, construction_object_id = ?, supplier_id = ?
                    WHERE id = ?
                """, (self.name, self.quantity, self.price, self.construction_object_id, self.supplier_id, self.id))

    def delete(self):
        """Удаляет материал из базы данных по его ID."""
        if self.id is None:
            raise ValueError("Невозможно удалить материал без ID.")

        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(f"DELETE FROM {self._table_name} WHERE id = ?", (self.id,))
            self.id = None


# --- API и Роуты ---
@app.route("/")
def index():
    objects = ConstructionObject.all()
    return render_template("index.html", objects=objects)


@app.route("/add", methods=["GET", "POST"])
def add_object():
    if request.method == "POST":
        name = request.form["name"]
        address = request.form["address"]
        deadline = request.form["deadline"]
        obj = ConstructionObject(name=name, address=address, deadline=deadline)
        obj.save()
        return redirect(url_for("index"))
    return render_template("add_object.html")


@app.route('/delete_object/<int:object_id>', methods=['GET', 'POST'])
def delete_object(object_id):
    # Найти объект в базе данных по ID
    obj = ConstructionObject.find(object_id)

    if obj:
        obj.delete()  # Удалить объект

    return redirect(url_for('index'))  # Перенаправить на главную страницу


@app.route("/api/objects", methods=["GET"])
def get_objects():
    objects = [vars(obj) for obj in ConstructionObject.all()]
    return jsonify(objects)


@app.route("/estimate/<int:object_id>", methods=["GET", "POST"])
def manage_estimate(object_id):
    estimate = Estimate.find_by_object(object_id)
    obj = ConstructionObject.find(object_id)
    materials = Material.get_by_construction_object(object_id)  # Получаем все материалы для объекта

    # Создаем словарь "id: name-quantity-price"
    material_options = {}
    for material in materials:
        material_options[material.id] = f"{material.name} - {material.quantity} кг - {material.price} руб/кг"

    if estimate and estimate.material_type:
        # Преобразуем значения в целые числа
        estimate.material_type = list(map(int, estimate.material_type))

    print(f"material_options {material_options}")

    # Если GET-запрос, вычисляем итоговую стоимость
    total_cost = 0
    if estimate:
        for material_id in estimate.materials:
            material = Material.find(material_id)
            if material:
                total_cost += material.price * material.quantity

    print(f"total_cost {total_cost}")

    if request.method == "POST":
        material_ids = request.form.getlist("materials")  # Получаем выбранные материалы
        labor_hours = int(request.form["labor_hours"])
        total_cost = float(request.form["total_cost"])
        material_type_ids = request.form.getlist("material_type[]")  # Получаем выбранные id материалов

        # Пересчитываем итоговую стоимость
        total_cost = 0
        for material_id in material_ids:
            material = Material.find(material_id)
            quantity = int(request.form.get(f"material_quantity_{material_id}", 0))  # Получаем количество для каждого материала
            if material:
                total_cost += material.price * quantity  # Пересчитываем стоимость с учетом количества

        if estimate is None:
            estimate = Estimate(
                object_id=object_id,
                materials=material_ids,
                labor_hours=labor_hours,
                total_cost=total_cost,
                material_type=material_type_ids
            )
        else:
            estimate.materials = material_ids
            estimate.labor_hours = labor_hours
            estimate.total_cost = total_cost
            estimate.material_type = material_type_ids  # Сохраняем новые типы материалов

        estimate.save()
        return redirect(url_for("manage_estimate", object_id=object_id))

    # Передаем материалы и их данные в шаблон
    return render_template(
        "manage_estimate.html",
        obj=obj,
        estimate=estimate,
        materials=materials,
        material_options=material_options
    )



@app.route("/comments/<int:object_id>", methods=["GET", "POST"])
def comments(object_id):
    obj = ConstructionObject.find(object_id)
    if request.method == "POST":
        user = request.form["user"]
        text = request.form["text"]
        comment = Comment(object_id=object_id, user=user, text=text)
        comment.save()
        return redirect(url_for("comments", object_id=object_id))
    comments = Comment.find_by_object(object_id)
    return render_template("comments.html", obj=obj, comments=comments)

@app.route("/workforce/<int:object_id>", methods=["GET", "POST"])
def manage_workforce(object_id):
    workforce = Workforce.find_by_object(object_id)
    obj = ConstructionObject.find(object_id)
    if request.method == "POST":
        labor_hours = int(request.form["labor_hours"])
        workers = int(request.form["workers"])
        start_date = request.form["start_date"]
        end_date = request.form["end_date"]
        if workforce is None:
            workforce = Workforce(object_id=object_id, labor_hours=labor_hours, workers=workers,
                                  start_date=start_date, end_date=end_date)
        else:
            workforce.labor_hours = labor_hours
            workforce.workers = workers
            workforce.start_date = start_date
            workforce.end_date = end_date
        workforce.save()
        return redirect(url_for("index"))
    return render_template("manage_workforce.html", obj=obj, workforce=workforce)


@app.route("/suppliers", methods=["GET", "POST"])
def manage_suppliers():
    if request.method == "POST":
        name = request.form["name"]
        contact_info = request.form["contact_info"]
        address = request.form["address"]
        supplier = Supplier(name=name, contact_info=contact_info, address=address)
        supplier.save()
        return redirect(url_for("manage_suppliers"))

    suppliers = Supplier.all()
    return render_template("manage_suppliers.html", suppliers=suppliers)


@app.route("/supplier/<int:supplier_id>", methods=["GET", "POST", "DELETE"])
def manage_supplier(supplier_id):
    supplier = Supplier.find(supplier_id)
    if not supplier:
        return "Поставщик не найден", 404

    if request.method == "POST":
        supplier.name = request.form["name"]
        supplier.contact_info = request.form["contact_info"]
        supplier.address = request.form["address"]
        supplier.save()
        return redirect(url_for("manage_suppliers"))

    if request.method == "DELETE":
        supplier.delete()
        return redirect(url_for("manage_suppliers"))

    return render_template("manage_supplier.html", supplier=supplier)


@app.route("/materials", methods=["GET", "POST"])
def manage_materials():
    if request.method == "POST":
        name = request.form["name"]
        quantity = int(request.form["quantity"])
        price = float(request.form["price"])
        construction_object_id = int(request.form["construction_object_id"])
        supplier_id = int(request.form["supplier_id"])
        material = Material(name=name, quantity=quantity, price=price, construction_object_id=construction_object_id,
                            supplier_id=supplier_id)
        material.save()
        return redirect(url_for("manage_materials"))

    materials = Material.all()
    return render_template("manage_materials.html", materials=materials)


@app.route("/material/<int:material_id>", methods=["GET", "POST", "DELETE"])
def manage_material(material_id):
    material = Material.find(material_id)
    if not material:
        return "Материал не найден", 404

    if request.method == "POST":
        material.name = request.form["name"]
        material.quantity = int(request.form["quantity"])
        material.price = float(request.form["price"])
        material.construction_object_id = int(request.form["construction_object_id"])
        material.supplier_id = int(request.form["supplier_id"])
        material.save()
        return redirect(url_for("manage_materials"))

    if request.method == "DELETE":
        material.delete()
        return redirect(url_for("manage_materials"))

    return render_template("manage_material.html", material=material)

# --- Инициализация приложения ---
if __name__ == "__main__":
    initialize_database()
    app.run(debug=True)
