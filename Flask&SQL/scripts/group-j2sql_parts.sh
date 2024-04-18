#!/bin/bash

# MySQL credentials and database name
user="u##"
pass="passwordGoesHere"
db="u##"

# paths to JSON files
partsFile="./parts_100.json"

parseJson() {
    python3 -c "import json, sys; [print(json.dumps(obj)) for obj in json.load(sys.stdin)]"
}

while IFS= read -r parts; do
    partID=$(echo $parts | python3 -c "import json; obj=json.loads(input()); print(obj['_id'])")
    price=$(echo $parts | python3 -c "import json; obj=json.loads(input()); print(obj['price'])")
    description=$(echo $parts | python3 -c "import json; obj=json.loads(input()); print(obj['description'])")
    
    # inserting supplierID, name, and email into the suppliers table
    mysql -u"$user" -p"$pass" -D"$db" -e \
    "INSERT INTO parts (partID, price, description) VALUES ('$partID', '$price', '$description');"
done < "$partsFile"