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
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')

    if not file:
        return "No file uploaded"

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    df = pd.read_csv(filepath)

    # 🔹 Basic Info
    rows, cols = df.shape
    missing_values = df.isnull().sum()
    total_missing = missing_values.sum()
    duplicates = df.duplicated().sum()

    # 🔹 Preview
    preview = df.head().to_html(classes="table", index=False)

    # 🔹 Graphs
    numeric_cols = df.select_dtypes(include='number').columns
    cat_cols = df.select_dtypes(include='object').columns

    if len(numeric_cols) > 0:
        plt.figure()
        df[numeric_cols[0]].hist()
        plt.savefig("static/hist.png")
        plt.close()

    if len(cat_cols) > 0:
        plt.figure()
        df[cat_cols[0]].value_counts().head(10).plot(kind='bar')
        plt.savefig("static/bar.png")
        plt.close()

    corr = df.select_dtypes(include='number').corr()
    if not corr.empty:
        plt.figure(figsize=(6,4))
        sns.heatmap(corr, annot=True, cmap="coolwarm")
        plt.savefig("static/heatmap.png")
        plt.close()

    # 🔹 Insights
    insights = []

    for col, val in missing_values.items():
        if val > 0:
            insights.append(f"{col} has {val} missing values")

    if not corr.empty:
        for i in corr.columns:
            for j in corr.columns:
                if i != j and abs(corr.loc[i, j]) > 0.7:
                    insights.append(f"High correlation between {i} and {j}")
                    break

    if len(insights) == 0:
        insights.append("Dataset looks clean 👍 No major issues found")

    return render_template(
        "result.html",
        rows=rows,
        cols=cols,
        total_missing=total_missing,
        duplicates=duplicates,
        preview=preview,
        missing_values=missing_values,
        insights=insights
    )


if __name__ == '__main__':
    app.run(debug=True)