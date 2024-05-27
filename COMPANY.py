import com_sql as usr
import os
from datetime import datetime, timedelta

def programet(Kund_id):
    os.system('cls')
    print(Kund_id)
    while True:
        action = input().lower()
        #print(action)
        if "x" == action:
            break
        #Visa bokningar
        elif "visa bokade tider" == action or "bt" == action or "bokade tider" == action:
            os.system('cls')
            SHOW_BOOKINGS(Kund_id)
        
        #Avboka
        elif "avboka" == action or "ab" == action:
            os.system('cls')
            Avboka()
        
        #SÄTT LEDIG DAG/PASS
        elif "ledig" == action or "l" == action:
            os.system('cls')
            LEDIG()

        #AVBOKA LEDIGHET
        elif "avboka ledighet" == action or "al" == action:
            os.system('cls')
            inte_ledig()
        
        #SE FAKTURA TOTALT OCH FÖR KUNDER
        elif "faktura" == action or "fk" == action:
            os.system('cls')
            show_invoice()

#_______________SE BOKNINGAR_______________
def SHOW_BOOKINGS(Kund_ID):
    print("HUR MÅNGA DAGAR FRAMÅT VILL DU SE ?\nTRYCK ENTER FÖR EN VECKA FRAMÅT")
    fram = input()
    
    today = datetime.now().date()   #DAGENS DATUM
    if fram != "":
        fram = int(fram)
        fram = datetime.now().date() + timedelta(days= fram)
        result = usr.show_c_bookings(Kund_ID, today, fram)
    else:
        result = usr.show_c_bookings(Kund_ID, today)

    if result and result != -1:
        os.system('cls')
        print("Dina kund bokningar från och med", today)
        for booking in result:
            if booking[7] == "LEDIG" and booking[8] == "LEDIG":
                print("Datum:      ", booking[1])
                print("Pass namn:  ", booking[2])
                print("Start tid:  ", booking[3])
                print("Kund:       ", booking[7])
                print("Adress:     ", booking[5])
                print("Meddelande: ", booking[6])
                print("Boknings ID:", booking[0])
                print("--------------------------")
            else:
                print("Boknings ID:", booking[0])
                print("Datum:      ", booking[1])
                print("Pass namn:  ", booking[2])
                print("Start tid:  ", booking[3])
                print("Pris pass:  ", booking[4])
                print("Kund:       ", booking[7], booking[8])
                print("Adress:     ", booking[5])
                print("Meddelande: ", booking[6])
                print("--------------------------")
    else:
        os.system('cls')
        print("Inga bokningar hittades")

    return

#_______________Avboka PASS FÖR KUND_______________
def Avboka():
    print("Vilket datum du vill avboka om du vill avboka allt för en dag\nSkriv: allt")
    forsok = 0
    while forsok < 3:
        in1 = input()
        if in1 == "allt":   #FÖR ATT AVBOKA ALLT
            datum = input("ANGE VILKET DATUM DU VILL AVBOKA: ")
            try:
                datum = datetime.strptime(datum, "%Y-%m-%d").date()
                res = usr.cancel_c_booking(datum)
                break
            except ValueError as ve:
                print("Felaktigt datumformat. Vänligen ange datumet i formatet YYYY-MM-DD.")
                forsok += 1
            
            break
        else:               #FÖR ATT AVBOKA Ett datum ev ett av flera pass samma datum
            try:
                in1 = datetime.strptime(in1, "%Y-%m-%d").date()
                in2 = input("Ange vilket pass som ska avbokas: ")
                res = usr.cancel_c_booking(in1, in2)
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
    elif res == 4:
        print(f"AVBOKNINGEN FÖR {in1} PASS {in2} LYCKADES")
    return 1

#_______________SÄTTA LEDIG DAG_______________
def LEDIG():
    in1 = input("SKRIV IN VILKET DATUM DU TÄNKER VARA LEDIG: ")
    in2 = input("Vilket Pass?\nOM hel dag tryck bara enter: ")
    in1 = datetime.strptime(in1, "%Y-%m-%d").date()
    
    if in2 == "":   #OM HELA DAGEN SKA FAKE BOKAS
        res = usr.LEDIG_SQL(in1)
        os.system('cls')
    else:           #OM BARA ETT PASS SKA FAKE BOKAS
        res = usr.LEDIG_SQL(in1, in2)
        os.system('cls')
    if res == 2:
        print("DAGEN SATT SOM LEDIG")
    if res[0] == 4:
        print(f"PASSET {res[1]} SATT SOM LEDIG")
    return

#_______________AVBOKA LEDIGHET_______________
def inte_ledig():
    print("Vilket datum vill du avboka ledighet, om du vill avboka allt för en dag\nSkriv: allt")
    forsok = 0
    while forsok < 3:
        in1 = input()
        if in1 == "allt":   #FÖR ATT AVBOKA ALLT
            datum = input("ANGE VILKET DATUM DU VILL AVBOKA: ")
            try:
                datum = datetime.strptime(datum, "%Y-%m-%d").date()
                res = usr.cancel_ledig_booking(datum)
                break
            except ValueError as ve:
                print("Felaktigt datumformat. Vänligen ange datumet i formatet YYYY-MM-DD.")
                forsok += 1
            
            break
        else:               #FÖR ATT AVBOKA Ett datum ev ett av flera pass samma datum
            try:
                in1 = datetime.strptime(in1, "%Y-%m-%d").date()
                in2 = input("Ange vilket pass som ska avbokas: ")
                res = usr.cancel_ledig_booking(in1, in2)
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
    elif res == 4:
        print(f"AVBOKNINGEN FÖR {in1} PASS {in2} LYCKADES")
    return 1

#_______________SE FAKTURA_______________
def show_invoice():
    year = datetime.now().year
    datee = input("SKRIV in vilken månad du vill se, för denna månad tryck ENTER:\n")
    os.system('cls')
    if datee == "": #UTAN KUND_ID o current månad
        res = usr.show_invoices()
    else:
        datee = int(datee)    
        datum = datetime(year,datee,1).date()
        in2 = input("SKRIV IN VILKET KUND ID.\nFÖR TOTALEN FÖR MÅNADEN TRYCK ENBART ENTER:\n")

        if in2 == "":   #UTAN KUND_ID
            res = usr.show_invoices(datum,)
        else:           #MED KUND_ID
            in2 = int(in2)
            res = usr.show_invoices(datum, in2)

    if res != -2:
        leng = len(res)-1
        not_leng = 0
        print("----------------------")
        for i in res:
            print("FAKTURA ID: ", i[0])
            print("KUND_ID:    ",  i[1])
            print("SUMMA:      ", i[2])
            print("MÅNAD:      ", i[4])
            print("ÅRTAL:      ", i[3])
            print("----------------------")
            not_leng +=1
            if not_leng == leng:
                break 
        print("MÅNADENS TOTAL:",res[2],"\n______________________")     #TOTALEN
    return

#_______________HUVUD-STARTEN DÄR MAN SÄGER VAD MAN SKA GÖRA_______________

def main_start():
    #SETTS GLOBAL Kund_ID
    os.system('cls')
    print("HEJ OCH VÄLKOMMEN, SKREV DET DU ÖNSKAR ATT GÖRA\n LOGGA IN")
    while True:
        os.system('cls')
        print("VÄLKOMMEN")
        user_name = input("ANVÄNDAR NAMN: ")
        if "x" == user_name.lower():
            break
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

            os.system('cls')
    #print("KUND_ID ", login)
    return

main_start()