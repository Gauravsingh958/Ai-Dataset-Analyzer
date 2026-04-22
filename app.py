from flask import Flask, render_template, request
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs("uploads", exist_ok=True)
os.makedirs("static", exist_ok=True)


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')

    if not file:
        return "No file uploaded"

    # Save file
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    # Read CSV
    df = pd.read_csv(filepath)

    # ---------------- BASIC INFO ----------------
    rows, cols = df.shape
    missing_values = df.isnull().sum()
    total_missing = int(missing_values.sum())
    duplicates = int(df.duplicated().sum())

    # ---------------- PREVIEW ----------------
    preview = df.head().to_html(index=False)

    # ---------------- COLUMN TYPES ----------------
    numeric_cols = df.select_dtypes(include='number').columns
    categorical_cols = df.select_dtypes(include='object').columns

    # ---------------- COLUMN ANALYSIS ----------------
    numeric_analysis = []
    for col in numeric_cols:
        numeric_analysis.append({
            "name": col,
            "mean": round(df[col].mean(), 2),
            "min": df[col].min(),
            "max": df[col].max()
        })

    categorical_analysis = []
    for col in categorical_cols:
        categorical_analysis.append({
            "name": col,
            "unique": df[col].nunique(),
            "top": df[col].mode()[0] if not df[col].mode().empty else "N/A"
        })

    # ---------------- OUTLIER DETECTION (IQR METHOD) ----------------
    outliers = {}

    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1

        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR

        count = df[(df[col] < lower) | (df[col] > upper)].shape[0]
        outliers[col] = int(count)

    # ---------------- GRAPHS ----------------
    if len(numeric_cols) > 0:
        plt.figure()
        df[numeric_cols[0]].hist()
        plt.title(f"Histogram of {numeric_cols[0]}")
        plt.savefig("static/hist.png")
        plt.close()

    if len(categorical_cols) > 0:
        plt.figure()
        df[categorical_cols[0]].value_counts().head(10).plot(kind='bar')
        plt.title(f"Top values of {categorical_cols[0]}")
        plt.savefig("static/bar.png")
        plt.close()

    corr = df.select_dtypes(include='number').corr()
    if not corr.empty:
        plt.figure(figsize=(6, 4))
        sns.heatmap(corr, annot=True, cmap="coolwarm")
        plt.title("Correlation Heatmap")
        plt.savefig("static/heatmap.png")
        plt.close()

    # ---------------- AI INSIGHTS ----------------
    insights = []

    if total_missing > 0:
        insights.append("Dataset contains missing values")

    if duplicates > 0:
        insights.append("Duplicate rows are present")

    for col, val in outliers.items():
        if val > 0:
            insights.append(f"{col} has {val} outliers")

    if len(insights) == 0:
        insights.append("Dataset looks clean and well structured")

    # ---------------- RENDER ----------------
    return render_template(
        "result.html",
        rows=rows,
        cols=cols,
        total_missing=total_missing,
        duplicates=duplicates,
        preview=preview,
        insights=insights,
        numeric_analysis=numeric_analysis,
        categorical_analysis=categorical_analysis,
        outliers=outliers
    )


if __name__ == "__main__":
    app.run(debug=True)