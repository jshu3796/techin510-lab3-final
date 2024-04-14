import os
from dataclasses import dataclass
import datetime

import streamlit as st
import psycopg2
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Prompt:
    title: str
    prompt: str
    is_favorite: bool
    created_at: datetime.datetime = None
    updated_at: datetime.datetime = None

def setup_database():
    con = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = con.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS prompts (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            prompt TEXT NOT NULL,
            is_favorite BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    con.commit()
    return con, cur

def prompt_form(prompt=None):
    default = Prompt("", "", False) if prompt is None else prompt
    with st.form(key="prompt_form", clear_on_submit=True):
        title = st.text_input("Title", value=default.title)
        prompt_content = st.text_area("Prompt", height=200, value=default.prompt)
        is_favorite = st.checkbox("Favorite", value=default.is_favorite)
        submitted = st.form_submit_button("Submit")
        if submitted:
            if not title or not prompt_content:
                st.error('Please fill in both the title and prompt fields.')
                return
            return Prompt(title, prompt_content, is_favorite)

def display_prompts(cur, search_query, sort_key, sort_order):
    query = "SELECT * FROM prompts"
    conditions = []
    if search_query:
        conditions.append("(title LIKE %s OR prompt LIKE %s)")
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += f" ORDER BY {sort_key} {sort_order}"
    cur.execute(query, ['%' + search_query + '%', '%' + search_query + '%'] if search_query else [])
    prompts = cur.fetchall()
    for p in prompts:
        with st.expander(f"{p[1]} - Created on {p[4]}"):
            st.code(p[2])
            if st.button("Delete", key=p[0]):
                cur.execute("DELETE FROM prompts WHERE id = %s", (p[0],))
                con.commit()
                st.rerun()
            fav_button_label = "Remove from Favorite" if p[3] else "Add to Favorite"
            if st.button(fav_button_label, key=f"fav_{p[0]}"):
                new_fav_status = not p[3]
                cur.execute("UPDATE prompts SET is_favorite = %s WHERE id = %s", (new_fav_status, p[0]))
                con.commit()
                st.rerun()

if __name__ == "__main__":
    st.title("Promptbase")
    st.subheader("A simple app to store and retrieve prompts")

    con, cur = setup_database()
    search_query = st.text_input("Search Prompts", "")
    sort_key = st.selectbox("Sort by", options=["created_at", "title", "is_favorite"], index=0)
    sort_order = st.selectbox("Order", options=["ASC", "DESC"], index=1)
    new_prompt = prompt_form()
    if new_prompt:
        try:
            cur.execute(
                "INSERT INTO prompts (title, prompt, is_favorite) VALUES (%s, %s, %s)",
                (new_prompt.title, new_prompt.prompt, new_prompt.is_favorite)
            )
            con.commit()
            st.success("Prompt added successfully!")
        except psycopg2.Error as e:
            st.error(f"Database error: {e}")
    display_prompts(cur, search_query, sort_key, sort_order)
    con.close()
