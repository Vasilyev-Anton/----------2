import sqlalchemy as sq
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy_utils import database_exists, create_database

from Vk_Db import User, Partner

Base = declarative_base()
engine = sq.create_engine('postgresql+psycopg2://postgres:314159W@localhost:5432/Vkinder', client_encoding='utf8')
Session = sessionmaker(bind=engine)
session = Session()


def add_user_to_db(user_id):
    current_user = session.query(User).filter_by(user=user_id).first()
    if user_id not in current_user:
        new_user = User(user=user_id)
        session.add(new_user)
        session.commit()


def add_partner_to_db(owner_id, user_id):
    current_partner = session.query(Partner).filter_by(partner=owner_id).first()
    if current_partner:
        return current_partner
    new_partner = Partner(partner=owner_id, user=user_id)
    session.add(new_partner)
    session.commit()

#
# def find_id_in_db(ids):
#     pass


if __name__ == '__main__':
    add_user_to_db(12233)
    # current_user = User(user=12233)

    # add_partner_to_db(12345, 12)
    print('Finish')
