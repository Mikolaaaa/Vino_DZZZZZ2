from data import (ConstructionObject, Comment, Workforce, Material,
                  Estimate, ReserveEstimate, PurchaseRequest, Supplier, User)


class ConstructionObjectGateway:
    @staticmethod
    def get_all_objects():
        """Получить все объекты строительства."""
        return ConstructionObject.all()

    @staticmethod
    def get_object_by_id(object_id):
        """Найти объект по ID."""
        return ConstructionObject.find(object_id)

    @staticmethod
    def create_object(name, address, deadline):
        """Создать новый объект строительства."""
        obj = ConstructionObject(name=name, address=address, deadline=deadline)
        obj.save()
        return obj

    @staticmethod
    def update_object_status(object_id, new_status):
        """Обновить статус объекта строительства."""
        obj = ConstructionObject.find(object_id)
        if not obj:
            return None
        obj.status = new_status
        obj.save()
        return obj

    @staticmethod
    def delete_object(object_id):
        """Удалить объект строительства."""
        obj = ConstructionObject.find(object_id)
        if obj:
            obj.delete()
        return obj


class MaterialGateway:
    @staticmethod
    def get_all_materials():
        """Получить все материалы."""
        return Material.all()

    @staticmethod
    def get_material_by_id(material_id):
        """Найти материал по ID."""
        return Material.find(material_id)

    @staticmethod
    def create_material(name, quantity, price, manufacturer, supplier_id):
        """Создать новый материал."""
        material = Material(
            name=name,
            quantity=quantity,
            price=price,
            manufacturer=manufacturer,
            supplier_id=supplier_id
        )
        material.save()
        return material

    @staticmethod
    def update_material(material_id, name, quantity, price, manufacturer, supplier_id):
        """Обновить информацию о материале."""
        material = Material.find(material_id)
        if not material:
            return None
        material.name = name
        material.quantity = quantity
        material.price = price
        material.manufacturer = manufacturer
        material.supplier_id = supplier_id
        material.save()
        return material

    @staticmethod
    def delete_material(material_id):
        """Удалить материал."""
        material = Material.find(material_id)
        if material:
            material.delete()
        return material


class ReserveEstimateGateway:
    #@staticmethod
    #def get_all_reserve_estimates():
    #    """Получить все резервные сметы."""
    #    return ReserveEstimate.all()

    @staticmethod
    def get_reserve_estimate_by_id(estimate_id):
        """Найти резервную смету по ID."""
        return ReserveEstimate.find_by_object(estimate_id)

    @staticmethod
    def create_reserve_estimate(name, quantity, price, construction_object_id, supplier_id, missing_material, missing_quantity, total_cost):
        """Создать резервную смету."""
        reserve_estimate = ReserveEstimate(
            name=name,
            quantity=quantity,
            price=price,
            construction_object_id=construction_object_id,
            supplier_id=supplier_id,
            missing_material=missing_material,
            missing_quantity=missing_quantity,
            total_cost=total_cost
        )
        reserve_estimate.save()
        return reserve_estimate

    @staticmethod
    def update_reserve_estimate(estimate_id, name, quantity, price, construction_object_id, supplier_id, missing_material, missing_quantity, total_cost):
        """Обновить резервную смету."""
        reserve_estimate = ReserveEstimate.find_by_object(estimate_id)
        if not reserve_estimate:
            return None
        reserve_estimate.name = name
        reserve_estimate.quantity = quantity
        reserve_estimate.price = price
        reserve_estimate.construction_object_id = construction_object_id
        reserve_estimate.supplier_id = supplier_id
        reserve_estimate.missing_material = missing_material
        reserve_estimate.missing_quantity = missing_quantity
        reserve_estimate.total_cost = total_cost
        reserve_estimate.save()
        return reserve_estimate

    @staticmethod
    def delete_reserve_estimate(estimate_id):
        """Удалить резервную смету."""
        reserve_estimate = ReserveEstimate.find_by_object(estimate_id)
        if reserve_estimate:
            reserve_estimate.delete()
        return reserve_estimate


class EstimateGateway:
    #@staticmethod
    #def get_all_estimates():
    #    """Получить все сметы."""
    #    return Estimate.all()

    @staticmethod
    def get_estimate_by_id(estimate_id):
        """Найти смету по ID."""
        return Estimate.find_by_object(estimate_id)

    @staticmethod
    def get_estimate_by_object(object_id):
        """Найти смету по объекту строительства."""
        return Estimate.find_by_object(object_id)

    @staticmethod
    def create_estimate(object_id, materials, labor_hours, total_cost, material_type):
        """Создать новую смету."""
        estimate = Estimate(
            object_id=object_id,
            materials=materials,
            labor_hours=labor_hours,
            total_cost=total_cost,
            material_type=material_type
        )
        estimate.save()
        return estimate

    @staticmethod
    def update_estimate(estimate_id, materials, labor_hours, total_cost, material_type):
        """Обновить смету."""
        estimate = Estimate.find_by_object(estimate_id)
        if not estimate:
            return None
        estimate.materials = materials
        estimate.labor_hours = labor_hours
        estimate.total_cost = total_cost
        estimate.material_type = material_type
        estimate.save()
        return estimate

    @staticmethod
    def delete_estimate(estimate_id):
        """Удалить смету."""
        estimate = Estimate.find_by_object(estimate_id)
        if estimate:
            estimate.delete()
        return estimate


class CommentGateway:

    @staticmethod
    def get_comments_by_object(object_id):
        """Получить комментарии для объекта."""
        return Comment.find_by_object(object_id)

    @staticmethod
    def create_comment(object_id, user, text):
        """Создать новый комментарий."""
        comment = Comment(object_id=object_id, user=user, text=text)
        comment.save()
        return comment

    @staticmethod
    def delete_comment(comment_id):
        """Удалить комментарий."""
        comment = Comment.find_by_object(comment_id)
        if comment:
            comment.delete()
        return comment


class WorkforceGateway:

    @staticmethod
    def get_workforce_by_object(object_id):
        """Получить рабочие бригады для объекта."""
        return Workforce.find_all_by_object(object_id)

    @staticmethod
    def create_workforce(object_id, kval, workers, start_date, end_date):
        """Создать новую рабочую бригаду."""
        workforce = Workforce(object_id=object_id, kval=kval, workers=workers, start_date=start_date, end_date=end_date)
        workforce.save()
        return workforce

    @staticmethod
    def update_workforce(workforce_id, kval, workers, start_date, end_date):
        """Обновить информацию о рабочей бригаде."""
        workforce = Workforce.find_by_object(workforce_id)
        if not workforce:
            return None
        workforce.kval = kval
        workforce.workers = workers
        workforce.start_date = start_date
        workforce.end_date = end_date
        workforce.save()
        return workforce

    @staticmethod
    def delete_workforce(workforce_id):
        """Удалить рабочую бригаду."""
        workforce = Workforce.find_by_object(workforce_id)
        if workforce:
            workforce.delete()
        return workforce


class SupplierGateway:
    @staticmethod
    def get_all_suppliers():
        """Получить всех поставщиков."""
        return Supplier.all()

    @staticmethod
    def get_supplier_by_id(supplier_id):
        """Найти поставщика по ID."""
        return Supplier.find(supplier_id)

    @staticmethod
    def create_supplier(name, address, contact_info, type_of_materials):
        """Создать нового поставщика."""
        supplier = Supplier(
            name=name,
            address=address,
            contact_info=contact_info,
            type_of_materials=type_of_materials
        )
        supplier.save()
        return supplier

    @staticmethod
    def update_supplier(supplier_id, name, address, contact_info, type_of_materials):
        """Обновить информацию о поставщике."""
        supplier = Supplier.find(supplier_id)
        if not supplier:
            return None
        supplier.name = name
        supplier.address = address
        supplier.contact_info = contact_info
        supplier.type_of_materials = type_of_materials
        supplier.save()
        return supplier

    @staticmethod
    def delete_supplier(supplier_id):
        """Удалить поставщика."""
        supplier = Supplier.find(supplier_id)
        if supplier:
            supplier.delete()
        return supplier


class PurchaseRequestGateway:
    @staticmethod
    def get_all_purchase_requests():
        """Получить все запросы на закупку."""
        return PurchaseRequest.all()

    @staticmethod
    def get_purchase_request_by_id(request_id):
        """Найти запрос на закупку по ID."""
        return PurchaseRequest.find(request_id)

    @staticmethod
    def create_purchase_request(material, quantity, price, supplier_id,status, request_date):
        """Создать запрос на закупку."""
        purchase_request = PurchaseRequest(
            material=material,
            quantity=quantity,
            price=price,
            supplier_id=supplier_id,
            status=status,
            request_date=request_date
        )
        purchase_request.save()
        return purchase_request

    @staticmethod
    def update_purchase_request(request_id, status):
        """Обновить статус запроса на закупку."""
        purchase_request = PurchaseRequest.find(request_id)
        if not purchase_request:
            return None
        purchase_request.status = status
        purchase_request.save()
        return purchase_request

    @staticmethod
    def delete_purchase_request(request_id):
        """Удалить запрос на закупку."""
        purchase_request = PurchaseRequest.find(request_id)
        if purchase_request:
            purchase_request.delete()
        return purchase_request


class UserGateway:
    @staticmethod
    def find_by_id(user_id):
        return User.find_by_id(user_id)

    @staticmethod
    def find_by_username(username):
        return User.find_by_username(username)
