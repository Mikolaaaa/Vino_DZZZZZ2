from active_record import (
    Material, ConstructionObject, Comment,
    Workforce, PurchaseRequest, ReserveEstimate, Supplier, User)


class MaterialTable:
    @staticmethod
    def get_all():
        return Material.get_all()

    @staticmethod
    def get_by_id(material_id):
        return Material.get_by_id(material_id)

    @staticmethod
    def save(name, quantity, price, manufacturer, supplier_id):
        materials = Material(name=name, quantity=quantity, price=price, manufacturer=manufacturer, supplier_id=supplier_id)
        materials.save()

    @staticmethod
    def delete(material_id):
        material = Material.get_by_id(material_id)
        material.delete()

    @staticmethod
    def calculate_total_cost():
        """Вычисляет общую стоимость всех материалов."""
        materials = Material.get_all()
        return sum(material.price * material.quantity for material in materials)


class ConstructionObjectTable:
    @staticmethod
    def get_all():
        return ConstructionObject.get_all()

    @staticmethod
    def get_by_id(object_id):
        return ConstructionObject.get_by_id(object_id)

    @staticmethod
    def save(name, address, deadline):
        con_obj = ConstructionObject(name=name, address=address, deadline=deadline, status="Ожидает")
        con_obj.save()

    @staticmethod
    def update(object_id, new_status):
        con_obj = ConstructionObject.get_by_id(object_id)
        if not con_obj:
            return None
        con_obj.status = new_status
        con_obj.save()

    @staticmethod
    def delete(object_id):
        con_obj = ConstructionObject.get_by_id(object_id)
        con_obj.delete()

    @staticmethod
    def find_overdue_objects(current_date):
        """Находит объекты с просроченным сроком."""
        objects = ConstructionObject.get_all()
        return [obj for obj in objects if obj.deadline < current_date]

    @staticmethod
    def find_active_objects(current_date):
        """Находит объекты с активным сроком."""
        objects = ConstructionObject.get_all()
        return [obj for obj in objects if obj.deadline >= current_date]


class ReserveEstimateTable:
    @staticmethod
    def get_all():
        return ReserveEstimate.get_all()

    @staticmethod
    def get_by_id(object_id):
        return ReserveEstimate.get_by_id(object_id)

    @staticmethod
    def save(
            name, quantity, price, construction_object_id,
            supplier_id, missing_material, missing_quantity,
            total_cost
    ):
        res_est = ReserveEstimate(
            name=name, quantity=quantity, price=price, construction_object_id=construction_object_id,
            supplier_id=supplier_id, missing_material=missing_material, missing_quantity=missing_quantity,
            total_cost=total_cost
        )
        res_est.save()


class WorkforceTable:
    @staticmethod
    def get_all():
        return Workforce.get_all()

    @staticmethod
    def get_by_id(object_id):
        return Workforce.get_by_id(object_id)

    @staticmethod
    def save(object_id, kval, workers, start_date, end_date):
        work = Workforce(object_id=object_id, kval=kval, workers=workers, start_date=start_date, end_date=end_date)
        work.save()

    @staticmethod
    def count_total_workers(object_id):
        """Вычисляет общее количество рабочих для объекта."""
        workforce_list = Workforce.get_all()
        return sum(workforce.workers for workforce in workforce_list if workforce.object_id == object_id)


class SupplierTable:

    @staticmethod
    def get_all():
        return Supplier.get_all()

    @staticmethod
    def get_by_id(workforce_id):
        return Supplier.get_by_id(workforce_id)

    @staticmethod
    def delete(supplier_id):
        supplier = Supplier.get_by_id(supplier_id)
        supplier.delete()

    @staticmethod
    def save(name, address, contact_info, type_of_materials):
        sup = Supplier(name=name, address=address, contact_info=contact_info, type_of_materials=type_of_materials)
        sup.save()

    @staticmethod
    def count_suppliers():
        """Подсчитывает общее количество поставщиков."""
        suppliers = Supplier.get_all()
        return len(suppliers)


class CommentTable:

    @staticmethod
    def get_by_id(object_id):
        return Comment.get_by_id(object_id)

    @staticmethod
    def save(object_id, user, text):
        com = Comment(object_id=object_id, user=user, text=text)
        com.save()


class UserTable:

    @staticmethod
    def get_by_id(user_id):
        return User.get_by_id(user_id)

    @staticmethod
    def get_by_username(username):
        return User.get_by_username(username)


class PurchaseRequestTable:

    @staticmethod
    def get_all():
        return PurchaseRequest.get_all()

    @staticmethod
    def get_by_id(request_id):
        return PurchaseRequest.get_by_id(request_id)

    @staticmethod
    def material(request):
        PurchaseRequest.material(request)
        return MaterialTable.get_by_id(request)

    @staticmethod
    def save(material, quantity, price, supplier_id, status, request_date):
        pur_req = PurchaseRequest(material=material, quantity=quantity, price=price,
                                  supplier_id=supplier_id, status=status, request_date=request_date)
        pur_req.save()

    @staticmethod
    def update(request_id, new_status):
        pur_req = PurchaseRequest.get_by_id(request_id)
        if not pur_req:
            return None
        pur_req.status = new_status
        pur_req.save()
