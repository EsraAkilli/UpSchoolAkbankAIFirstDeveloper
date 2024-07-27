import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import CatFact, Base

engine = create_engine('sqlite:///cat_facts.db')
Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine)


def get_all_facts():
    session = Session()
    facts = session.query(CatFact).all()
    session.close()
    return facts


def add_fact(text):
    session = Session()
    new_fact = CatFact(text=text)
    session.add(new_fact)
    session.commit()
    session.close()


def delete_fact(fact_id):
    session = Session()
    fact = session.query(CatFact).filter_by(id=fact_id).first()
    if fact:
        session.delete(fact)
        session.commit()
    session.close()


def main():
    st.title("Cat Facts App")

    menu = ["Home", "View Facts", "Add Fact", "Delete Fact"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        st.subheader("Home")
        st.write("Welcome to the Cat Facts App!")
        st.write("Use the menu on the left to navigate.")
        st.image("https://cataas.com/cat", caption="A random cat image")

    elif choice == "View Facts":
        st.subheader("View Cat Facts")
        facts = get_all_facts()
        for fact in facts:
            st.write(f"ID: {fact.id}")
            st.write(f"Fact: {fact.text}")
            st.write(f"Created at: {fact.created_at}")
            st.write(f"Updated at: {fact.updated_at}")
            st.write("---")

    elif choice == "Add Fact":
        st.subheader("Add New Cat Fact")
        new_fact = st.text_area("Enter a new cat fact:")
        if st.button("Add Fact"):
            add_fact(new_fact)
            st.success("Fact added successfully!")

    elif choice == "Delete Fact":
        st.subheader("Delete Cat Fact")
        facts = get_all_facts()
        fact_to_delete = st.selectbox("Select fact to delete",
                                      [(fact.id, fact.text) for fact in facts])
        if st.button("Delete Fact"):
            delete_fact(fact_to_delete[0])
            st.success("Fact deleted successfully!")


if __name__ == '__main__':
    main()
