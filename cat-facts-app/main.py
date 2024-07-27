import requests
from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class CatFact(Base):
    __tablename__ = 'cat_facts'

    id = Column(String, primary_key=True)
    text = Column(String)
    created_at = Column(String)
    updated_at = Column(String)

    def __repr__(self):
        return f"<CatFact(id='{self.id}', text='{self.text[:30]}...')>"


engine = create_engine('sqlite:///cat_facts.db')
Session = sessionmaker(bind=engine)


def fetch_cat_facts():
    """Fetch cat facts from the API"""
    url = "https://cat-fact.herokuapp.com/facts"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data: Status code {response.status_code}")
        return None


def create_database():
    """Create SQLite database and table"""
    Base.metadata.create_all(engine)


def save_cat_facts(facts):
    """Save cat facts to the database"""
    session = Session()
    for fact in facts:
        cat_fact = CatFact(
            id=fact['_id'],
            text=fact['text'],
            created_at=fact['createdAt'],
            updated_at=fact['updatedAt']
        )
        session.merge(cat_fact)
    session.commit()
    session.close()


def view_cat_facts():
    """View cat facts from the database"""
    session = Session()
    facts = session.query(CatFact).all()
    for fact in facts:
        print(f"ID: {fact.id}")
        print(f"Fact: {fact.text}")
        print(f"Created at: {fact.created_at}")
        print(f"Updated at: {fact.updated_at}")
        print("-" * 50)
    session.close()


def main():
    cat_facts = fetch_cat_facts()
    if not cat_facts:
        return

    create_database()

    save_cat_facts(cat_facts)

    view_cat_facts()


if __name__ == "__main__":
    main()
