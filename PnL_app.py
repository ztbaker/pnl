# -*- coding: utf-8 -*-
"""
Created on Tue Jul  8 15:39:58 2025

@author: ZBaker
"""
# import os
# try:
#     import streamlit as st
# except ImportError:
#     os.system("pip install streamlit")
#     import streamlit as st
import streamlit as st

import os
import subprocess
try:
    import xlsxwriter
except ImportError:
    subprocess.check_call(["pip", "install", "xlsxwriter"])
    import xlsxwriter

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
