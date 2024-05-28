#	    BOOKING_SYTEM		      #
Simple booking system that helps company to keep track of invoices related to bookings.

This software is written in Python 3.12.3.

Everything in the project related to SQL is written in MySQL 8.0.36.

## FILES
- **com_sql.py**: Contains SQL queries for all Company actions.
- **user_sql.py**: Contains SQL queries for all user actions.
- **user_app.py**: Main program for customers.
- **COMPANY.py**: Main program for company users.


## Dependencies
- MySQL Connector Python: Used to connect Python to MySQL databases.

## How to Run
1. Install the necessary dependencies using `pip install mysql-connector-python`.
2. Set up a MySQL database and configure the connection details in `user_sql.py` and `com_sql.py`.
3. Run all the queris inside `sql_DB_1.sql` to setup all the tables, procedures and triggers, this also generates two test users.
6. Run `python user_app.py` or `python COMPANY.py` to start the program.



## License

This project is licensed under the Creative Commons Attribution-NonCommercial 4.0 International License -see the [LICENSE](LICENSE) file for details.


## Creators
- Mikael Strandlund
