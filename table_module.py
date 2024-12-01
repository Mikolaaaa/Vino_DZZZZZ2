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
    def filter_by_name(name):
        materials = Material.get_all()
        return [material for material in materials if name.lower() in material.name.lower()]

    @staticmethod
    def save(name, quantity, price, manufacturer, supplier_id):
        mat = Material(name=name, quantity=quantity, price=price, manufacturer=manufacturer, supplier_id=supplier_id)
        mat.save()

    @staticmethod
    def delete(material_id):
        Material.delete(material_id)


class ConstructionObjectTable:
    @staticmethod
    def get_all():
        return ConstructionObject.get_all()

    @staticmethod
    def get_by_id(object_id):
        return ConstructionObject.get_by_id(object_id)

    @staticmethod
    def filter_by_status(status):
        objects = ConstructionObject.get_all()
        return [obj for obj in objects if obj.status.lower() == status.lower()]

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
        ConstructionObject.delete(object_id)


class ReserveEstimateTable:
    @staticmethod
    def get_all():
        return ReserveEstimate.get_all()

    @staticmethod
    def get_by_id(object_id):
        return ReserveEstimate.get_by_id(object_id)

    @staticmethod
    def filter_by_object(construction_object_id):
        reserves = ReserveEstimate.get_all()
        return [reserve for reserve in reserves if reserve.construction_object_id == construction_object_id]

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

    @staticmethod
    def delete_all(estimate_id):
        ReserveEstimate.delete(estimate_id)


class WorkforceTable:
    @staticmethod
    def get_all():
        return Workforce.get_all()

    @staticmethod
    def get_by_id(object_id):
        return Workforce.get_by_id(object_id)

    @staticmethod
    def filter_by_object(object_id):
        workforce_list = Workforce.get_all()
        return [workforce for workforce in workforce_list if workforce.object_id == object_id]

    @staticmethod
    def delete(workforce_id):
        Workforce.delete(workforce_id)

    @staticmethod
    def save(object_id, kval, workers, start_date, end_date):
        work = Workforce(object_id=object_id, kval=kval, workers=workers, start_date=start_date, end_date=end_date)
        work.save()


class SupplierTable:

    @staticmethod
    def get_all():
        return Supplier.get_all()

    @staticmethod
    def get_by_id(workforce_id):
        return Supplier.get_by_id(workforce_id)

    @staticmethod
    def filter_by_object(object_id):
        supplier_list = Supplier.get_all()
        return [supplier for supplier in supplier_list if supplier.object_id == object_id]

    @staticmethod
    def delete(supplier_id):
        Supplier.delete(supplier_id)

    @staticmethod
    def save(name, address, contact_info, type_of_materials):
        sup = Supplier(name=name, address=address, contact_info=contact_info, type_of_materials=type_of_materials)
        sup.save()


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
    def delete(request_id):
        PurchaseRequest.delete(request_id)

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
