import sqlite3
import os
import streamlit as st
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
import streamlit_pydantic as sp

# Connect to the database
DB_CONFIG = os.getenv("DB_TYPE")
if DB_CONFIG == 'PG':
    import psycopg2
    PG_USER = os.getenv("PG_USER")
    PG_PASSWORD = os.getenv("PG_PASSWORD")
    PG_HOST = os.getenv("PG_HOST")
    PG_PORT = os.getenv("PG_PORT")
    con = psycopg2.connect(f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/todoapp?connect_timeout=10&application_name=todoapp")
else:
    con = sqlite3.connect("todoapp.sqlite", check_same_thread=False)
cur = con.cursor()

# Update the CREATE TABLE command to include all fields
cur.execute(
    """
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY,
        name TEXT,
        description TEXT,
        created_at TEXT,
        created_by TEXT,
        category TEXT,
        state TEXT
    )
    """
)

class TaskState(Enum):
    PLANNED = 'planned'
    IN_PROGRESS = 'in-progress'
    DONE = 'done'

class Task(BaseModel):
    name: str = Field(...)
    description: str = Field(...)
    created_at: datetime = Field(default_factory=datetime.now)
    created_by: str = Field(...)
    category: str = Field(...)
    state: TaskState = Field(...)

def main():
    st.title("Todo App")

    # Create a Form using the streamlit-pydantic package
    form_data = sp.pydantic_form(key="task_form", model=Task)
    if form_data:
        # Convert datetime to string for SQLite
        created_at_str = form_data.created_at.strftime("%Y-%m-%d %H:%M:%S")
        # Insert the new task into the database
        cur.execute(
            """
            INSERT INTO tasks (name, description, created_at, created_by, category, state) 
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (form_data.name, form_data.description, created_at_str, form_data.created_by, form_data.category, form_data.state.value),
        )
        con.commit()
        st.success("Task added successfully!")

    # Fetch and display tasks...
    data = cur.execute("SELECT * FROM tasks").fetchall()
    cols = st.columns(6)
    cols[0].write("ID")
    cols[1].write("Name")
    cols[2].write("Description")
    cols[3].write("Created At")
    cols[4].write("Created By")
    cols[5].write("State")
    for row in data:
        cols = st.columns(6)
        cols[0].write(row[0])
        cols[1].write(row[1])
        cols[2].write(row[2])
        created_at_display = datetime.strptime(row[3], "%Y-%m-%d %H:%M:%S") if row[3] else "N/A"
        cols[3].write(created_at_display)
        cols[4].write(row[4])
        cols[5].write(row[5])

if __name__ == "__main__":
    main()
