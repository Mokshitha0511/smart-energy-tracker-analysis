from flask import Flask, request, render_template, Response, redirect, url_for, make_response
import pandas as pd
from app.utils import clean_data, detect_anomalies, init_db, save_anomaly_file, get_anomaly_file
from io import BytesIO
import matplotlib
matplotlib.use("Agg")          # 👈 non-GUI backend for Matplotlib
import matplotlib.pyplot as plt

app = Flask(__name__)

init_db()
df_global = None
anomalies_global = None

@app.route('/upload', methods = ['GET', 'POST'])
def upload_file():
    global df_global, anomalies_global
    if request.method == 'POST':
        file = request.files['file'] # Gets the uploaded file
        df = pd.read_csv(file, sep=';', low_memory=False) # Reads the file into a DataFrame
        print(df.shape)
        df = clean_data(df) # Cleans the file if null values
        df_original = df.copy()  # Keep a copy of the original cleaned data
        df.rename(columns={"Global_active_power": "power"}, inplace=True)
        df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], dayfirst=True)
        anomalies = detect_anomalies(df) # Detect anomalies
        anomalies_original = df_original.loc[anomalies.index]  # Get anomalies from original data
        csv_text = anomalies_original.to_csv(index=False)
        base = file.filename.rsplit(".", 1)[0]
        anomaly_file_name = f"{base}_anomaly.csv"
        save_anomaly_file(anomaly_file_name, csv_text)
        
        # ---- Simple threshold alert ----
        THRESHOLD = 9
        high_usage = df[df['power'] > THRESHOLD]

        for _, row in high_usage.iterrows():
            print(f"⚠️ ALERT: High usage detected! Power={row['power']} at {row['Date']} {row['Time']}")
        # ---- End alert block ----

        df_global = df  
        anomalies_global = anomalies
        return render_template('upload_result.html', filename=file.filename, anomaly_file = anomaly_file_name)
    return render_template('upload.html')

@app.route('/plot_image')
def plot_image():
    if df_global is None or anomalies_global is None:
        print("Data frame or anomalies is None")
        return redirect(url_for('upload_file'))
    
    img = BytesIO()

    # Use original data, no resampling
    df_plot = df_global[['DateTime', 'power']].sort_values('DateTime')
    anomalies_plot = anomalies_global[['DateTime', 'power']].sort_values('DateTime')

    plt.figure(figsize=(16, 6))

    # Main power usage line
    plt.plot(
        df_plot['DateTime'],
        df_plot['power'],
        label='Power Usage',
        color='blue',
        alpha=0.6
    )

    # Anomaly points (exact same level as data)
    if not anomalies_plot.empty:
        plt.scatter(
            anomalies_plot['DateTime'],
            anomalies_plot['power'],
            color='red',
            s=25,
            label='Anomalies'
        )

    # Y-axis limits based on actual data
    y_max = max(df_plot['power'].max(), anomalies_plot['power'].max() if not anomalies_plot.empty else df_plot['power'].max())
    plt.ylim(0, y_max * 1.1)


    #Downsampling the data to 1 day as the graph is too dense with huge data
    #df_downsampled = df_global[['DateTime', 'power']].set_index('DateTime').resample('D').mean().reset_index()
    #anomalies_downsampled = anomalies_global[['DateTime', 'power']].set_index('DateTime').resample('D').max().reset_index()

    #Plotting the downsampled data
    #plt.figure(figsize=(10, 4))
    #plt.plot(df_downsampled['DateTime'], df_downsampled['power'], label='Power Usage', color='blue', alpha=0.6)
    #plt.scatter(anomalies_downsampled['DateTime'], anomalies_downsampled['power'], color='red', s= 25, label='Anomalies')
    #plt.ylim(0, max(df_downsampled['power'].max(), anomalies_downsampled['power'].max())*1.1)
    
    # Set dashboard-like font
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Segoe UI', 'Arial', 'DejaVu Sans']
    plt.xlabel('DateTime', fontsize=12)
    plt.ylabel('Power Usage (kW)', fontsize=12)
    plt.title('Smart Energy Usage', fontsize=14)
    plt.legend()
    plt.tight_layout()
    plt.savefig(img, format='png', dpi=300)
    plt.close()
    img.seek(0)
    return Response(img.getvalue(), mimetype='image/png')

@app.route('/plot')
def plot_page():
    if df_global is None:
        return redirect(url_for('upload_file'))
    anomaly_file = request.args.get('anomaly')
    if anomaly_file is not None and anomaly_file.strip() == "":
        anomaly_file = None
    return render_template('plot.html', anomaly_file = anomaly_file)


@app.route('/download_anomaly')
def download_anomaly():
    file_name = request.args.get('file') 
    if not file_name:
        return "Missing file parameter", 400

    try:
        csv_text = get_anomaly_file(file_name)  # returns TEXT (string) or None
        if not csv_text:
            return "File not found", 404

        resp = make_response(csv_text)
        resp.headers.set('Content-Type', 'text/csv; charset=utf-8')
        resp.headers.set('Content-Disposition', f'attachment; filename={file_name}')
        return resp

    except Exception as e:
        print("Download DB error:", e)
        return "Internal server error", 500


if __name__ == '__main__':
    app.run(debug=True)