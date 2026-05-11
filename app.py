import streamlit as st
import pandas as pd
import json
import os
import matplotlib.pyplot as plt
from datetime import datetime, date
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="To-Do List",
    page_icon="✅",
    layout="wide"
)

st.title("✅ Smart To-Do List")
st.markdown("Manage tasks with priorities, "
            "deadlines and progress tracking.")
st.markdown("---")

# Persistence
TODO_FILE = "todos.json"

def load_todos():
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE, 'r') as f:
            return json.load(f)
    return []

def save_todos(todos):
    with open(TODO_FILE, 'w') as f:
        json.dump(todos, f, indent=2)

def generate_id():
    return datetime.now().strftime(
        '%Y%m%d%H%M%S%f')

# Colors
PRIORITY_COLORS = {
    'High':   '#e74c3c',
    'Medium': '#f39c12',
    'Low':    '#2ecc71'
}

CATEGORY_COLORS = {
    'Work':      '#3498db',
    'Study':     '#9b59b6',
    'Personal':  '#2ecc71',
    'Health':    '#e74c3c',
    'Finance':   '#f39c12',
    'Project':   '#1abc9c',
    'Other':     '#95a5a6'
}

CATEGORIES = list(CATEGORY_COLORS.keys())
PRIORITIES = ['High', 'Medium', 'Low']

# Session state
if 'todos' not in st.session_state:
    st.session_state.todos = load_todos()

# Sidebar — Add task
st.sidebar.header("➕ Add New Task")

task_title = st.sidebar.text_input(
    "Task title:",
    placeholder="What needs to be done?"
)
task_desc = st.sidebar.text_area(
    "Description (optional):",
    placeholder="Add details...",
    height=80
)
task_priority = st.sidebar.selectbox(
    "Priority:", PRIORITIES)
task_category = st.sidebar.selectbox(
    "Category:", CATEGORIES)
task_deadline = st.sidebar.date_input(
    "Deadline:", min_value=date.today())

if st.sidebar.button("➕ Add Task",
                     type="primary"):
    if task_title.strip():
        todo = {
            'id':        generate_id(),
            'title':     task_title,
            'desc':      task_desc,
            'priority':  task_priority,
            'category':  task_category,
            'deadline':  str(task_deadline),
            'done':      False,
            'created':   str(date.today()),
            'completed_at': None
        }
        st.session_state.todos.insert(0, todo)
        save_todos(st.session_state.todos)
        st.sidebar.success("✅ Task added!")
        st.rerun()
    else:
        st.sidebar.warning(
            "Please enter a task title.")

# Sidebar stats
st.sidebar.markdown("---")
total    = len(st.session_state.todos)
done     = sum(1 for t in
               st.session_state.todos
               if t['done'])
pending  = total - done
overdue  = sum(
    1 for t in st.session_state.todos
    if not t['done'] and
    t['deadline'] < str(date.today())
)

st.sidebar.markdown("### 📊 Quick Stats")
st.sidebar.metric("Total Tasks",   total)
st.sidebar.metric("Completed",     done)
st.sidebar.metric("Pending",       pending)
if overdue > 0:
    st.sidebar.error(
        f"⚠️ {overdue} overdue tasks!")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Tasks",
    "📅 Today",
    "📊 Analytics",
    "🗂️ Completed"
])

# Tab 1 — All Tasks
with tab1:
    if not st.session_state.todos:
        st.info("No tasks yet! Add your first "
                "task using the sidebar.")
    else:
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_priority = st.selectbox(
                "Filter priority:",
                ["All"] + PRIORITIES
            )
        with col2:
            filter_category = st.selectbox(
                "Filter category:",
                ["All"] + CATEGORIES
            )
        with col3:
            sort_by = st.selectbox(
                "Sort by:",
                ["Deadline", "Priority",
                 "Created", "Category"]
            )

        # Apply filters
        todos = [
            t for t in st.session_state.todos
            if not t['done']
        ]

        if filter_priority != "All":
            todos = [
                t for t in todos
                if t['priority'] ==
                filter_priority
            ]
        if filter_category != "All":
            todos = [
                t for t in todos
                if t['category'] ==
                filter_category
            ]

        # Sort
        priority_order = {
            'High': 0, 'Medium': 1, 'Low': 2}
        if sort_by == "Deadline":
            todos.sort(
                key=lambda x: x['deadline'])
        elif sort_by == "Priority":
            todos.sort(
                key=lambda x:
                priority_order[x['priority']])
        elif sort_by == "Category":
            todos.sort(
                key=lambda x: x['category'])

        st.markdown(
            f"**{len(todos)} pending tasks**")
        st.markdown("---")

        for todo in todos:
            p_color = PRIORITY_COLORS[
                todo['priority']]
            c_color = CATEGORY_COLORS.get(
                todo['category'], '#95a5a6')

            # Check overdue
            is_overdue = todo['deadline'] < str(date.today())
            overdue_label = " ⚠️ OVERDUE" \
                if is_overdue else ""

            with st.container():
                st.markdown(
                    f"<div style='"
                    f"border-left:4px solid "
                    f"{p_color}; "
                    f"padding:10px; "
                    f"border-radius:4px; "
                    f"margin-bottom:8px'>"
                    f"<b>{todo['title']}"
                    f"{overdue_label}</b><br>"
                    f"<small style='color:gray'>"
                    f"📅 {todo['deadline']} | "
                    f"<span style='"
                    f"background:{c_color};"
                    f"color:white;"
                    f"padding:2px 6px;"
                    f"border-radius:8px;"
                    f"font-size:11px'>"
                    f"{todo['category']}"
                    f"</span> | "
                    f"<span style='"
                    f"background:{p_color};"
                    f"color:white;"
                    f"padding:2px 6px;"
                    f"border-radius:8px;"
                    f"font-size:11px'>"
                    f"{todo['priority']}"
                    f"</span>"
                    f"</small>"
                    f"</div>",
                    unsafe_allow_html=True
                )

                if todo['desc']:
                    st.caption(
                        f"📝 {todo['desc'][:80]}")

                c1, c2, c3 = st.columns([1,1,4])
                with c1:
                    if st.button(
                        "✅ Done",
                        key=f"done_{todo['id']}"
                    ):
                        for t in st.session_state\
                                .todos:
                            if t['id'] == \
                                    todo['id']:
                                t['done'] = True
                                t['completed_at']\
                                    = str(
                                    date.today())
                        save_todos(
                            st.session_state.todos)
                        st.rerun()
                with c2:
                    if st.button(
                        "🗑️ Delete",
                        key=f"del_{todo['id']}"
                    ):
                        st.session_state.todos = [
                            t for t in
                            st.session_state.todos
                            if t['id'] !=
                            todo['id']
                        ]
                        save_todos(
                            st.session_state.todos)
                        st.rerun()

# Tab 2 — Today
with tab2:
    st.markdown("### 📅 Today's Tasks")
    today_str = str(date.today())

    today_todos = [
        t for t in st.session_state.todos
        if t['deadline'] == today_str
        and not t['done']
    ]
    overdue_todos = [
        t for t in st.session_state.todos
        if t['deadline'] < today_str
        and not t['done']
    ]

    if overdue_todos:
        st.error(
            f"⚠️ {len(overdue_todos)} "
            f"overdue tasks!")
        for todo in overdue_todos:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(
                    f"🔴 **{todo['title']}** "
                    f"— due {todo['deadline']}"
                )
            with col2:
                if st.button(
                    "✅",
                    key=f"ov_{todo['id']}"
                ):
                    for t in st.session_state\
                            .todos:
                        if t['id'] == todo['id']:
                            t['done'] = True
                            t['completed_at'] = \
                                str(date.today())
                    save_todos(
                        st.session_state.todos)
                    st.rerun()

    if today_todos:
        st.success(
            f"📅 {len(today_todos)} tasks "
            f"due today")
        for todo in today_todos:
            col1, col2 = st.columns([4, 1])
            with col1:
                p_color = PRIORITY_COLORS[
                    todo['priority']]
                st.markdown(
                    f"<span style='"
                    f"background:{p_color};"
                    f"color:white;"
                    f"padding:2px 6px;"
                    f"border-radius:6px;"
                    f"font-size:11px'>"
                    f"{todo['priority']}"
                    f"</span> "
                    f"**{todo['title']}**",
                    unsafe_allow_html=True
                )
            with col2:
                if st.button(
                    "✅ Done",
                    key=f"td_{todo['id']}"
                ):
                    for t in st.session_state\
                            .todos:
                        if t['id'] == todo['id']:
                            t['done'] = True
                            t['completed_at'] = \
                                str(date.today())
                    save_todos(
                        st.session_state.todos)
                    st.rerun()
    elif not overdue_todos:
        st.success(
            "🎉 No tasks due today. "
            "You're all caught up!")

# Tab 3 — Analytics
with tab3:
    st.markdown("### 📊 Task Analytics")

    if not st.session_state.todos:
        st.info("Add some tasks to see analytics!")
    else:
        df = pd.DataFrame(st.session_state.todos)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### By Category")
            cat_counts = df.groupby(
                'category').size()
            fig, ax    = plt.subplots(
                figsize=(6, 4))
            colors     = [
                CATEGORY_COLORS.get(c, '#95a5a6')
                for c in cat_counts.index
            ]
            ax.pie(cat_counts.values,
                   labels=cat_counts.index,
                   colors=colors,
                   autopct='%1.1f%%',
                   startangle=90,
                   wedgeprops={
                       'edgecolor': 'white'})
            ax.set_title('Tasks by Category',
                         fontsize=12)
            plt.tight_layout()
            st.pyplot(fig)

        with col2:
            st.markdown("#### By Priority")
            pri_counts = df.groupby(
                'priority').size()
            fig2, ax2  = plt.subplots(
                figsize=(6, 4))
            colors2    = [
                PRIORITY_COLORS.get(p, '#95a5a6')
                for p in pri_counts.index
            ]
            ax2.bar(pri_counts.index,
                    pri_counts.values,
                    color=colors2,
                    edgecolor='black')
            ax2.set_title('Tasks by Priority',
                          fontsize=12)
            ax2.set_ylabel('Count')
            plt.tight_layout()
            st.pyplot(fig2)

        # Completion rate
        total_tasks = len(df)
        done_tasks  = len(df[df['done'] == True])
        comp_rate   = (done_tasks / total_tasks
                       * 100) if total_tasks > 0 \
                      else 0

        s1, s2, s3, s4 = st.columns(4)
        s1.metric("Completion Rate",
                  f"{comp_rate:.1f}%")
        s2.metric("High Priority",
                  len(df[df['priority'] ==
                         'High']))
        today_str2 = str(date.today())
        overdue_count = len(df[
                 (df['done'] == False) &
                 (df['deadline'] < today_str2)
          ])
        s3.metric("Overdue", overdue_count)
        s4.metric("Categories Used",
                  df['category'].nunique())

# Tab 4 — Completed
with tab4:
    st.markdown("### 🗂️ Completed Tasks")

    completed = [
        t for t in st.session_state.todos
        if t['done']
    ]

    if not completed:
        st.info("No completed tasks yet. "
                "Mark tasks as done to see them here!")
    else:
        st.success(
            f"🎉 {len(completed)} tasks completed!")

        for todo in reversed(completed):
            with st.expander(
                f"✅ {todo['title']} "
                f"— {todo['category']}"
            ):
                st.write(
                    f"**Priority:** "
                    f"{todo['priority']}")
                st.write(
                    f"**Deadline:** "
                    f"{todo['deadline']}")
                st.write(
                    f"**Completed:** "
                    f"{todo['completed_at']}")
                if todo['desc']:
                    st.write(
                        f"**Notes:** {todo['desc']}")

                if st.button(
                    "↩️ Restore",
                    key=f"restore_{todo['id']}"
                ):
                    for t in st.session_state\
                            .todos:
                        if t['id'] == todo['id']:
                            t['done'] = False
                            t['completed_at'] = \
                                None
                    save_todos(
                        st.session_state.todos)
                    st.rerun()

        # Download completed
        comp_df = pd.DataFrame(completed)
        csv     = comp_df.to_csv(index=False)
        st.download_button(
            "⬇️ Download Completed Tasks",
            csv,
            "completed_tasks.csv",
            "text/csv"
        )

st.markdown("---")
st.markdown(
    "Built by **Jyotiraditya** | "
    "Smart To-Do List | "
    "Stay organized, stay productive ✅"
)