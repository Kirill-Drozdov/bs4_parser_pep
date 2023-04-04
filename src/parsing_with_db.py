# Импортируйте все нужные библиотеки.
import requests
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import Session, declared_attr, declarative_base
from bs4 import BeautifulSoup

PEP_URL = 'https://peps.python.org/'


class Base:

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)


Base = declarative_base(cls=Base)


class Pep(Base):
    type_status = Column(String(2))
    number = Column(Integer, unique=True)
    title = Column(String(200))
    authors = Column(String(20))

    def __repr__(self):
        return f'PEP {self.type_status} {self.number}'


engine = create_engine('sqlite:///sqlite.db')

# Ваш код - здесь:
# создайте таблицу в БД;
# загрузите страницу PEP_URL;
# создайте объект BeautifulSoup;
# спарсите таблицу построчно и запишите данные в БД.

Base.metadata.create_all(engine)
session = Session(engine)

response = requests.get(PEP_URL)
soup = BeautifulSoup(response.text, features='lxml')

numerical_index = soup.find('section', attrs={'id': 'numerical-index'})

tbody_tag = numerical_index.find('tbody')

tr_tags = tbody_tag.find_all('tr')

for tr in tr_tags:
    # preview_status = tr.find('abbr').text
    # print(preview_status)
    td_tags = tr.find_all('td')
    tr_status = td_tags[0].text
    tr_number = td_tags[1].text
    tr_title = td_tags[2].text
    tr_authors = td_tags[3].text
    pep = Pep(
        type_status=tr_status,
        number=tr_number,
        title=tr_title,
        authors=tr_authors
    )
    session.add(pep)
    session.commit()
