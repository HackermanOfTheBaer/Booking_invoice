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

        login_query = "SELECT Kund_ID, PassW FROM användare WHERE Username = %s"
        cursor.execute(login_query, (user,))
        Db_fetch = cursor.fetchone()
        if Db_fetch is not None:
            Kund_ID = Db_fetch[0] 
            Db_PASS = Db_fetch[1]
        else:
            return -2
        # Stäng anslutningen
        cnx.close()
        print('Anslutningen har stängts')

    except mysql.connector.Error as err:
        print(f'Något gick fel: {err}')

    if Db_PASS == passW:
        return Kund_ID
    else:
        return -1

#_____________REGGA NY KUND____________
def register_KUND(Fnamn, Lnamn, Mail, Adress, passW):
    suc = 1
    try:
        new_kund_id = 0
        args =(Fnamn, Lnamn, Mail, Adress)
        cnx = mysql.connector.connect(**config)
        
        if cnx.is_connected():
            print('Anslutning lyckades till Databasen bokhäimr')

            try:
                cursor = cnx.cursor()
                
                cursor.callproc('insert_ny_kund',args)
                
                kund_query = "SELECT Kund_ID FROM kunder WHERE Fnamn =%s AND Lnamn =%s AND Mail =%s AND Adress =%s"
                cursor.execute(kund_query,(Fnamn, Lnamn, Mail, Adress) )
                new_kund_id = cursor.fetchone()[0]
                cnx.commit()
                print(new_kund_id)
                if new_kund_id != 0:
                    register_LOGIN2(Mail, passW, new_kund_id, cnx)

            except mysql.connector.Error as proc_error:
                suc = -1
                if proc_error.errno == 1062:
                    print(f'Fel: E-postadressen {Mail} är redan registrerad.')
                else:
                    print(f'PROCEDURE GICK INTE ATT NÅ: {proc_error}')
                    cnx.rollback()
            finally:
                cursor.close()
        
    except mysql.connector.Error as err:
        suc = -1
        print(f'Något gick fel: {err}')
    finally:
        cnx.close()
        print(f'Anslutningen stängd')
    return suc, new_kund_id

def register_LOGIN2(user, passW, KuND_ID, cnx):
    passW = hash_func(passW)
    roll = "KUND"
    args =(user, passW, KuND_ID, roll)

    try:
        cursor = cnx.cursor()
        
        cursor.callproc('insert_user',args)
        
        cnx.commit()
    except mysql.connector.Error as proc_error:
        print(f'PROCEDURE GICK INTE ATT NÅ: {proc_error}')
        cnx.rollback()
    finally:
        cursor.close()

    return
#_____________HÄMTA LEDIGA TIDER_____________
def fetch_free_bookings(start_date, end_date, num_days):
    try:
        # Skapa anslutning till databasen
        cnx = mysql.connector.connect(**config)
        if cnx.is_connected():
            print('Anslutning lyckades till Databasen bokhäimr')
        cursor = cnx.cursor()
        available_bookings = []

        # Loopa genom varje datum i intervallet
        current_date = start_date
        while current_date < end_date:
            # Hämta alla pass från databasen för det aktuella datumet
            cursor.execute("SELECT PASS_NAMN, Start_tid, Varaktighet,Pris_pass FROM PASS WHERE PASS_INT NOT IN (SELECT Pass_ID FROM BOKNINGAR WHERE datum = %s) AND WEEKDAY(%s) BETWEEN 0 AND 4", (current_date,current_date))
            available_passes = cursor.fetchall()

            # Om det finns tillgängliga pass för det datumet, lägg till i resultatlistan
            if available_passes:
                available_bookings.append({
                    'date': current_date,
                    'available_passes': available_passes
                })
            else:
                #FALL den stötter på en helg ska den visa en dag längre fram än default så 7 resultat visas
                end_date += timedelta(days=1)
            # Gå till nästa datum
            current_date += timedelta(days=1)

    except mysql.connector.Error as err:
        print(f'Något gick fel: {err}')
    finally:
        cursor.close()
        cnx.close()
        print('Anslutningen har stängts')
    return available_bookings

#_____________BOKA IN TID_____________
def book_time(Kund_ID, datum, Pass_namn, Ut_address = None, message = None ):
    value_mapping = {"morgon": 1, "middag" : 2, "kväll" : 3,"1": 1, "2" : 2, "3" : 3}
    nummer_pass = value_mapping.get(Pass_namn, None)    #TA REDA PÅ PASS_ID

    suc = 1
    try:
        args =(Kund_ID, datum, nummer_pass, message, Ut_address)
        cnx = mysql.connector.connect(**config)
        
        if cnx.is_connected():
            print('Anslutning lyckades till Databasen bokhäimr')

            try:
                cursor = cnx.cursor()
                
                cursor.callproc('new_booking',args)
                
                check_query = """
                SELECT COUNT(*)
                FROM BOKNINGAR
                WHERE datum = %s AND Pass_ID = %s
                """
                cursor.execute(check_query, (datum, nummer_pass))
                result = cursor.fetchone()
                if result[0] > 1:   #CHECK IF THERE IS A BOOKING ALREADY AT WISHED BOOKING if true, return and withdraw bookings
                    print(f'Det finns redan en bokning för {datum} och pass {Pass_namn}.')
                    cnx.rollback()
                    cursor.close()
                    cnx.close()
                    return -1

                cnx.commit()
                
            except mysql.connector.Error as proc_error:
                suc = -1
                print(f'PROCEDURE GICK INTE ATT NÅ: {proc_error}')
                cnx.rollback()
            finally:
                cursor.close()
        
    except mysql.connector.Error as err:
        suc = -1
        print(f'Något gick fel: {err}')
    finally:
        cnx.close()
        #print(f'Anslutningen stängd')
    return suc

#_____________VISA BOKNINGAR_____________
def show_c_bookings(Kund_ID, datum):
    bookings = None
    try:
        cnx = mysql.connector.connect(**config)
        if cnx.is_connected():
            
            cursor = cnx.cursor()

            fetch_query = """
                SELECT Bokning_ID, datum, PASS_NAMN, Start_tid, Pris_pass, Ut_adress, message
                FROM bokningar
                INNER JOIN PASS ON BOKNINGAR.Pass_ID = PASS.PASS_INT
                WHERE Kund_ID = %s AND datum >= %s
                ORDER BY datum
            """

            cursor.execute(fetch_query, (Kund_ID, datum))
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
def cancel_c_booking(Kund_id, date=None, Pass=None):
    value_mapping = {"morgon": 1, "middag" : 2, "kväll" : 3,"1": 1, "2" : 2, "3" : 3}
    if Pass != None:
        nummer_pass = value_mapping.get(Pass, None)    #TA REDA PÅ PASS_ID
    try:
        cnx = mysql.connector.connect(**config)
        if cnx.is_connected():
            cursor = cnx.cursor()
            print(Pass)
            if date == None:    #OM allt ska bort
                date = datetime.now()
                delete_query1 = """
                        DELETE FROM bokningar
                        WHERE Kund_ID = %s AND datum > %s
                """
                cursor.execute(delete_query1, (Kund_id, date))
                cnx.commit()
                suc = 1
            
            elif Pass == None:  #OM allt samma dag ska bort
                print("HEJSAN")
                if date <= datetime.now().date():
                    return -5
                
                delete_query2 = """
                        DELETE FROM bokningar
                        WHERE Kund_ID = %s AND datum = %s
                """
                cursor.execute(delete_query2, (Kund_id, date))
                cnx.commit()
                suc = 2

            else:               #OM ett specifikt pass ska bort
                print("else")
                if date <= datetime.now().date():
                    return -5
                delete_query3 = """
                        DELETE FROM bokningar
                        WHERE Kund_ID = %s AND datum = %s AND Pass_id = %s
                """
                cursor.execute(delete_query3, (Kund_id, date, nummer_pass))
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
    if suc == 2:
        return 3
    if suc == 3:
        return 4

#_____________ÄNDRA ADRESS_____________
def change_adress_booking(Kund_id, date, adress):
    try:
        # Skapa anslutning till databasen
        cnx = mysql.connector.connect(**config)

    # Kontrollera om anslutningen lyckades
        if cnx.is_connected():
            print('Anslutning lyckades till Databasen bokhäimr')
            cursor = cnx.cursor()

            update_query = """
            UPDATE bokningar
            SET Ut_adress = %s
            Where Kund_ID = %s AND datum = %s
            """

            cursor.execute(update_query, (adress, Kund_id, date))
            if cursor.rowcount == 0:
                    print("Ingen bokning matchar de angivna kriterierna.")
                    cnx.rollback()
            else:
                cnx.commit()
                print("Adressen har uppdaterats.")

    except mysql.connector.Error as err:
        print(f'Något gick fel: {err}')
    finally:
        cnx.close()
        print('Anslutningen stängd')
    return

#_____________ÄNDRA ELLER LÄGGA TILL MEDDELANDE_____________
def change_message_booking(Kund_id, date, message):
    try:
        # Skapa anslutning till databasen
        cnx = mysql.connector.connect(**config)

    # Kontrollera om anslutningen lyckades
        if cnx.is_connected():
            print('Anslutning lyckades till Databasen bokhäimr')
            cursor = cnx.cursor()

            update_query = """
            UPDATE bokningar
            SET message = %s
            Where Kund_ID = %s AND datum = %s
            """

            cursor.execute(update_query, (message, Kund_id, date))
            if cursor.rowcount == 0:
                    print("Ingen bokning matchar de angivna kriterierna.")
                    cnx.rollback()
            else:
                cnx.commit()
                print("Adressen har uppdaterats.")

    except mysql.connector.Error as err:
        print(f'Något gick fel: {err}')
    finally:
        cnx.close()
        print('Anslutningen stängd')
    return
