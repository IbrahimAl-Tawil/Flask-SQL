from flask import Flask, render_template, request, redirect, url_for
import MySQLdb
import MySQLdb.cursors
from MySQLdb._exceptions import IntegrityError



app = Flask(__name__)

# Database configuration
DB_HOST = 'localhost'
DB_USER = 'u##'
DB_NAME = 'u##'
DB_PASSWORD = 'passwordGoesHere'

def get_db_connection():
    return MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME, cursorclass=MySQLdb.cursors.DictCursor)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/show_table', methods=['GET', 'POST'])
def show_table():
    if request.method == 'POST':
        table_name = request.form.get('table_name')
        # TODO: Validate table_name to prevent SQL injection
        conn = get_db_connection()
        cur = conn.cursor()

        if table_name == "suppliers":
            try:
                cur.execute("SELECT suppliers.supplierID, suppliers.name, suppliers.email, supplierPhones.telNumber FROM suppliers, supplierPhones WHERE suppliers.supplierID = supplierPhones.supplierID;")
                data = cur.fetchall()
                columns = [desc[0] for desc in cur.description]
                cur.close()
                return render_template('show_table.html', data=data, columns=columns, table_name=table_name)
            except MySQLdb.Error as e:
                cur.close()
                return f"Error fetching data from the database: {str(e)}", 500
            
        if table_name == "orders":
            try:
                cur.execute("SELECT orders.orderID, orders.date, orders.supplierID, orderDetails.partID, orderDetails.qty FROM orders, orderDetails WHERE orders.orderID = orderDetails.orderID;")
                data = cur.fetchall()
                columns = [desc[0] for desc in cur.description]
                cur.close()
                return render_template('show_table.html', data=data, columns=columns, table_name=table_name)
            except MySQLdb.Error as e:
                cur.close()
                return f"Error fetching data from the database: {str(e)}", 500

        else:
            try:
                cur.execute(f"SELECT * FROM {table_name}")
                data = cur.fetchall()
                columns = [desc[0] for desc in cur.description]
                cur.close()
                return render_template('show_table.html', data=data, columns=columns, table_name=table_name)
            except MySQLdb.Error as e:
                cur.close()
                return f"Error fetching data from the database: {str(e)}", 500
    return render_template('show_table_form.html')  # Ensure you have a form in 'show_table_form.html'

@app.route('/add_suppliers', methods=['GET', 'POST'])
def add_supplier():
    if request.method == 'POST':
        supplierID = request.form['supplierID']
        name = request.form['name']
        email = request.form['email']
        telNumber = request.form.getlist('tel[]')
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO suppliers (supplierID, name, email) VALUES (%s, %s, %s)", (supplierID, name, email))

            insertTel = "INSERT INTO supplierPhones (telNumber, supplierID) VALUES (%s, %s)"
            for i in telNumber:
                cur.execute(insertTel, (i, supplierID))
            conn.commit()

            # Optionally, provide feedback to the user about successful addition
            return redirect(url_for('index'))  # Assuming you have a route or template named 'index'
        except IntegrityError as e:
            conn.rollback()
            if e.args[0] == 1062:
                # Handle the duplicate entry scenario
                error_message = "Error: Duplicate Entry"
            else:
                # Handle other MySQL errors
                error_message = f"Failed to add supplier: {str(e)}"
            return error_message
        finally:
            cur.close()
    return render_template('add_suppliers.html')
@app.route('/annual-expenses', methods=['GET', 'POST'])
def annual_expenses():
    if request.method == 'POST':
        start = request.form['start_year']
        end = request.form['end_year']

        conn = get_db_connection()
        cur = conn.cursor()
        # SQL injection fix: use placeholders for parameters
        cur.execute("""
        SELECT YEAR(orders.date) AS year, SUM(parts.price * orderDetails.qty) AS total_amount
	    FROM orderDetails
	    JOIN parts ON orderDetails.partID = parts.partID
	    JOIN orders ON orders.orderID = orderDetails.orderID
	    WHERE YEAR(orders.date) >= %s AND YEAR(orders.date) <= %s
	    GROUP BY YEAR(orders.date);""", (start, end))  
        expenses = cur.fetchall()
        conn.close()

        # Pass the expenses list to the template
        return render_template('annual_expenses.html', expenses=expenses)
    else:
        # This ensures that there is always a return statement regardless of the request method
        return render_template('annual_expenses.html', expenses=None)


def calculate_projections(initialYearExpenses, years, rate):
    projections = []
    for year in range(1, years + 1):
        future_amount = initialYearExpenses * ((1 + rate) ** year)
        projections.append((2023 + year, future_amount))
    return projections

@app.route('/budget-projection', methods=['GET', 'POST'])
def budget_projection():
    if request.method == 'POST':
        # last full year:
        initialYear = 2023
        years = request.form.get('years')
        inflation_rate = request.form.get('inflation_rate')
        if years and inflation_rate:
            years = int(years)
            inflation_rate = float(inflation_rate) / 100

            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute("""SELECT SUM(parts.price * orderDetails.qty) AS 'total_expenses'
                        FROM orderDetails
                        JOIN parts ON orderDetails.partID = parts.partID
                        JOIN orders ON orders.orderID = orderDetails.orderID
                        WHERE YEAR(orders.date) = %s;""", (initialYear,))
            
            result = cur.fetchone()
            conn.close()

            if result and result['total_expenses']:
                initialExpenses = result['total_expenses']
            else:
                initialExpenses = 0
            # initialExpenses = result['total_expenses'] if result else 0
            
            projections = calculate_projections(initialExpenses, years, inflation_rate)
            


            return render_template('budget_projection.html', projections=projections)
        else:
            # If years or inflation_rate are missing, optionally handle the error
            error_message = "Please provide both the number of years and the inflation rate."
            # Render the form again with an error message
            return render_template('budget_projection.html', error_message=error_message)
    else:
        # GET request - just show the form without projections
        return render_template('budget_projection.html')	
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=13412)