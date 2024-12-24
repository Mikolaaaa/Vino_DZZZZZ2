from datetime import datetime

from flask import Flask, request, jsonify, render_template, redirect, url_for
import sqlite3
from flask_login import login_required, login_user, logout_user, LoginManager, current_user
from init_db import initialize_database
from flask import flash
from table_module import (
    CommentTable, PurchaseRequestTable, SupplierTable, PurchaseRequestTable,
    WorkforceTable, ReserveEstimateTable, ConstructionObjectTable, UserTable, MaterialTable,
)

app = Flask(__name__)
app.secret_key = "supersecretkey"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # Страница для входа
login_manager.login_message = "Пожалуйста, войдите, чтобы продолжить."


# --- API и Роуты ---
@app.route("/")
@login_required
def index():
    print(str(datetime.now().strftime("%Y-%m-%d")))
    objects = ConstructionObjectTable.find_active_objects(str(datetime.now().strftime("%Y-%m-%d")))
    end = ConstructionObjectTable.find_overdue_objects(str(datetime.now().strftime("%Y-%m-%d")))
    return render_template("index.html", objects=objects, end=end)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        print(f"username {username}")

        user = UserTable.get_by_username(username)
        print(f"Found user: {user}")
        if user and user.password == password:
            login_user(user)
            flash("Вы успешно вошли в систему.", "success")
            return redirect(url_for("index"))
        else:
            flash("Неправильное имя пользователя или пароль.", "danger")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Вы вышли из системы.", "info")
    return redirect(url_for("login"))


@login_manager.user_loader
def load_user(user_id):
    return UserTable.get_by_id(user_id)


@app.route("/add", methods=["GET", "POST"])
@login_required
def add_object():
    if request.method == "POST":
        name = request.form["name"]
        address = request.form["address"]
        deadline = request.form["deadline"]
        ConstructionObjectTable.save(name, address, deadline)
        return redirect(url_for("index"))
    return render_template("add_object.html")


@app.route("/update_status/<int:object_id>", methods=["POST"])
@login_required
def update_status(object_id):
    obj = ConstructionObjectTable.get_by_id(object_id)
    if obj:
        new_status = request.form.get("status")  # Получаем новый статус
        ConstructionObjectTable.update(object_id, new_status)
        flash(f"Статус объекта {obj.name} успешно обновлен на {new_status}.", "success")
    else:
        flash("Объект не найден.", "danger")
    return redirect(url_for("index"))


@app.route('/delete_object/<int:object_id>', methods=['GET', 'POST'])
@login_required
def delete_object(object_id):
    # Найти объект в базе данных по ID
    obj = ConstructionObjectTable.get_by_id(object_id)

    if obj:
        ConstructionObjectTable.delete(object_id)  # Удалить объект

    return redirect(url_for('index'))  # Перенаправить на главную страницу

@app.route("/api/objects", methods=["GET"])
@login_required
def get_objects():
    objects = [vars(obj) for obj in ConstructionObjectTable.get_all()]
    return jsonify(objects)


@app.route("/estimate/<int:object_id>", methods=["GET", "POST"])
@login_required
def manage_estimate(object_id):
    obj = ConstructionObjectTable.get_by_id(object_id)
    materials = MaterialTable.get_all()  # Получаем все материалы
    reserve_estimates = ReserveEstimateTable.get_by_id(object_id)  # Резервные материалы
    print(f"reserve_estimates {reserve_estimates}")

    # Вычисление оставшихся материалов
    remaining_materials = {}
    for material in materials:
        reserved_quantity = sum(
            res.quantity for res in reserve_estimates if res.name == material.name
        )
        remaining_materials[material.id] = material.quantity - reserved_quantity

    # Итоговая стоимость резервов
    total_reserve_cost = sum(
        res.quantity * res.price for res in reserve_estimates
    )

    if request.method == "POST":
        # Получаем данные из формы
        material_ids = request.form.getlist("materials")  # Получаем список материалов
        material_quantities = request.form.getlist("material_quantity")  # Получаем список количеств материалов

        print(f"material_ids {material_ids}")
        print(f"material_quantities {material_quantities}")

        # Обработка каждого материала
        for material_id, material_quantity in zip(material_ids, material_quantities):
            material_id = int(material_id)  # Преобразуем ID в integer
            material_quantity = int(material_quantity)  # Преобразуем количество в integer

            # Получаем материал из базы
            mat = MaterialTable.get_by_id(material_id)

            if material_id and material_quantity > 0:
                # Обновляем или добавляем резервный материал
                ReserveEstimateTable.save(
                    name=mat.name,
                    quantity=material_quantity,
                    price=mat.price,
                    construction_object_id=object_id,
                    supplier_id=mat.supplier_id,
                    missing_material=1,  # Пример, нужно уточнить
                    missing_quantity=1,  # Пример, нужно уточнить
                    total_cost=mat.price * material_quantity  # Пример, расчет стоимости
                )

        # Перенаправление обратно на страницу
        return redirect(url_for("manage_estimate", object_id=object_id))

    materials1 = MaterialTable.filter_by_price_range(1, 15)
    print(materials1)

    return render_template(
        "manage_estimate.html",
        obj=obj,
        materials=materials,
        reserve_estimates=reserve_estimates,
        remaining_materials=remaining_materials,
        total_reserve_cost=total_reserve_cost,
    )


@app.route("/comments/<int:object_id>", methods=["GET", "POST"])
@login_required
def comments(object_id):
    obj = ConstructionObjectTable.get_by_id(object_id)

    if request.method == "POST":
        user = current_user.desc
        text = request.form["text"]
        CommentTable.save(object_id=object_id, user=user, text=text)
        return redirect(url_for("comments", object_id=object_id))
    comments = CommentTable.get_by_id(object_id)
    return render_template("comments.html", obj=obj, comments=comments)


@app.route("/workforce/<int:object_id>", methods=["GET", "POST"])
@login_required
def manage_workforce(object_id):
    obj = ConstructionObjectTable.get_by_id(object_id)
    workforces = WorkforceTable.get_by_id(object_id)  # Получаем все бригады для объекта

    if request.method == "POST":
        kval = request.form["kval"]
        workers = int(request.form["workers"])
        start_date = request.form["start_date"]
        end_date = request.form["end_date"]

        WorkforceTable.save(object_id=object_id, kval=kval, workers=workers, start_date=start_date, end_date=end_date)
        return redirect(url_for("manage_workforce", object_id=object_id))

    all_worker = WorkforceTable.count_total_workers(object_id)

    return render_template("manage_workforce.html", obj=obj, workforces=workforces, all_worker=all_worker)


@app.route("/suppliers", methods=["GET", "POST"])
@login_required
def manage_suppliers():
    if request.method == "POST":
        print(request)
        name = request.form["name"]
        contact_info = request.form["contact_info"]
        type_of_materials = request.form["type_of_materials"]
        address = request.form["address"]
        SupplierTable.save(name=name, address=address, contact_info=contact_info, type_of_materials=type_of_materials)
        return redirect(url_for("manage_suppliers"))

    suppliers = SupplierTable.get_all()
    lens = SupplierTable.count_suppliers()
    return render_template("manage_suppliers.html", suppliers=suppliers, lens=lens)


@app.route("/supplier/<int:supplier_id>", methods=["GET", "POST", "DELETE"])
@login_required
def manage_supplier(supplier_id):
    supplier = SupplierTable.get_by_id(supplier_id)
    if not supplier:
        return "Поставщик не найден", 404

    if request.method == "POST":
        if request.form.get('_method') == 'DELETE':
            SupplierTable.delete(supplier_id)
            flash("Поставщик успешно удален!", "success")
            return redirect(url_for("manage_suppliers"))
        name = request.form["name"]
        contact_info = request.form["contact_info"]
        type_of_materials = request.form["type_of_materials"]
        address = request.form["address"]
        SupplierTable.save(name=name, address=address, contact_info=contact_info, type_of_materials=type_of_materials)
        return redirect(url_for("manage_suppliers"))

    if request.method == "DELETE":
        SupplierTable.delete(supplier_id)
        return redirect(url_for("manage_suppliers"))

    return render_template("manage_supplier.html", supplier=supplier)


@app.route("/materials", methods=["GET", "POST"])
@login_required
def manage_materials():
    if request.method == "POST":
        name = request.form["name"]
        quantity = int(request.form["quantity"])
        price = float(request.form["price"])
        manufacturer = str(request.form["manufacturer"])
        supplier_id = int(request.form["supplier_id"])
        material = MaterialTable.save(name=name, quantity=quantity, price=price, manufacturer=manufacturer,
                            supplier_id=supplier_id)
        return redirect(url_for("manage_materials"))

    materials = MaterialTable.get_all()
    return render_template("manage_materials.html", materials=materials)


@app.route("/material/<int:material_id>", methods=["GET", "POST", "DELETE"])
@login_required
def manage_material(material_id):
    material = MaterialTable.get_by_id(material_id)
    if not material:
        return "Материал не найден", 404

    if request.method == "POST" and request.form.get("_method") == "DELETE":
        request.method = "DELETE"

    if request.method == "POST":
        name = request.form["name"]
        quantity = int(request.form["quantity"])
        price = float(request.form["price"])
        manufacturer = str(request.form["manufacturer"])
        supplier_id = int(request.form["supplier_id"])
        MaterialTable.save(name=name, quantity=quantity, price=price, manufacturer=manufacturer, supplier_id=supplier_id)
        return redirect(url_for("manage_materials"))

    if request.method == "DELETE":
        MaterialTable.delete(material_id)
        return redirect(url_for("manage_materials"))

    return render_template("manage_material.html", material=material)


@app.route("/purchase_requests", methods=["GET", "POST"])
@login_required
def purchase_requests():
    suppliers = SupplierTable.get_all()
    if request.method == "POST":
        try:
            material = request.form["material"]
            quantity = int(request.form["quantity"])
            price = int(request.form["price"])
            supplier_id = int(request.form["supplier_id"])
            status = request.form["status"]
            request_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"material {material} quantity {quantity} price {price} supplier {supplier_id} status {status} request_date: {request_date}")
            PurchaseRequestTable.save(material=material, quantity=quantity, price=price,
                                                           supplier_id=supplier_id, status=status, request_date=request_date)
            flash("Запрос на закупку материала создан!", "success")
            return redirect(url_for("purchase_requests"))
        except ValueError as e:
            flash(f"Ошибка: {str(e)}", "danger")


    purchase_requests = PurchaseRequestTable.get_all()
    return render_template("purchase_requests.html", suppliers=suppliers, purchase_requests=purchase_requests)


@app.route("/update_purchase_request/<int:request_id>", methods=["GET", "POST"])
@login_required
def update_purchase_request(request_id):
    purchase_request = PurchaseRequestTable.get_by_id(request_id)

    if purchase_request is None:
        return "Запрос не найден", 404

    if request.method == "POST":
        # Обновляем статус запроса
        status = request.form["status"]
        qqqqq = purchase_request.supplier_id
        manufacturer = SupplierTable.get_by_id(qqqqq)
        PurchaseRequestTable.update(request_id, status)
        if status == "Закрыт":
            MaterialTable.save(name=purchase_request.material, quantity=purchase_request.quantity,
                               price=purchase_request.price, manufacturer=manufacturer.name,
                               supplier_id=qqqqq)


        flash("Статус запроса обновлен!", "success")
        return redirect(url_for('purchase_requests'))  # Перенаправляем на страницу запросов

    # Если GET-запрос, отображаем форму
    return render_template("purchase_requests.html", purchase_request=purchase_request)


# --- Инициализация приложения ---
if __name__ == "__main__":
    initialize_database()
    app.run(debug=True)
