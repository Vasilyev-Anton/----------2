import sqlalchemy as sq
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy_utils import database_exists, create_database

Base = declarative_base()
engine = sq.create_engine('postgresql://postgres:314159W@localhost:5432/VkDb', client_encoding='utf8')
Session = sessionmaker(bind=engine)

if not database_exists(engine.url):
    create_database(engine.url)


class User(Base):
    __tablename__ = 'user'
    id = sq.Column(sq.Integer, primary_key=True)
    user = sq.Column(sq.Integer)
    partners = relationship('Partner', backref='user')


class Partner(Base):
    __tablename__ = 'partner'
    id = sq.Column(sq.Integer, primary_key=True)
    partner = sq.Column(sq.Integer)
    user_id = sq.Column(sq.Integer, sq.ForeignKey('user.id'))

    @classmethod
    def get_all(cls):
        session = Session()
        return session.query(cls).all()


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    print('Finish')
