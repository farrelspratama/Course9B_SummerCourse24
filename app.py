from flask import Flask, render_template
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# Load and preprocess data (Assuming you have downloaded and saved the data as 'waste_data.xlsx')
def load_data():
    # Load Excel file
    df = pd.read_excel('Data_Timbulan_Sampah_SIPSN_KLHK.xlsx', skiprows=1)
    
    return df

data = load_data()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/total_waste')
def total_waste():
    total_waste_per_province = data.groupby(['Provinsi', 'Tahun'])['Timbulan Sampah Tahunan(ton)'].sum().reset_index()
    return render_template('total_waste.html', data=total_waste_per_province.to_html())

@app.route('/average_waste')
def average_waste():
    average_waste_per_province = data.groupby('Provinsi')['Timbulan Sampah Tahunan(ton)'].mean().reset_index()
    return render_template('average_waste.html', data=average_waste_per_province.to_html())

@app.route('/most_least_waste')
def most_least_waste():
    most_waste_per_year = data.groupby(['Tahun', 'Provinsi'])['Timbulan Sampah Tahunan(ton)'].sum().reset_index().sort_values(['Tahun', 'Timbulan Sampah Tahunan(ton)'], ascending=[True, False]).groupby('Tahun').first().reset_index()
    least_waste_per_year = data.groupby(['Tahun', 'Provinsi'])['Timbulan Sampah Tahunan(ton)'].sum().reset_index().sort_values(['Tahun', 'Timbulan Sampah Tahunan(ton)'], ascending=[True, True]).groupby('Tahun').first().reset_index()
    return render_template('most_least_waste.html', most_waste=most_waste_per_year.to_html(), least_waste=least_waste_per_year.to_html())

@app.route('/waste_graph')
def waste_graph():
    total_waste_per_province = data.groupby(['Provinsi', 'Tahun'])['Timbulan Sampah Tahunan(ton)'].sum().unstack().fillna(0)
    fig, ax = plt.subplots(figsize=(15, 8))
    total_waste_per_province.T.plot(ax=ax)
    plt.title('Annual Waste Generation (Tons) in Each Province 2018-2023')
    plt.xlabel('Years')
    plt.ylabel('Annual Waste Generation (Tons)')
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    return render_template('waste_graph.html', plot_url=plot_url)

@app.route('/average_waste_categorization')
def average_waste_categorization():
    average_waste_per_province = data.groupby('Provinsi')['Timbulan Sampah Tahunan(ton)'].mean().reset_index()
    average_waste_per_province['Category'] = pd.cut(average_waste_per_province['Timbulan Sampah Tahunan(ton)'], bins=[0, 100000, 700000, float('inf')], labels=['GREEN', 'ORANGE', 'RED'])
    
    # Generate bar chart
    colors = {'GREEN': 'green', 'ORANGE': 'orange', 'RED': 'red'}
    fig, ax = plt.subplots(figsize=(15, 8))
    for category, color in colors.items():
        subset = average_waste_per_province[average_waste_per_province['Category'] == category]
        ax.bar(subset['Category'], subset['Provinsi'], color=color, label=category)
    plt.xticks(rotation=90)
    plt.legend(title='Category')
    plt.title('Average Annual Waste Categorization by Province')
    plt.xlabel('Province')
    plt.ylabel('Average Waste (tons)')
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url_categorization = base64.b64encode(img.getvalue()).decode('utf8')
    return render_template('average_waste_categorization.html', plot_url=plot_url_categorization)

if __name__ == '__main__':
    app.run(debug=True)
