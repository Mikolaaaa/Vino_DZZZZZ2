from flask import Flask, request, jsonify, render_template, redirect, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"

DB_PATH = "construction_system.db"


# --- Инициализация базы данных ---
def initialize_database():
    with sqlite3.connect(DB_PATH) as conn:
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
        # Таблица для смет
        conn.execute("""
            CREATE TABLE IF NOT EXISTS estimates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                object_id INTEGER NOT NULL,
                materials TEXT NOT NULL,
                labor_hours INTEGER NOT NULL,
                total_cost REAL NOT NULL,
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


class Estimate:
    _table_name = "estimates"

    def __init__(self, id=None, object_id=None, materials=None, labor_hours=0, total_cost=0):
        self.id = id
        self.object_id = object_id
        self.materials = materials
        self.labor_hours = labor_hours
        self.total_cost = total_cost

    def save(self):
        with sqlite3.connect(DB_PATH) as conn:
            if self.id is None:
                cursor = conn.execute(f"""
                    INSERT INTO {self._table_name} (object_id, materials, labor_hours, total_cost)
                    VALUES (?, ?, ?, ?)
                """, (self.object_id, self.materials, self.labor_hours, self.total_cost))
                self.id = cursor.lastrowid
            else:
                conn.execute(f"""
                    UPDATE {self._table_name}
                    SET materials = ?, labor_hours = ?, total_cost = ?
                    WHERE id = ?
                """, (self.materials, self.labor_hours, self.total_cost, self.id))

    @classmethod
    def find_by_object(cls, object_id):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute(f"SELECT * FROM {cls._table_name} WHERE object_id = ?", (object_id,))
            row = cursor.fetchone()
            if row:
                return cls(*row)
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


@app.route("/api/objects", methods=["GET"])
def get_objects():
    objects = [vars(obj) for obj in ConstructionObject.all()]
    return jsonify(objects)


@app.route("/estimate/<int:object_id>", methods=["GET", "POST"])
def manage_estimate(object_id):
    estimate = Estimate.find_by_object(object_id)
    obj = ConstructionObject.find(object_id)
    if request.method == "POST":
        materials = request.form["materials"]
        labor_hours = int(request.form["labor_hours"])
        total_cost = float(request.form["total_cost"])
        if estimate is None:
            estimate = Estimate(object_id=object_id, materials=materials, labor_hours=labor_hours, total_cost=total_cost)
        else:
            estimate.materials = materials
            estimate.labor_hours = labor_hours
            estimate.total_cost = total_cost
        estimate.save()
        return redirect(url_for("index"))
    return render_template("manage_estimate.html", obj=obj, estimate=estimate)



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


@app.route("/comments/<int:object_id>")
def view_comments(object_id):
    comments = Comment.find_by_object(object_id)
    return render_template("view_comments.html", comments=comments, object_id=object_id)

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




# --- Инициализация приложения ---
if __name__ == "__main__":
    initialize_database()
    app.run(debug=True)
