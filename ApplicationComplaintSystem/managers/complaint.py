from werkzeug.exceptions import NotFound

from managers.auth import auth
from models.complaint import ComplaintModel
from models.enums import State
from db import db


class ComplaintManager:
    @staticmethod
    def get_all():
        return ComplaintModel.query.all()

    @staticmethod
    def create(complaint_data, complainer_id):
        complaint_data['complainer_id'] = complainer_id
        complaint = ComplaintModel(**complaint_data)
        db.session.add(complaint)
        db.session.commit()
        return complaint

    @staticmethod
    def update(complaint_data, id_):
        complaint_q = ComplaintModel.query.filter_by(id=id_)
        complaint = complaint_q.first()
        if not complaint:
            raise NotFound('This complaint does not exist')
        user = auth.current_user()

        if not user.id == complaint.complainer_id:
            raise NotFound('This complaint does not exist')

        complaint_q.update(complaint_data)
        db.session.add(complaint)
        db.session.commit()
        return complaint

    @staticmethod
    def delete(id_):
        complaint_q = ComplaintModel.query.filter_by(id=id_)
        complaint = complaint_q.first()

        if not complaint:
            raise NotFound('This complaint does not exist')

        db.session.delete(complaint)
        db.session.commit()

    @staticmethod
    def approve(id_):
        complaint_q = ComplaintModel.query.filter_by(id=id_)
        complaint = complaint_q.first()

        if not complaint:
            raise NotFound('This complaint does not exist')

        complaint_q.update({'status': State.approved})
        db.session.add(complaint)
        db.session.commit()
        return complaint

    @staticmethod
    def reject(id_):
        complaint_q = ComplaintModel.query.filter_by(id=id_)
        complaint = complaint_q.first()

        if not complaint:
            raise NotFound('This complaint does not exist')

        complaint_q.update({'status': State.rejected})
        db.session.add(complaint)
        db.session.commit()
        return complaint
