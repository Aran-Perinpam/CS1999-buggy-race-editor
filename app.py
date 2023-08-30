from flask import Flask, render_template, request, jsonify
import os
import sqlite3 as sql

# app - The flask application where all the magical things are configured.
app = Flask(__name__)

# Constants - Stuff that we need to know that won't ever change!
DATABASE_FILE = "database.db"
DEFAULT_BUGGY_ID = "1"
BUGGY_RACE_SERVER_URL = "https://rhul.buggyrace.net"

#------------------------------------------------------------
# the index page
#------------------------------------------------------------
@app.route('/')
def home():
    return render_template('index.html', server_url=BUGGY_RACE_SERVER_URL)

@app.route('/info')
def information():
    return render_template("info.html")

#------------------------------------------------------------
# creating a new buggy:
#  if it's a POST request process the submitted data
#  but if it's a GET request, just show the form
#------------------------------------------------------------

@app.route('/new', methods=['POST', 'GET'])
def create_buggy():
    if request.method == 'GET':
        return render_template("buggy-form.html", msg="")
   
    elif request.method == 'POST':
        msg = ""
        qty_wheels = request.form.get('qty_wheels')
        flag_color = request.form.get('flag_color')
        cost_limit = request.form.get('cost_limit')

        if not cost_limit:
             cost_limit = 0

        if 'fill_entries' in request.form:
            if cost_limit and cost_limit.strip():
                try:
                    cost_limit = float(cost_limit)
                except ValueError:
                    msg = "Invalid input. Please enter a valid number for the cost limit."
                    return render_template("buggy-form.html", msg=msg)
             
                if cost_limit < 0:
                    msg = "Invalid input. Cost limit cannot be negative."
                    return render_template("buggy-form.html", msg=msg)
             
                qty_wheels  = max(4, int(cost_limit // 10))
                total_cost = calculate_total_cost(qty_wheels)
                while total_cost > cost_limit:
                    qty_wheels = max(4, qty_wheels - 2)
                    total_cost = calculate_total_cost(qty_wheels)
                flag_color = "red"
            else:
                 msg = "Please enter a value for the cost limit before using Fill Entries"
                 return render_template("buggy-form.html", msg=msg)
        
        print("Qty wheels:", qty_wheels)
        print("Flag colour:", flag_color)

        try:
            qty_wheels = int(qty_wheels)
            if qty_wheels % 2 != 0:
                 msg = "Invalid input. The quantity of wheels must be even."
                 return render_template("buggy-form.html", msg=msg)  

            if qty_wheels < 4:
                 msg = "Invalid input. The quantity of wheels must be equal to or above 4."
                 return render_template("buggy-form.html", msg=msg)
            
        except ValueError:
                msg = "Invalid input. Please enter an integer for the quantity of wheels."
                return render_template("buggy-form.html", msg=msg)    
        
        if flag_color.isdigit() or len(flag_color) <= 1:
                msg = "Invalid input. Please enter a valid colour not an integer for the Colour of flag."
                return render_template("buggy-form.html", msg=msg)
        
        total_cost = calculate_total_cost(qty_wheels)
               
        try:
            print("Attempting to connect to the database:", DATABASE_FILE)
            with sql.connect(DATABASE_FILE) as con:
                print("Connected to the database:", DATABASE_FILE)
                cur = con.cursor()

                try:
                    cur.execute(
                        "UPDATE buggies SET qty_wheels=?, flag_color=?, total_cost=? WHERE id=?",
                        (qty_wheels, flag_color, total_cost, DEFAULT_BUGGY_ID)
                    )
                    con.commit()
                    msg = "Record successfully saved"
                except Exception as e:
                    con.rollback()
                    msg = "Error in the update operation: " + str(e)
        


        except sql.Error as e:
            msg = "Error connecting to the database: " + str(e)
              
        return render_template("updated.html", msg=msg)

def calculate_total_cost(qty_wheels):
     cost_qty_wheels = 10
     cost_flag = 20

     total_cost = (cost_qty_wheels * qty_wheels) + cost_flag
     return total_cost

def update_total_cost(buggy_id, total_cost):
     try:
          with sql.connect(DATABASE_FILE) as con:
               cur = con.cursor()
               cur.execute("UPDATE buggies SET total_cost=? WHERE id=?", (total_cost, buggy_id))
               con.commit()
               msg = "Total cost updated successfully"
     except:
          con.rollback()
          msg = "Error updating total cost"
     finally:
          con.close()
    
     return msg

#------------------------------------------------------------
# a page for displaying the buggy
#------------------------------------------------------------
@app.route('/buggy')
def show_buggies():
    con = sql.connect(DATABASE_FILE)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM buggies WHERE id=?", (DEFAULT_BUGGY_ID,))
    record = cur.fetchone();
    con.close()

    qty_wheels = record['qty_wheels'] 

    total_cost = calculate_total_cost(qty_wheels)

    return render_template("buggy.html", buggy = record, total_cost=total_cost)

#------------------------------------------------------------
# a placeholder page for editing the buggy: you'll need
# to change this when you tackle task 2-EDIT
#------------------------------------------------------------
@app.route('/edit')
def edit_buggy():
    try:
        con = sql.connect(DATABASE_FILE)
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM buggies WHERE id=?", (DEFAULT_BUGGY_ID,))
        record = cur.fetchone()

        qty_wheels = record['qty_wheels']
        flag_color = record['flag_color']

        con.close()

        return render_template("buggy-form.html", qty_wheels=qty_wheels, flag_color=flag_color, record=record)
    except:
         return "An error  occurred while fetching the buggy information."
#------------------------------------------------------------
# You probably don't need to edit this... unless you want to ;)
#
# get JSON from current record
#  This reads the buggy record from the database, turns it
#  into JSON format (excluding any empty values), and returns
#  it. There's no .html template here because it's *only* returning
#  the data, so in effect jsonify() is rendering the data.
#------------------------------------------------------------
@app.route('/json')
def summary():
    con = sql.connect(DATABASE_FILE)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM buggies WHERE id=? LIMIT 1", (DEFAULT_BUGGY_ID))

    buggies = dict(zip([column[0] for column in cur.description], cur.fetchone())).items() 
    return jsonify({ key: val for key, val in buggies if (val != "" and val is not None) })

# You shouldn't need to add anything below this!
if __name__ == '__main__':
    alloc_port = os.environ.get('CS1999_PORT') or 5000
    app.run(debug=True, host="0.0.0.0", port=alloc_port)

