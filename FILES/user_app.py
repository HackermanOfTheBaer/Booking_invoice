#KÖR I CMD: Z:, python "Z:\DB kurs\projekt\user_app.py"
import user_sql as usr
import os
from datetime import datetime, timedelta
commands = ["KOMMANDON         -- FÖRKLARING\n____________________________________________",
            "lediga tider      -- VISAR ALLA LEDIGA TIDER",
            "boka              -- FÖR ATT BOKA IN PASS",
            "visa bokade tider -- VISA DINA BOKADE TIDER",
            "avboka            -- AVBOKA BOKA TID",
            "ändra bokning     -- ÄNDRA MEDDELANDE ELLER ADRESS I BOKNING",
            "help              -- LISTA KOMMANDON",
            "exit              -- STÄNGER AV PROGRAMMET EFTER 2ggr"]

def programet(Kund_id):
    os.system('cls')
    #print(Kund_id)
    print('VÄLKOMMEN\nFör hjälp skriv: help')
    while True:
        action = input().lower()
        #print(action)
        if "x" == action or "exit" == action:
            break
        #VISA TIDER
        elif "lediga tider" == action or action == "lt":
            os.system('cls')        #CLEAR TERMINAL 
            print("För att visa fler dagar eller ifrån annat datum,")
            func_in = input("Var god att ange datum och antal synliga dagar\nAnnars tryck enter: ")
            
            if func_in:
                if ' ' in func_in:
                    func1, func2 = func_in.split()
                    free = SHOW_FREE_BOOKINGS(func1, int(func2))
                else:
                    free = SHOW_FREE_BOOKINGS(func_in)
            else:
                free = SHOW_FREE_BOOKINGS()
            for booking in free:
                print(f"Date: {booking['date']}")
                for pass_info in booking['available_passes']:
                    print(f"  Pass Name: {pass_info[0]}, Start Time: {pass_info[1]}, Varaktighet: {pass_info[2]}H, Price: {pass_info[3]}")
        
        #BOKA
        elif "boka" == action or "b" == action:
            os.system('cls')        #CLEAR TERMINAL 
            BOKA(Kund_id)
            

        #Visa bokningar
        elif "visa bokade tider" == action or "bt" == action or "bokade tider" == action:
            os.system('cls')
            SHOW_BOOKINGS(Kund_id)
        
        #Avboka
        elif "avboka" == action or "ab" == action:
            os.system('cls')
            Avboka(Kund_id)
        
        #ÄNDRA
        elif "ändra bokning" == action or "ändra" == action:
            os.system('cls')
            Change_bokning(Kund_id)

        elif "help" == action or "h" == action:
            os.system('cls')
            for i in commands:
                print(i)
            print("____________________________________________")
        
        elif "vilkor" == action:
            print("VILKOR VID BOKNING:\n\nBokningar som har en adress som har längre kör tid än 1 timme\nifrån företagets huvud-adress kommer inte att genomföras om inte annat överenskommet\n")
            print("Avbokningar som sker samma datum som själv bokningen måste meddelas via telefon.\nVid utebliven bokning kommer det faktureras fullt pris.")

#_______________VISA LEDIGA TIDER ATT BOKA_______________
def SHOW_FREE_BOOKINGS(start_date = None, num_days=5):
    if start_date is None or start_date == "":
        start_date = datetime.now().date() + timedelta(days=1)
    else:
        # Försök omvandla start_date till ett datetime.date-objekt
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            if start_date < datetime.now().date() + timedelta(days=1):
                start_date = datetime.now().date() + timedelta(days=1)
        except ValueError:
            # Om det inte går att omvandla, använd defaultvärde (morgondagens datum)
            start_date = datetime.now().date() + timedelta(days=1)
    
    if num_days <= 0 or num_days > 100:
        num_days = 20
    #print(start_date)
    #print(type(start_date))
    end_date = None
    end_date = start_date + timedelta(days = num_days)
    free = usr.fetch_free_bookings(start_date, end_date, num_days)

    return free

#_______________BOKA NY TID_______________
def BOKA(Kund_ID):
    forsok = 0
    while forsok < 3:
        datum_b = input("Ange önskat datum YYYY-MM-DD: ")
        
        try:
            datum_b = datetime.strptime(datum_b, "%Y-%m-%d").date()
            if datum_b < datetime.now().date() + timedelta(days=1) or datum_b.weekday() >= 5:
                os.system('cls')
                print(f"GÅR INTE ATT BOKA DETTA DATUMET: {datum_b} SKICKAR TILL START")
                return -1 
            
            pass_b = input("Ange önskat pass: ")
            adress_b = input("Om annan address önskas ange annars trycke ENTER: ")
            message_b = input("ÖVERIGT MEDDELANDE alt tryck enter för att gå vidare: ")
            res = usr.book_time(Kund_ID,datum_b,pass_b,adress_b,message_b)
            break
        except ValueError as ve:
            print("Felaktigt datumformat. Vänligen ange datumet i formatet YYYY-MM-DD.")
            forsok += 1
    if forsok == 3:
        os.system('cls')
        print("Du har anget tre ogiltiga format för datum skickar tillbaka till start")
        return -1
    
    if res == 1:
        os.system('cls')
        print(f'BOKNINGEN {datum_b} PASS: {pass_b} GENOMFÖRD')
    else:
        print("SKICKAR TILL START")
    return

#_______________SE EGNA BOKNINGAR_______________
def SHOW_BOOKINGS(Kund_ID):
    today = datetime.now().date()   #DAGENS DATUM
    result = usr.show_c_bookings(Kund_ID, today)

    if result and result != -1:
        os.system('cls')
        print("Dina bokningar från och med", today)
        for booking in result:
            print("Boknings ID:", booking[0])
            print("Datum:      ", booking[1])
            print("Pass namn:  ", booking[2])
            print("Start tid:  ", booking[3])
            print("Pris pass:  ", booking[4])
            print("Adress:     ", booking[5])
            print("Meddelande: ", booking[6])
            print("--------------------------")
    else:
        os.system('cls')
        print("Inga bokningar hittades")

    return

#_______________Avboka_______________
def Avboka(Kund_ID):
    print("Vilket datum du vill avboka om du vill avboka allt\nSkriv: allt")
    forsok = 0
    while forsok < 3:
        in1 = input()
        if in1 == "allt":   #FÖR ATT AVBOKA ALLT
            res = usr.cancel_c_booking(Kund_ID)
            break
        else:               #FÖR ATT AVBOKA Ett datum ev ett av flera pass samma datum
            try:
                in1 = datetime.strptime(in1, "%Y-%m-%d").date()
                in2 = input("Om du vill bara avboka ett av flera pass skriv vilket: ")
                if in2 == '':
                    res = usr.cancel_c_booking(Kund_ID, in1)
                else:
                    res = usr.cancel_c_booking(Kund_ID, in1, in2)
                break
            except ValueError as ve:
                print("Felaktigt datumformat. Vänligen ange datumet i formatet YYYY-MM-DD.")
                forsok += 1
    if forsok == 3:
        print("Du har anget tre ogiltiga format för datum skickar tillbaka till start")
        return -1
    os.system('cls')
    if res == 2:
        print("AVBOKNINGARNA LYCKADES")
    elif res == 3:
        print(f"AVBOKNINGEN FÖR DATUMET {in1} LYCKADES")
    elif res == 4:
        print(f"AVBOKNINGEN FÖR {in1} PASS {in2} LYCKADES")
    elif res == -5:
        print("DU KAN INTE AVBOKA DETTA DATUM")
    return 1

def Change_bokning(Kund_ID):
    print('SKRIV "ADRESS" FÖR ATT ÄNDRA BOKNINGENS ADRESS OCH "Meddlande för Ändra/lägga till Meddelande" ')
    action2 = input().lower()
    if "adress" == action2:
        forsok = 0
        while forsok < 3:
            in1 = input("Bokningens datum: ")
            try:
                in1 = datetime.strptime(in1, "%Y-%m-%d").date()
                in2 = input("NYA ADRESSEN: ")
                usr.change_adress_booking(Kund_ID, in1, in2)
                break

            except ValueError as ve:
                print("Felaktigt datumformat. Vänligen ange datumet i formatet YYYY-MM-DD.")
                forsok += 1
        
        if forsok == 3:
            print("Du har anget tre ogiltiga format för datum skickar tillbaka till start")
            return -1
        os.system('cls')
        print("MEDDELANDET HAR ÄNDRATS")
        
    elif "meddelande" == action2 or "m" == action2:
        forsok = 0
        while forsok < 3:
            in3 = input("Bokningens datum: ")
            try:
                in3 = datetime.strptime(in3, "%Y-%m-%d").date()
                in4 = input("NYA MEDDELANDET: ")
                usr.change_message_booking(Kund_ID, in3, in4)
                break

            except ValueError as ve:
                print("Felaktigt datumformat. Vänligen ange datumet i formatet YYYY-MM-DD.")
                forsok += 1
        
        if forsok == 3:
            print("Du har anget tre ogiltiga format för datum skickar tillbaka till start")
            return -1
        os.system('cls')
        print("MEDDELANDET HAR ÄNDRATS")
        
        
    else:
        print("FELAKTIG INPUT")

    return

#_______________HUVUD-STARTEN DÄR MAN SÄGER VAD MAN SKA GÖRA_______________

def main_start():
    #SETTS GLOBAL Kund_ID
    os.system('cls')
    print("HEJ OCH VÄLKOMMEN\n")
    while True:
        action = input("    VAD ÖNSKAS ATT GÖRA?\n    SKREV DET DU ÖNSKAR ATT GÖRA\n    LOGGA IN\n    REGISTRERA\n\n    ")
        action = action.lower()
        if action == "logga in" or action == "1":
            os.system('cls')
            user_name = input("MAIL: ")
            passW = input("LÖSENORD: ")
            login = usr.login(user_name, passW)
            if login > 0:
                #start thread ny loop
                programet(login)
                os.system('cls')
            else:
                if login == -2:
                    os.system('cls')
                    print("\nKontot finns inte\n")
                else:
                    os.system('cls')
                    print("\nFELAKTIGT LÖSENORD\n")
                continue
        elif action == "registrera" or action == "2":
            fnamn = input("Förnamn: ")
            lnamn = input("Efternamn: ")
            Mail = input("Mail: ")
            adress = input("Adress: ")
            lösen = input("Lösenord: ")
            suc = usr.register_KUND(fnamn,lnamn,Mail,adress,lösen)
            print("\n")
            if suc[0] > 0:
                programet(suc[1])
        elif "x" == action or "exit" == action:
            break
        else:
            os.system('cls')
    #print("KUND_ID ", login)
    return

main_start()
