# -*- coding: utf-8 -*-
"""
Created on Tue Jul  8 15:39:58 2025

@author: ZBaker
"""
import os
try:
    from xlsxwriter.utility import xl_rowcol_to_cell
except ImportError:
    os.system("pip install xlsxwriter")
    from xlsxwriter.utility import xl_rowcol_to_cell
import streamlit as st

from io import BytesIO

from JS_PnL import getPnl

st.title("PnL Config")

BLOTTER_FILE = st.file_uploader("Please upload blotter", type=["xlsx"])

if BLOTTER_FILE is not None:
    try:
        st.info("Processing your file...")
        
        with open("blotter.xlsx", "wb") as temp_file:
            temp_file.write(BLOTTER_FILE.read())
        
        output_file_path = getPnl("blotter.xlsx")
        
        with open(output_file_path, "rb") as f:
            output_data = BytesIO(f.read())
            
        st.success("File processed successfully! Download new PnL file below.")
        st.download_button(
            label="Download Processed PnL File",
            data=output_data,
            file_name="sorted_pnl.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    
    except Exception as e:
        st.error(f"An error occurred: {e}\n Contact provider for more information.")
