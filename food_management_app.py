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


# Sidebar Navigation
st.sidebar.title("Navigation")
options = [
    "Project Introduction",
    "View Table",
    "CRUD Operation",
    "SQL Queries & Visualization",
    "User Introduction"
]
choice = st.sidebar.selectbox("Go to", options)

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

# View table
elif choice == "View Table":
    st.title("View Tables") 
    table_choice = st.selectbox("Select Table", ["Providers", "Receivers", "Food Listings", "Claims"])
    
    table_map = {
        "Providers": "providers",
        "Receivers": "receivers",
        "Food Listings": "food_listings",
        "Claims": "claims"
    }

    try:
        query = f"SELECT * FROM {table_map[table_choice]}"
        df = pd.read_sql(query, conn)
        st.dataframe(df)
    except Exception as e:
        st.error(f"Error: {e}")

# CRUD Creation
elif choice == "CRUD Operation":
    st.title("CRUD Operations")
    crud_table = st.selectbox("Select Table", ["Providers", "Receivers", "Food Listings", "Claims"])
    cursor = conn.cursor()

    #providers
    if crud_table == "Providers":
        st.subheader("Add New Provider")
        name = st.text_input("Name")
        type_ = st.text_input("Type")
        address = st.text_input("Address")
        city = st.text_input("City")
        contact = st.text_input("Contact")
        if st.button("Add Provider"):
            try:
                cursor.execute("""
                    INSERT INTO providers (Name, Type, Address, City, Contact)
                    VALUES (%s,%s,%s,%s,%s)
                """, (name, type_, address, city, contact))
                conn.commit()
                st.success("Provider added successfully!")
            except Exception as e:
                st.error(f"Error: {e}")

    # receivers 
    elif crud_table == "Receivers":
        st.subheader("Add New Receiver")
        name = st.text_input("Name")
        type_ = st.text_input("Type")
        city = st.text_input("City")
        contact = st.text_input("Contact")
        if st.button("Add Receiver"):
            try:
                cursor.execute("""
                    INSERT INTO receivers (Name, Type, City, Contact)
                    VALUES (%s,%s,%s,%s)
                """, (name, type_, city, contact))
                conn.commit()
                st.success("Receiver added successfully!")
            except Exception as e:
                st.error(f"Error: {e}")

    # FOOD Listings
    elif crud_table == "Food Listings":
        st.subheader("Add New Food Listing")
        food_name = st.text_input("Food Name")
        quantity = st.number_input("Quantity", min_value=1)
        expiry = st.date_input("Expiry Date")
        provider_id = st.number_input("Provider ID", min_value=1)
        provider_type = st.text_input("Provider Type")
        location = st.text_input("Location")
        food_type = st.text_input("Food Type")
        meal_type = st.text_input("Meal Type")
        if st.button("Add Food Listing"):
            try:
                cursor.execute("""
                    INSERT INTO food_listings 
                    (Food_Name, Quantity, Expiry_Date, Provider_ID, Provider_Type, Location, Food_Type, Meal_Type)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                """, (food_name, quantity, expiry, provider_id, provider_type, location, food_type, meal_type))
                conn.commit()
                st.success("Food Listing added successfully!")
            except Exception as e:
                st.error(f"Error: {e}")

    #  Claims
    elif crud_table == "Claims":
        st.subheader("Add New Claim")
        food_id = st.number_input("Food ID", min_value=1)
        receiver_id = st.number_input("Receiver ID", min_value=1)
        status = st.selectbox("Status", ["Pending", "Approved", "Successful", "Canceled"])
        date_val = st.date_input("Date", datetime.date.today())
        timestamp = datetime.datetime.combine(date_val, datetime.datetime.now().time())
        if st.button("Add Claim"):
            try:
                cursor.execute("""
                    INSERT INTO claims (Food_ID, Receiver_ID, Status, Timestamp)
                    VALUES (%s,%s,%s,%s)
                """, (food_id, receiver_id, status, timestamp))
                conn.commit()
                st.success("Claim added successfully!")
            except Exception as e:
                st.error(f"Error: {e}")

    cursor.close()


# SQL Qeries Visualization 
elif choice == "SQL Queries & Visualization":
    st.title("SQL Queries & Visualization")

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

                if len(numeric_cols) > 0:
                    if len(string_cols) > 0:
                        st.bar_chart(df.set_index(string_cols[0])[numeric_cols])
                    else:
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
