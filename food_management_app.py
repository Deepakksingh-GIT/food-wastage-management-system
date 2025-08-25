import streamlit as st
import pandas as pd
import mysql.connector
import datetime


# DATABASE C0nfiguration
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "Deepak@121" 
DB_NAME = "FoodWastageDB"

@st.cache_resource
def get_connection():
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    return conn

conn = get_connection()


# sidebar navigation
st.sidebar.title("Navigation")
options = [
    "Project Introduction",
    "View Table",
    "Crud Operation",
    "Sql Queries & Visualization",
    "User Introduction"
]
choice = st.sidebar.selectbox("go to", options)


# Project Introduction
if choice == "Project Introduction":
    st.title("Local Food Wastage Management System")
    st.subheader("Project Overview")
    st.write("""
    This project is designed to reduce food wastage by connecting food providers 
    (restaurants, grocery stores) with receivers (NGOs, shelters, individuals).

    Key features:
    - View and manage providers, receivers, food listings, and claims
    - Analyze food distribution trends
    - Track claims and donations
    """)


# View Table
elif choice == "View Table":
    st.title("View Tables")
    table_choice = st.selectbox("Select Table", ["providers", "receivers", "food listings", "claims"])

    table_map = {
        "providers": "providers",
        "receivers": "receivers",
        "food listings": "food_listings",
        "claims": "claims"
    }

    try:
        query = f"SELECT * FROM {table_map[table_choice]}"
        df = pd.read_sql(query, conn)
        st.dataframe(df)
    except Exception as e:
        st.error(f"Error: {e}")


# CRUD Operation
elif choice == "Crud Operation":
    st.title("CRUD Operations")

    crud_table = st.selectbox("Select Table", ["providers", "receivers", "food listings", "claims"])
    crud_action = st.radio("Select Action", ["add", "update", "delete"])

    cursor = conn.cursor()

    if crud_action == "add":
        st.write(f"**Add new record in {crud_table}**")

        if crud_table == "providers":
            st.subheader("Add New Provider")
            with st.form("add_provider_form"):
                name = st.text_input("Provider Name")
                city = st.text_input("City")
                provider_type = st.selectbox("Provider Type", ["Restaurant", "Grocery", "Hotel"])
                submit = st.form_submit_button("Add Provider")

            if submit:
                try:
                    cursor.execute(
                        "INSERT INTO providers (name, city, provider_type) VALUES (%s, %s, %s)",
                        (name, city, provider_type)
                    )
                    conn.commit()
                    st.success("✅ Provider added successfully!")
                except Exception as e:
                    st.error(f"Error: {e}")

        elif crud_table == "receivers":
            st.subheader("Add New Receiver")
            with st.form("add_receiver_form"):
                name = st.text_input("Receiver Name")
                city = st.text_input("City")
                receiver_type = st.selectbox("Receiver Type", ["NGO", "Shelter", "Individual"])
                submit = st.form_submit_button("Add Receiver")

            if submit:
                try:
                    cursor.execute(
                        "INSERT INTO receivers (name, city, type) VALUES (%s, %s, %s)",
                        (name, city, receiver_type)
                    )
                    conn.commit()
                    st.success("✅ Receiver added successfully!")
                except Exception as e:
                    st.error(f"Error: {e}")

        elif crud_table == "food listings":
            st.subheader("Add New Food Listing")
            with st.form("add_food_form"):
                food_name = st.text_input("Food Name")
                quantity = st.number_input("Quantity", min_value=1)
                expiry_date = st.date_input("Expiry Date")
                provider_id = st.number_input("Provider ID", min_value=1)
                provider_type = st.text_input("Provider Type")
                location = st.text_input("Location")
                food_type = st.text_input("Food Type")
                meal_type = st.text_input("Meal Type")
                submit = st.form_submit_button("Add Food Listing")

            if submit:
                try:
                    cursor.execute(
                        """INSERT INTO food_listings 
                        (food_name, quantity, expiry_date, provider_id, provider_type, location, food_type, meal_type) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                        (food_name, quantity, expiry_date, provider_id, provider_type, location, food_type, meal_type)
                    )
                    conn.commit()
                    st.success("✅ Food listing added successfully!")
                except Exception as e:
                    st.error(f"Error: {e}")

        elif crud_table == "claims":
            st.subheader("Add New Claim")
            with st.form("add_claim_form"):
                food_id = st.number_input("Food ID", min_value=1)
                receiver_id = st.number_input("Receiver ID", min_value=1)
                status = st.selectbox("Status", ["Pending", "Successful", "Rejected"])
                timestamp = st.date_input("Timestamp", datetime.date.today())
                submit = st.form_submit_button("Add Claim")

            if submit:
                try:
                    cursor.execute(
                        "INSERT INTO claims (food_id, receiver_id, status, timestamp) VALUES (%s, %s, %s, %s)",
                        (food_id, receiver_id, status, timestamp)
                    )
                    conn.commit()
                    st.success("✅ Claim added successfully!")
                except Exception as e:
                    st.error(f"Error: {e}")

    elif crud_action == "update":
        st.write(f"**Update record in {crud_table}**")
        record_id = st.number_input(f"Enter {crud_table[:-1]} ID to update", min_value=1)

        table_columns = {
            "providers": ["name", "type", "address", "city", "contact"],
            "receivers": ["name", "type", "city", "contact"],
            "food listings": ["food_name", "quantity", "expiry_date", "provider_id", "provider_type", "location", "food_type", "meal_type"],
            "claims": ["food_id", "receiver_id", "status", "timestamp"]
        }

        column_to_update = st.selectbox("Column to Update", table_columns[crud_table])
        new_value = st.text_input("New Value")

        if st.button("Update Record"):
            if new_value.strip() == "":
                st.error("Please enter a valid new value.")
            else:
                if column_to_update in ["quantity", "provider_id", "receiver_id", "food_id"]:
                    try:
                        new_value = int(new_value)
                    except:
                        st.error("Please enter a numeric value for this column.")
                        cursor.close()
                        st.stop()

                try:
                    query = f"UPDATE {crud_table.replace(' ', '_')} SET {column_to_update} = %s WHERE {crud_table[:-1]}_id = %s"
                    cursor.execute(query, (new_value, record_id))
                    conn.commit()
                    st.success(f"{crud_table[:-1]} record updated successfully!")
                except Exception as e:
                    st.error(f"Error: {e}")

    elif crud_action == "delete":
        st.write(f"**Delete record from {crud_table}**")
        record_id = st.number_input(f"Enter {crud_table[:-1]} ID to delete", min_value=1)
        if st.button("Delete Record"):
            try:
                query = f"DELETE FROM {crud_table.replace(' ', '_')} WHERE {crud_table[:-1]}_id = %s"
                cursor.execute(query, (record_id,))
                conn.commit()
                st.success("Record deleted successfully!")
            except Exception as e:
                st.error(f"Error: {e}")

    cursor.close()


# sql queries visualization 
elif choice == "Sql Queries & Visualization":
    st.title("Sql Queries & Visualization")


    queries = {
        "1. Providers & Receivers by City": """
            SELECT city,
                   SUM(provider_count) as total_providers,
                   SUM(receiver_count) as total_receivers
            FROM (
                SELECT City as city, COUNT(Provider_ID) as provider_count, 0 as receiver_count 
                FROM Providers 
                GROUP BY City
                UNION ALL
                SELECT City as city, 0 as provider_count, COUNT(Receiver_ID) as receiver_count 
                FROM Receivers 
                GROUP BY City
            ) as combined
            GROUP BY city
        """,
        "2. Top Food Provider Type": """
            SELECT Provider_Type, SUM(Quantity) AS total_quantity
            FROM food_listings
            GROUP BY Provider_Type
            ORDER BY total_quantity DESC
            LIMIT 1
        """,
        "3. Contact Info of Providers in a City": """
            SELECT Name, Type, Address, Contact
            FROM Providers
            WHERE City = 'New Jessica'
        """,
        "4. Top Receivers by Claims": """
            SELECT r.Receiver_ID, r.Name, SUM(fl.Quantity) AS Total_Food_Claimed
            FROM claims c
            JOIN receivers r ON c.Receiver_ID = r.Receiver_ID
            JOIN food_listings fl ON c.Food_ID = fl.Food_ID
            GROUP BY r.Receiver_ID, r.Name
            ORDER BY Total_Food_Claimed DESC
        """,
        "5. Total Food Available": """
            SELECT SUM(Quantity) AS Total_Food_Available
            FROM food_listings
        """,
        "6. City with Highest Food Listings": """
            SELECT Location AS City, COUNT(*) AS Total_Listings
            FROM food_listings
            GROUP BY Location
            ORDER BY Total_Listings DESC
            LIMIT 1
        """,
        "7. Most Common Food Types": """
            SELECT Food_Type, COUNT(*) AS Total_Count
            FROM food_listings
            GROUP BY Food_Type
            ORDER BY Total_Count DESC
        """,
        "8. Claims per Food Item": """
            SELECT f.Food_ID, f.Food_Name, COUNT(c.Claim_ID) AS Total_Claims
            FROM food_listings f
            LEFT JOIN claims c ON f.Food_ID = c.Food_ID
            GROUP BY f.Food_ID, f.Food_Name
            ORDER BY Total_Claims DESC
        """,
        "9. Provider with Most Successful Claims": """
            SELECT p.Provider_ID, p.Name, COUNT(c.Claim_ID) AS Successful_Claims
            FROM providers p
            JOIN food_listings f ON p.Provider_ID = f.Provider_ID
            JOIN claims c ON f.Food_ID = c.Food_ID
            WHERE c.Status = 'Successful'
            GROUP BY p.Provider_ID, p.Name
            ORDER BY Successful_Claims DESC
            LIMIT 1
        """,
        "10. Food Claims Status Percentage": """
            SELECT Status,
                   CONCAT(ROUND((COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims)), 2), '%') AS Percentage
            FROM claims
            GROUP BY Status
        """,
        "11. Average Quantity of Food Claimed per Receiver": """
            SELECT r.Receiver_ID, r.Name, AVG(f.Quantity) AS Avg_Quantity_Claimed
            FROM Receivers r
            JOIN Claims c ON r.Receiver_ID = c.Receiver_ID
            JOIN Food_Listings f ON c.Food_ID = f.Food_ID
            GROUP BY r.Receiver_ID, r.Name
        """,
        "12. Most Claimed Meal Type": """
            SELECT f.Meal_Type, COUNT(*) AS Total_Claims
            FROM Claims c
            JOIN Food_Listings f ON c.Food_ID = f.Food_ID
            GROUP BY f.Meal_Type
            ORDER BY Total_Claims DESC
        """,
        "13. Total Quantity of Food Donated by Each Provider": """
            SELECT p.Provider_ID, p.Name, SUM(f.Quantity) AS Total_Quantity_Donated
            FROM Providers p
            JOIN Food_Listings f ON p.Provider_ID = f.Provider_ID
            GROUP BY p.Provider_ID, p.Name
            ORDER BY Total_Quantity_Donated DESC
        """,
        "14. Provider Type with Most Providers": """
            SELECT Type, COUNT(*) AS Total_Providers
            FROM Providers
            GROUP BY Type
            ORDER BY Total_Providers DESC
            LIMIT 1;
        """,
        "15. Total Receivers per City": """
            SELECT City, COUNT(*) AS Total_Receivers
            FROM Receivers
            GROUP BY City
            ORDER BY Total_Receivers DESC;
        """,
        "16. Top Receivers by Total Claims": """
            SELECT r.Receiver_ID, r.Name, COUNT(c.Claim_ID) AS Total_Claims
            FROM Receivers r
            JOIN Claims c ON r.Receiver_ID = c.Receiver_ID
            GROUP BY r.Receiver_ID, r.Name
            ORDER BY Total_Claims DESC
            LIMIT 5;
        """,
        "17. Average Food Quantity per Provider": """
            SELECT p.Provider_ID, p.Name, AVG(f.Quantity) AS Avg_Quantity
            FROM Providers p
            JOIN Food_Listings f ON p.Provider_ID = f.Provider_ID
            GROUP BY p.Provider_ID, p.Name
            ORDER BY Avg_Quantity DESC;
        """,
        "18. Food Types with Highest Claims": """
            SELECT f.Food_Type, COUNT(c.Claim_ID) AS Total_Claims
            FROM Food_Listings f
            JOIN Claims c ON f.Food_ID = c.Food_ID
            GROUP BY f.Food_Type
            ORDER BY Total_Claims DESC;
        """,
        "19. Top 5 Providers by Quantity Donated": """
            SELECT p.Provider_ID, p.Name, SUM(f.Quantity) AS Total_Quantity_Donated
            FROM Providers p
            JOIN Food_Listings f ON p.Provider_ID = f.Provider_ID
            GROUP BY p.Provider_ID, p.Name
            ORDER BY Total_Quantity_Donated DESC
            LIMIT 5;
        """,
        "20. Most Claimed Meal Types": """
            SELECT f.Meal_Type, COUNT(c.Claim_ID) AS Total_Claims
            FROM Food_Listings f
            JOIN Claims c ON f.Food_ID = c.Food_ID
            GROUP BY f.Meal_Type
            ORDER BY Total_Claims DESC;
        """,
        "21. Total Food Available": """
            SELECT SUM(Quantity) AS Total_Food
            FROM Food_Listings;
        """,
        "22. Total Successful Claims per City": """
            SELECT r.City, COUNT(c.Claim_ID) AS Successful_Claims
            FROM Receivers r
            JOIN Claims c ON r.Receiver_ID = c.Receiver_ID
            WHERE c.Status = 'Successful'
            GROUP BY r.City
            ORDER BY Successful_Claims DESC;
        """,
        "23. Most Recent Food Listings": """
            SELECT Food_ID, Food_Name, Provider_ID, Expiry_Date
            FROM Food_Listings
            ORDER BY Expiry_Date DESC
            LIMIT 10;
        """   
    }
    query_choice = st.selectbox("Select Query", list(queries.keys()))

    if st.button("Run Query"):
        try:
            df = pd.read_sql(queries[query_choice], conn)
            if df.empty:
                st.warning("Query executed but returned no data.")
            else:
                st.dataframe(df)

                # Visualization
                numeric_cols = df.select_dtypes(include='number').columns
                string_cols = df.select_dtypes(include='object').columns

                if len(numeric_cols) > 0 and len(string_cols) > 0:
                    x_col = string_cols[0]
                    chart_data = df.groupby(x_col)[numeric_cols].sum()
                    st.bar_chart(chart_data)
                elif len(numeric_cols) > 0:
                    st.bar_chart(df[numeric_cols])
        except Exception as e:
            st.error(f"Error: {e}")

#Introduction
elif choice == "User Introduction":
    st.title("User Introduction")
    st.write("Name: Deepak Kumar Singh")
    st.write("Location: Noida, Uttar Pradesh")
    st.write("Email: Deepakks7007@gmail.com")
    st.write("Learning Data Science and SQL, Python")
