#!/bin/bash

# MySQL credentials and database name
user="u##"
pass="passwordGoesHere"
db="u##"

# paths to JSON files
suppliersFile="./suppliers_100.json"
ordersFile="./orders_4000.json"

# function to parse JSON with Python
parseJson() {
    python3 -c "import json, sys; [print(json.dumps(obj)) for obj in json.load(sys.stdin)]"
}

# parsing the suppliers_100.json supplierID, name, and email
while IFS= read -r suppliers; do
    supplierID=$(echo $suppliers | python3 -c "import json; obj=json.loads(input()); print(obj['_id'])")
    name=$(echo $suppliers | python3 -c "import json; obj=json.loads(input()); print(obj['name'])")
    email=$(echo $suppliers | python3 -c "import json; obj=json.loads(input()); print(obj['email'])")
    
    # inserting supplierID, name, and email into the suppliers table
    mysql -u"$user" -p"$pass" -D"$db" -e \
    "INSERT INTO suppliers (supplierID, name, email) VALUES ('$supplierID', '$name', '$email');"

    # parsing the telephone numbers
    echo $suppliers | python3 -c "import json; obj=json.loads(input()); [print(tel['number']) for tel in obj['tel']]" | while IFS= read -r number; do
        # inserting telNumber into the supplierPhones table
        mysql -u"$user" -p"$pass" -D"$db" -e \
        "INSERT INTO supplierPhones (telNumber, supplierID) VALUES ('$number', '$supplierID');"
    done
done < <(parseJson < "$suppliersFile")


# parsing the orders_4000.json date and supplierID
while IFS= read -r orders; do
    date=$(echo "$orders" | python3 -c "import json; obj=json.loads(input()); print(obj['when'])")
    orderSupplierID=$(echo "$orders" | python3 -c "import json; obj=json.loads(input()); print(obj['supp_id'])")
    
    # inserting date, supplierID, and orderID into the orders table
    orderID=$(mysql -u"$user" -p"$pass" -D"$db" -se \
    "INSERT INTO orders (date, supplierID) VALUES ('$date', '$orderSupplierID'); SELECT LAST_INSERT_ID();")

    # parsing the order details
    echo "$orders" | python3 -c "import json; obj=json.loads(input()); [print(item['part_id'], item['qty']) for item in obj['items']]" | while IFS=' ' read -r partID qty; do
        # inserting partID and qty into the orderDetails table
        mysql -u"$user" -p"$pass" -D"$db" -e \
        "INSERT INTO orderDetails (orderID, partID, qty) VALUES ('$orderID', '$partID', '$qty');"
    done
done < "$ordersFile"