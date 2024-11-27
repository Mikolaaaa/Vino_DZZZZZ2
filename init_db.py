import sqlite3

DB_PATH = "construction_system2222.db"


# --- Инициализация базы данных ---
def initialize_database():
    with sqlite3.connect(DB_PATH) as conn:
        # Таблица для запросов на закупку материалов
        conn.execute("""
            CREATE TABLE IF NOT EXISTS purchase_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                material TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price INTEGER NOT NULL,
                supplier_id INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'Ожидает',
                request_date TEXT NOT NULL,
                FOREIGN KEY (supplier_id) REFERENCES supplier(id) ON DELETE CASCADE
                    )
                """)
        # Таблица пользователей
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                desc TEXT NOT NULL
                    )
                """)
        # Таблица для поставщиков
        conn.execute("""
            CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                address TEXT,
                contact_info TEXT,
                type_of_materials TEXT
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
                manufacturer TEXT NOT NULL,
                supplier_id INTEGER,
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
                kval TEXT NOT NULL,
                workers INTEGER NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                FOREIGN KEY (object_id) REFERENCES construction_objects (id) ON DELETE CASCADE
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reserve_estimates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                construction_object_id INTEGER,
                supplier_id INTEGER,
                missing_material TEXT,  -- Новое поле для хранения недостающих материалов
                missing_quantity INTEGER DEFAULT 0,  -- Новое поле для недостающего количества
                total_cost REAL NOT NULL,  -- Итоговая стоимость
                FOREIGN KEY (construction_object_id) REFERENCES construction_objects(id) ON DELETE SET NULL,
                FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE SET NULL
            )
        """)

    print("База данных и таблицы инициализированы.")
