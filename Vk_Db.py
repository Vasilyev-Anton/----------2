import sqlalchemy as sq
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database

Base = declarative_base()
engine = sq.create_engine('postgresql://postgres:314159W@localhost:5432/VkDb', client_encoding='utf8')
Session = sessionmaker(bind=engine)
session = Session()

if not database_exists(engine.url):
    create_database(engine.url)


class Partner(Base):
    __tablename__ = 'partner'
    id = sq.Column(sq.Integer, primary_key=True)
    partner = sq.Column(sq.Integer)
    user = sq.Column(sq.Integer)


def add_partner_to_db(owner_id, user_id):
    current_partner = session.query(Partner).filter_by(partner=owner_id, user=user_id).first()
    if current_partner:
        return True
    new_partner = Partner(partner=owner_id, user=user_id)
    session.add(new_partner)
    session.commit()
