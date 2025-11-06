from flask import Flask, render_template, request, send_file
import pandas as pd
import os
import numpy as np
from sklearn.linear_model import LinearRegression

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    # Read CSV
    df = pd.read_csv(filepath)
    df['Date'] = pd.to_datetime(df['Date'])

    # Calculations
    df['Revenue'] = df['Units_Sold'] * df['Price']
    total_sales = df['Revenue'].sum()
    top_product = df.groupby('Product')['Units_Sold'].sum().idxmax()
    top_revenue_product = df.groupby('Product')['Revenue'].sum().idxmax()
    low_stock_items = df[df['Stock'] < 10]['Product'].tolist()
    high_demand = df.groupby('Product')['Units_Sold'].sum().nlargest(3).index.tolist()

    # Monthly trends
    monthly_sales = df.groupby(df['Date'].dt.strftime('%B'))['Units_Sold'].sum().to_dict()

    # Predict next 3 months
    monthly = df.groupby(df['Date'].dt.month)['Units_Sold'].sum()
    X = np.array(monthly.index).reshape(-1, 1)
    y = monthly.values
    model = LinearRegression()
    model.fit(X, y)
    predictions = {f'Month {i}': int(model.predict([[max(X)[0] + i]])[0]) for i in range(1, 4)}

    # Insights
    best_day = df.groupby(df['Date'].dt.day_name())['Units_Sold'].sum().idxmax()
    insights = [
        f"Best-selling product: {top_product}",
        f"Highest revenue product: {top_revenue_product}",
        f"Best day for sales: {best_day}",
        f"Total revenue generated: ₹{int(total_sales)}"
    ]

    # Summary CSV
    summary = pd.DataFrame({
        'Metric': ['Total Sales', 'Top Product', 'Highest Revenue Product', 'Best Day'],
        'Value': [total_sales, top_product, top_revenue_product, best_day]
    })
    summary_path = os.path.join(app.config['UPLOAD_FOLDER'], 'report.csv')
    summary.to_csv(summary_path, index=False)

    # Top 5 Products by Revenue
    top_products_revenue = df.groupby('Product')['Revenue'].sum().nlargest(5)

    return render_template(
        'dashboard.html',
        table=df.to_html(classes='table table-striped', index=False),
        total_sales=total_sales,
        top_product=top_product,
        low_stock_items=low_stock_items,
        high_demand=high_demand,
        month_labels=list(monthly_sales.keys()),
        month_values=list(monthly_sales.values()),
        insights=insights,
        predictions=predictions,
        top_products=top_products_revenue.index.tolist(),
        top_revenue_values=top_products_revenue.values.tolist()
    )


@app.route('/download')
def download():
    return send_file('uploads/report.csv', as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
