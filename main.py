from datetime import datetime

from flask import Flask, request, jsonify, render_template, redirect, url_for
import sqlite3
from flask_login import login_required, login_user, logout_user, LoginManager, current_user
from init_db import initialize_database
from data import ConstructionObject, ReserveEstimate, Estimate, Comment, Workforce, Supplier, Material, User, \
    PurchaseRequest
from flask import flash

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
    objects = ConstructionObject.all()
    return render_template("index.html", objects=objects)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.find_by_username(username)
        if user and user.password == password:  # Здесь можно заменить на bcrypt
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
    return User.find_by_id(user_id)  # Убедитесь, что метод `find_by_id` существует в классе `User`.


@app.route("/add", methods=["GET", "POST"])
@login_required
def add_object():
    if request.method == "POST":
        name = request.form["name"]
        address = request.form["address"]
        deadline = request.form["deadline"]
        obj = ConstructionObject(name=name, address=address, deadline=deadline)
        obj.save()
        return redirect(url_for("index"))
    return render_template("add_object.html")


@app.route("/update_status/<int:object_id>", methods=["POST"])
@login_required
def update_status(object_id):
    obj = ConstructionObject.find(object_id)
    if obj:
        new_status = request.form.get("status")  # Получаем новый статус
        obj.status = new_status  # Обновляем статус объекта
        obj.save()  # Сохраняем изменения
        flash(f"Статус объекта {obj.name} успешно обновлен на {new_status}.", "success")
    else:
        flash("Объект не найден.", "danger")
    return redirect(url_for("index"))


@app.route('/delete_object/<int:object_id>', methods=['GET', 'POST'])
@login_required
def delete_object(object_id):
    # Найти объект в базе данных по ID
    obj = ConstructionObject.find(object_id)

    if obj:
        obj.delete()  # Удалить объект

    return redirect(url_for('index'))  # Перенаправить на главную страницу


@app.route("/api/objects", methods=["GET"])
@login_required
def get_objects():
    objects = [vars(obj) for obj in ConstructionObject.all()]
    return jsonify(objects)


@app.route("/estimate/<int:object_id>", methods=["GET", "POST"])
@login_required
def manage_estimate(object_id):
    estimate = Estimate.find_by_object(object_id)
    obj = ConstructionObject.find(object_id)
    materials = Material.all()  # Получаем все материалы для объекта

    # Создаем словарь "id: name-quantity-price"
    material_options = {}
    for material in materials:
        material_options[material.id] = f"{material.name} - {material.quantity} кг - {material.price} руб/кг"

    total_cost = 0
    if estimate:
        for material_id in estimate.materials:
            material = Material.find(material_id)
            if material:
                total_cost += material.price * material.quantity

    if estimate and estimate.material_type:
        # Преобразуем значения в целые числа
        estimate.material_type = list(map(str, estimate.material_type))

    if request.method == "POST":
        material_ids = request.form.getlist("materials")  # Получаем выбранные материалы
        labor_hours = int(request.form["labor_hours"])
        total_cost = float(request.form["total_cost"])
        material_type_ids = request.form.getlist("material_type[]")  # Получаем выбранные id материалов
        print(f"material_type_ids: {material_type_ids}")

        # Пересчитываем итоговую стоимость
        total_cost = 0
        missing_materials = []  # Список для недостающих материалов

        for material_id in material_ids:
            material = Material.find(material_id)
            quantity = int(request.form.get(f"material_quantity_{material_id}", 0))  # Получаем количество для каждого материала
            if material:
                if quantity > material.quantity:
                    missing_materials.append((material.name, quantity - material.quantity))  # Добавляем недостающий материал
                    total_cost += material.price * material.quantity  # Платим только за доступное количество
                else:
                    total_cost += material.price * quantity  # Пересчитываем стоимость с учетом количества

        # Сохраняем в reserve_estimates с учетом недостающих материалов
        for material_id in material_ids:
            material = Material.find(material_id)
            quantity = int(request.form.get(f"material_quantity_{material_id}", 0))

            reserve_estimate = ReserveEstimate(
                name=material.name,
                quantity=quantity,
                price=material.price,
                construction_object_id=object_id,
                supplier_id=material.supplier_id,
                missing_material=', '.join([m[0] for m in missing_materials]) if missing_materials else None,
                missing_quantity=sum([m[1] for m in missing_materials]) if missing_materials else 0,
                total_cost=total_cost
            )
            reserve_estimate.save()

        # Обновляем или сохраняем estimate
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
@login_required
def comments(object_id):
    obj = ConstructionObject.find(object_id)

    if request.method == "POST":
        user = current_user.desc
        text = request.form["text"]
        comment = Comment(object_id=object_id, user=user, text=text)
        comment.save()
        return redirect(url_for("comments", object_id=object_id))
    comments = Comment.find_by_object(object_id)
    return render_template("comments.html", obj=obj, comments=comments)

@app.route("/workforce/<int:object_id>", methods=["GET", "POST"])
@login_required
def manage_workforce(object_id):
    obj = ConstructionObject.find(object_id)
    workforces = Workforce.find_all_by_object(object_id)  # Получаем все бригады для объекта

    if request.method == "POST":
        kval = request.form["kval"]
        workers = int(request.form["workers"])
        start_date = request.form["start_date"]
        end_date = request.form["end_date"]

        workforce = Workforce(object_id=object_id, kval=kval, workers=workers, start_date=start_date, end_date=end_date)
        workforce.save()  # Добавляем новую бригаду
        return redirect(url_for("manage_workforce", object_id=object_id))

    return render_template("manage_workforce.html", obj=obj, workforces=workforces)



@app.route("/suppliers", methods=["GET", "POST"])
@login_required
def manage_suppliers():
    if request.method == "POST":
        print(request)
        name = request.form["name"]
        contact_info = request.form["contact_info"]
        type_of_materials = request.form["type_of_materials"]
        address = request.form["address"]
        print(111111)
        print(name, address, contact_info, type_of_materials)
        supplier = Supplier(name=name, address=address, contact_info=contact_info, type_of_materials=type_of_materials)
        supplier.save()
        return redirect(url_for("manage_suppliers"))

    suppliers = Supplier.all()
    return render_template("manage_suppliers.html", suppliers=suppliers)


@app.route("/supplier/<int:supplier_id>", methods=["GET", "POST", "DELETE"])
@login_required
def manage_supplier(supplier_id):
    supplier = Supplier.find(supplier_id)
    if not supplier:
        return "Поставщик не найден", 404

    if request.method == "POST":
        if request.form.get('_method') == 'DELETE':
            supplier.delete()
            flash("Поставщик успешно удален!", "success")
            return redirect(url_for("manage_suppliers"))
        supplier.name = request.form["name"]
        supplier.contact_info = request.form["contact_info"]
        supplier.type_of_materials = request.form["type_of_materials"]
        supplier.address = request.form["address"]
        supplier.save()
        return redirect(url_for("manage_suppliers"))

    if request.method == "DELETE":
        supplier.delete()
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
        material = Material(name=name, quantity=quantity, price=price, manufacturer=manufacturer,
                            supplier_id=supplier_id)
        material.save()
        return redirect(url_for("manage_materials"))

    materials = Material.all()
    return render_template("manage_materials.html", materials=materials)


@app.route("/material/<int:material_id>", methods=["GET", "POST", "DELETE"])
@login_required
def manage_material(material_id):
    material = Material.find(material_id)
    if not material:
        return "Материал не найден", 404

    if request.method == "POST":
        material.name = request.form["name"]
        material.quantity = int(request.form["quantity"])
        material.price = float(request.form["price"])
        material.manufacturer = str(request.form["manufacturer"])
        material.supplier_id = int(request.form["supplier_id"])
        material.save()
        return redirect(url_for("manage_materials"))

    if request.method == "DELETE":
        material.delete()
        return redirect(url_for("manage_materials"))

    return render_template("manage_material.html", material=material)


@app.route("/purchase_requests", methods=["GET", "POST"])
@login_required
def purchase_requests():
    materials = Material.all()
    if request.method == "POST":
        material_id = int(request.form["material_id"])
        quantity = int(request.form["quantity"])
        status = request.form["status"]
        request_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        purchase_request = PurchaseRequest(material_id=material_id, quantity=quantity, status=status, request_date=request_date)
        purchase_request.save()
        flash("Запрос на закупку материала создан!", "success")
        return redirect(url_for("purchase_requests"))

    purchase_requests = PurchaseRequest.all()
    return render_template("purchase_requests.html", materials=materials, purchase_requests=purchase_requests)


@app.route("/update_purchase_request/<int:request_id>", methods=["GET", "POST"])
@login_required
def update_purchase_request(request_id):
    # Получаем запрос на закупку по ID
    purchase_request = PurchaseRequest.find(request_id)

    if purchase_request is None:
        return "Запрос не найден", 404

    if request.method == "POST":
        # Обновляем статус запроса
        status = request.form["status"]
        purchase_request.status = status
        purchase_request.save()  # Метод save должен сохранять обновления в базе данных

        flash("Статус запроса обновлен!", "success")
        return redirect(url_for('purchase_requests'))  # Перенаправляем на страницу запросов

    # Если GET-запрос, отображаем форму
    return render_template("purchase_requests.html", purchase_request=purchase_request)


# --- Инициализация приложения ---
if __name__ == "__main__":
    initialize_database()
    app.run(debug=True)
