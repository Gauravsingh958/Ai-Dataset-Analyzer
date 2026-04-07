from flask import Flask, render_template, request
import pandas as pd
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']

    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        df = pd.read_csv(filepath)

        rows, cols = df.shape
        columns = list(df.columns)
        dtypes = df.dtypes.astype(str)

        return render_template(
            "result.html",
            rows=rows,
            cols=cols,
            columns=columns,
            dtypes=dtypes
        )

    return "No file uploaded"

if __name__ == '__main__':
    app.run(debug=True)