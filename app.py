from flask import Flask, render_template, request
import pandas as pd
import os
import matplotlib.pyplot as plt

app = Flask(__name__)

# Upload folder setup
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Create folders if not exist
if not os.path.exists("uploads"):
    os.makedirs("uploads")

if not os.path.exists("static"):
    os.makedirs("static")


# Home route
@app.route('/')
def home():
    return render_template('index.html')


# Upload route
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')

    if not file:
        return "No file uploaded"

    # Save file
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    # Read data
    df = pd.read_csv(filepath)

    # 🔹 Basic Info
    rows, cols = df.shape
    columns = list(df.columns)
    dtypes = df.dtypes.astype(str)

    # 🔹 Data Quality
    missing_values = df.isnull().sum()
    total_missing = missing_values.sum()
    duplicates = df.duplicated().sum()

    # 🔹 Graph (Histogram)
    graph_path = os.path.join("static", "graph.png")
    numeric_cols = df.select_dtypes(include='number').columns

    if len(numeric_cols) > 0:
        plt.figure()
        df[numeric_cols[0]].hist()
        plt.title(f"Histogram of {numeric_cols[0]}")
        plt.savefig(graph_path)
        plt.close()

    return render_template(
        "result.html",
        rows=rows,
        cols=cols,
        columns=columns,
        dtypes=dtypes,
        missing_values=missing_values,
        total_missing=total_missing,
        duplicates=duplicates
    )


if __name__ == '__main__':
    app.run(debug=True)