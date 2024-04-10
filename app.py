import os
from dataclasses import dataclass
from datetime import datetime

import streamlit as st
import streamlit_pydantic as sp
from pydantic import BaseModel, Field
import psycopg2
from dotenv import load_dotenv

load_dotenv()

con = psycopg2.connect(os.getenv("DATABASE_URL"))
cur = con.cursor()

cur.execute(
    """
    CREATE TABLE IF NOT EXISTS prompts (
        id SERIAL PRIMARY KEY,
        title TEXT NOT NULL,
        prompt TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
)

@dataclass
class Prompt:
    title: str
    prompt: str
    genre: str
    is_favorite: bool = False
    created_at_datetime = datetime.strptime(created_at_str, "%Y-%m-%d %H:%M:%S")

def prompt_form(prompt=Prompt("","")):
    """
    TODO: Add validation to the form, so that the title and prompt are required.
    """
    with st.form(key="prompt_form", clear_on_submit=True):
        title = st.text_input("Title", value=prompt.title)
        prompt = st.text_area("Prompt", height=200, value=prompt.prompt)
        submitted = st.form_submit_button("Submit")
        if submitted:
            return Prompt(title, prompt)

st.title("Promptbase")
st.subheader("A simple app to store and retrieve prompts")

prompt = prompt_form()
if prompt:
    cur.execute("INSERT INTO prompts (title, prompt) VALUES (%s, %s)", (prompt.title, prompt.prompt,))
    con.commit()
    st.success("Prompt added successfully!")

cur.execute("SELECT * FROM prompts")
prompts = cur.fetchall()


# TODO: Add a search bar
# TODO: Add a sort by date
# TODO: Add favorite button


for p in prompts:
    with st.expander(p[1]):
        st.code(p[2])
        # TODO: Add a edit function
        if st.button("Delete", key=p[0]):
            cur.execute("DELETE FROM prompts WHERE id = %s", (p[0],))
            con.commit()
            st.rerun()