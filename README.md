# Excel Streamlit App

## Overview
This app allows users to upload an Excel file, processes it to generate a new file, and provides the ability to download the processed file.

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/excel-streamlit-app.git
cd excel-streamlit-app

```
### 2. Set Up the Conda Environment
```bash
conda env create --file=environment.yml
conda activate my-env2
```
### 3. Run the Streamlit App
```bash
streamlit run PnL_app.py
```

## File Descriptions
### PnL_app.py
This is the Streamlit app which serves as the user interface
### JS_PnL.py
This script contains the function which executes the organizing process for the uploaded blotter
### myenv2.yml
Specifies the Conda environment for all necessary dependencies of this project
### .gitignore
Lists patterns for files and folders to be exclided from version control
### README.md
This document, providing an overview of the project
