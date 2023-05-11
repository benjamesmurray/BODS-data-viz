import streamlit as st
import os
from _archive.dataviz_scatterplot import load_data, create_fig1, create_fig2, create_fig3

current_directory = os.getcwd()
print("Current working directory:", current_directory)


def adjust_figsize(fig, scale_factor=2):
    width, height = fig.get_size_inches()
    fig.set_size_inches(width * scale_factor, height * scale_factor)


st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

st.title("BODS - Services Require Attention visualisation")

option = st.selectbox(
    "Please choose a visualisation",
    ["Between 0% and 100%", "0% Attention Percentage", "100% Attention Percentage"],
)

file_name = "timetables_data_catalogue.csv"
grouped = load_data(file_name)

if option == "Between 0% and 100%":
    fig1_file = create_fig1(grouped, current_directory)
    adjust_figsize(fig1_file, 1.5)
    st.pyplot(fig1_file, use_column_width=True)

if option == "0% Attention Percentage":
    fig2_file = create_fig2(grouped, current_directory)
    adjust_figsize(fig2_file, 1.5)
    st.pyplot(fig2_file, use_column_width=True)

if option == "100% Attention Percentage":
    fig3_file = create_fig3(grouped, current_directory)
    adjust_figsize(fig3_file, 1.5)
    st.pyplot(fig3_file, use_column_width=True)
