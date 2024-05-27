import mysql.connector
import bcrypt
from datetime import datetime, timedelta
Salt = bytes(b'$2b$12$SDfvKZsx5rW/OYnLgeGlWu')
config = {
        'user': 'root',
        'password':'',
        'host': '127.0.0.1',
        'database': 'bokhäimr'}


#____HASH PASWORDS____
def hash_func(password):
    hashes_pas = bcrypt.hashpw(password.encode('utf-8'), Salt)
    return hashes_pas

#____________LOGIN FUNKTION_______________
def login(user, passW):
    passW = str(hash_func(passW))
    passW = passW[2:]
    passW = passW[:-1]

    try:
        # Skapa anslutning till databasen
        cnx = mysql.connector.connect(**config)

    # Kontrollera om anslutningen lyckades
        if cnx.is_connected():
            print('Anslutning lyckades till Databasen bokhäimr')

        cursor = cnx.cursor()

        login_query = "SELECT PassW FROM användare WHERE Username = %s"
        cursor.execute(login_query, (user,))
        Db_fetch = cursor.fetchone()
        print(Db_fetch)
        if Db_fetch is not None: 
            Db_PASS = Db_fetch[0]
        else:
            return -2
        # Stäng anslutningen
        cnx.close()
        print('Anslutningen har stängts')

    except mysql.connector.Error as err:
        print(f'Något gick fel: {err}')

    if Db_PASS == passW:
        return 1
    else:
        return -1

#_____________VISA BOKNINGAR_____________
def show_c_bookings(Kund_ID, datum, max_fram = (datetime.now().date() + timedelta(days=7))):
    bookings = None
    try:
        cnx = mysql.connector.connect(**config)
        if cnx.is_connected():
            
            cursor = cnx.cursor()

            fetch_query = """
                SELECT B.Bokning_ID, B.datum, P.PASS_NAMN, P.Start_tid, P.Pris_pass, B.Ut_adress, B.message, K.Fnamn, K.Lnamn, B.Kund_ID
                FROM bokningar B
                INNER JOIN PASS P ON B.Pass_ID = P.PASS_INT
                INNER JOIN Kunder K ON B.Kund_ID = K.Kund_ID
                WHERE datum >= %s AND datum <= %s
                ORDER BY datum
            """

            cursor.execute(fetch_query, (datum, max_fram))
            bookings = cursor.fetchall()



    except mysql.connector.Error as err:
        suc = -1
        print(f'Något gick fel: {err}')
        cnx.close()
        return -1
    finally:
        cnx.close()
        print(f'Anslutningen stängd')

    return bookings

#_____________AVOKA BOKNINGAR_____________
def cancel_c_booking(datum, Pass=None):
    value_mapping = {"morgon": 1, "middag" : 2, "kväll" : 3,"1": 1, "2" : 2, "3" : 3}
    if Pass != None:
        nummer_pass = value_mapping.get(Pass, None)    #TA REDA PÅ PASS_ID
    try:
        cnx = mysql.connector.connect(**config)
        if cnx.is_connected():
            cursor = cnx.cursor()
            print(Pass)
            if Pass == None:    #OM allt ska bort för ett datum
                delete_query1 = """
                        DELETE FROM bokningar
                        WHERE  datum = %s
                """
                cursor.execute(delete_query1, (datum,))
                cnx.commit()
                suc = 1

                LEDIG_SQL(datum)

            else:               #OM ett specifikt pass ska bort
                print("else")
                delete_query2 = """
                        DELETE FROM bokningar
                        WHERE datum = %s AND Pass_id = %s
                """
                cursor.execute(delete_query2, (datum, nummer_pass))
                cnx.commit()
                suc = 3
                LEDIG_SQL(datum, nummer_pass)
    
    except mysql.connector.Error as err:
        suc = -1
        print(f'Något gick fel: {err}')
        cnx.close()
        return -1
    finally:
        cnx.close()
        print(f'Anslutningen stängd')

    if suc == 1:
        return 2
    if suc == 3:
        return 4

#_____________SÄTT SOM LEDIG_____________
def LEDIG_SQL(datum, Pass=None):
    value_mapping = {"morgon": 1, "middag" : 2, "kväll" : 3,"1": 1, "2" : 2, "3" : 3}
    if Pass != None:
        nummer_pass = value_mapping.get(Pass, None)    #TA REDA PÅ PASS_ID
    try:
        
        cnx = mysql.connector.connect(**config)
        if cnx.is_connected():
            cursor = cnx.cursor()
            #print(Pass)
            if Pass == None:    #OM allt ska bort för ett datum
                i = 0
                while i != 3:       #BOKAR HELA DAGEN
                    args =(-1, datum, i+1, "LEDIG", "LEDIG")
                    cursor.callproc('new_booking',args) #PASS 1
                    i += 1

                cnx.commit()
                suc = 1

            else:               #OM ett specifikt pass ska bort
                #print("else")
                args =(-1, datum, nummer_pass, "LEDIG", "LEDIG")
                cursor.callproc('new_booking',args) #PASS 1
                
                cnx.commit()
                suc = 3
    
    except mysql.connector.Error as err:
        suc = -1
        print(f'Något gick fel: {err}')
        cnx.close()
        return -1
    finally:
        cnx.close()
        print(f'Anslutningen stängd')

    if suc == 1:
        return 2
    if suc == 3:
        return 4, nummer_pass
    return

#_____________AVBOKA LEDIGHET_____________
def cancel_ledig_booking(datum, Pass=None):
    value_mapping = {"morgon": 1, "middag" : 2, "kväll" : 3,"1": 1, "2" : 2, "3" : 3}
    if Pass != None:
        nummer_pass = value_mapping.get(Pass, None)    #TA REDA PÅ PASS_ID
    try:
        cnx = mysql.connector.connect(**config)
        if cnx.is_connected():
            cursor = cnx.cursor()
            print(Pass)
            if Pass == None:    #OM allt ska bort för ett datum
                delete_query1 = """
                        DELETE FROM bokningar
                        WHERE  datum = %s AND Kund_ID = -1
                """
                cursor.execute(delete_query1, (datum,))
                cnx.commit()
                suc = 1

            else:               #OM ett specifikt pass ska bort
                print("else")
                delete_query2 = """
                        DELETE FROM bokningar
                        WHERE datum = %s AND Pass_id = %s AND Kund_ID = -1
                """
                cursor.execute(delete_query2, (datum, nummer_pass))
                cnx.commit()
                suc = 3
    
    except mysql.connector.Error as err:
        suc = -1
        print(f'Något gick fel: {err}')
        cnx.close()
        return -1
    finally:
        cnx.close()
        print(f'Anslutningen stängd')

    if suc == 1:
        return 2
    if suc == 3:
        return 4

#_____________VISA FAKTUROR_____________
def show_invoices(date = datetime.now().date(), kund_ID = None ):      #DEFAULT DENNA MÅNADEN
    try:
        # Skapa anslutning till databasen
        cnx = mysql.connector.connect(**config)

    # Kontrollera om anslutningen lyckades
        if cnx.is_connected():
            print('Anslutning lyckades till Databasen bokhäimr')

        cursor = cnx.cursor()
        
        #______HÄMTA ALLA FAKTUROR FÖR GIVEN MÅNAD_____ 
        if kund_ID == None:
            invoice_query = """
                SELECT FAKTURA_ID, KUND_ID,AMOUNT,invoice_year, invoice_month
                FROM invoice
                WHERE invoice_year = YEAR(%s) AND 
                invoice_month = MONTH(%s) AND 
                Kund_ID <> -1;
                """

            cursor.execute(invoice_query, (date, date))
            Db_fetch = cursor.fetchall()

            #__FÖR ATT RÄKNA UT TOTALEN FÖR ANGIVEN MÅNAD__
            query_2 = """
                SELECT SUM(AMOUNT)
                FROM invoice
                WHERE invoice_year = YEAR(%s) AND 
                invoice_month = MONTH(%s) AND 
                Kund_ID <> -1        
                """
            
            cursor.execute(query_2, (date, date))
            summa = cursor.fetchone()
            summa = int(summa[0])

            Db_fetch.append(summa)

            if Db_fetch is None: 
                cnx.close()
                print('Anslutningen har stängts')
                return -2
        
        #______HÄMTA FÖR SPECIFIK KUND_______
        else:
            invoice_query = """
                SELECT FAKTURA_ID, KUND_ID,AMOUNT,invoice_year, invoice_month
                FROM invoice
                WHERE invoice_year = YEAR(%s) AND 
                invoice_month = MONTH(%s) AND 
                Kund_ID = %s;
                """

            cursor.execute(invoice_query, (date, date, kund_ID))
            Db_fetch = cursor.fetchall()
            if Db_fetch is None: 
                cnx.close()
                print('Anslutningen har stängts')
                return -2
        
        # Stäng anslutningen
        cnx.close()
        print('Anslutningen har stängts')

    except mysql.connector.Error as err:
        print(f'Något gick fel: {err}')

    return Db_fetch
