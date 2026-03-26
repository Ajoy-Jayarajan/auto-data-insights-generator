import os
import pandas as pd
import streamlit as st
from openai import OpenAI

# Title
st.title("Auto Data Insights Generator")

# API key 
from dotenv import load_dotenv
import os

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN,
)

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, encoding="latin1", on_bad_lines="skip")

    st.subheader("Dataset Preview")
    st.write(df.head())

    numeric_df = df.select_dtypes(include="number")

    if numeric_df.empty:
        st.warning("No numeric columns found.")
    else:
        summary = {
            "columns": df.columns.tolist(),
            "mean_values": numeric_df.mean().round(2).to_dict(),
            "max_values": numeric_df.max().to_dict(),
            "min_values": numeric_df.min().to_dict(),
        }

        st.subheader("Basic Statistics")
        st.write(summary)

        if st.button("Generate Insights"):

            col_preview  = summary["columns"][:20]
            mean_preview = dict(list(summary["mean_values"].items())[:10])
            max_preview  = dict(list(summary["max_values"].items())[:10])
            min_preview  = dict(list(summary["min_values"].items())[:10])

            prompt = (
                f"You are a data analyst. Based on the dataset summary below, "
                f"generate exactly 3 clear, numbered insights in simple English.\n\n"
                f"Columns: {col_preview}\n"
                f"Mean values: {mean_preview}\n"
                f"Max values: {max_preview}\n"
                f"Min values: {min_preview}"
            )

            completion = client.chat.completions.create(
                model="deepseek-ai/DeepSeek-R1:novita",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=512,
            )

            raw = completion.choices[0].message.content.strip()

            if "<think>" in raw and "</think>" in raw:
                raw = raw.split("</think>")[-1].strip()

            st.subheader("AI Insights")
            st.write(raw)