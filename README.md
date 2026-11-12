# Project Setup and Run Guide

Follow the instructions below according to your operating system to set up the environment and run the application.

## Prerequisites

- Python 3.8 or higher installed on your system.

## For Windows Users

```
python -m venv venv
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\venv\Scripts\activate
pip install streamlit
pip isntall streamlit plotly
streamlit run app.py
```
If your download speed is slow, you can use this instead of `pip install streamlit`:

```
pip install streamlit -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## For macOS/Linux Users

```
python3 -m venv venv
source venv/bin/activate
pip install streamlit
pip isntall streamlit plotly
streamlit run app.py
```
If your download speed is slow, you can use this instead of `pip install streamlit`:

```
pip install streamlit -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## Deactivating the Virtual Environment

When you are finished working, you can deactivate the environment on any operating system by pressing `CTRL+C`