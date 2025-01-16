import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time

st.title('Tutorial data analysis')

with st.spinner('loading data...'):
    uploaded_file = st.file_uploader('upload file', type=['csv'])

if "counter" not in st.session_state:
    st.session_state.counter = 0

st.session_state.counter += 1

st.header(f"This page has run {st.session_state.counter} times.")
st.button("Run it again")

st.sidebar.subheader("Use of selectbox and slider in sidebar:") 

# Add a selectbox to the sidebar:
add_selectbox = st.sidebar.selectbox(
    'How would you like to be contacted?',
    ('Email', 'Home phone', 'Mobile phone')
)

# Add a slider to the sidebar:
add_slider = st.sidebar.slider(
    'Select a range of values',
    0.0, 100.0, (25.0, 75.0),
    step = 4.0
)

'Starting a long computation...'

# Add a placeholder
latest_iteration = st.empty()
bar = st.progress(0)

for i in range(10):
  # Update the progress bar with each iteration.
  latest_iteration.text(f'Iteration {i+1}')
  bar.progress(i + 1)
  time.sleep(0.1)

'...and now we\'re done!'

if uploaded_file:

    df = pd.read_csv(uploaded_file)

    st.subheader("Data preview")
    st.dataframe(df.head())
    # st.write(df.sample(5))
    x = st.slider('x', min_value=20, max_value=1000)  # 👈 this is a widget
    st.write(x, 'squared is', x * x)

    st.text_input("API KEY", key="name", type="password")
    # You can access the value at any point with:
    # st.session_state.name
    st.subheader("Use of columns sections:")

    left_column, right_column = st.columns(2)
    # You can use a column just like st.sidebar:
    left_column.button('Press me!')

    # Or even better, call Streamlit functions inside a "with" block:
    with right_column:
        chosen = st.radio(
            'Sorting hat',
            ("Gryffindor", "Ravenclaw", "Hufflepuff", "Slytherin"))
        st.write(f"You are in {chosen} house!")

    st.subheader("Data info")
    st.write(df.describe())

    if st.checkbox('correlation'):
        st.write(df.select_dtypes(include='number').corr())

    st.subheader("Data columns")
    selected_col = st.selectbox('select column', df.columns)

    unique_values = df[selected_col].unique()
    st.subheader("unique values of the selected column")
    selected_value = st.selectbox('select value', unique_values)

    filtered_df = df[df[selected_col] == selected_value]
    st.write(filtered_df.head())

    st.subheader("Data visualization")
    st.write("line chart")
    x_axes = st.selectbox('select x axes', df.columns)
    y_axes = st.selectbox('select y axes', df.columns)

    if st.button('generate line chart'):
        st.line_chart(filtered_df.set_index(x_axes)[y_axes])
else:
    st.write('waiting for file upload')





