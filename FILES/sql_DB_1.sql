CREATE TABLE Kunder( Kund_ID INT auto_increment, Fnamn varchar(128) NOT NULL, Lnamn varchar(128) NOT NULL, Mail varchar(256) NOT NULL, Adress varchar(256) NOT NULL,
primary key(Kund_ID));

CREATE TABLE Användare(Username varchar(256) NOT NULL, PassW varchar(512) NOT NULL, Kund_ID INT NOT NULL, Roll varchar(20),
primary key(Username), foreign key(Kund_ID) references Kunder(Kund_ID));
 

CREATE TABLE BOKNINGAR (Bokning_ID INT AUTO_INCREMENT PRIMARY KEY, Kund_ID INT, datum DATE NOT NULL, Pass_ID INT,
 message varchar(512), Ut_adress varchar(256), foreign key (Kund_ID) REFERENCES kunder(Kund_ID) ON UPDATE CASCADE);

Create table PASS (PASS_INT INT, Varaktighet int, Start_tid TIME, PASS_NAMN varchar(12),Pris_pass INT, Primary key(PASS_INT));

CREATE TABLE invoice (FAKTURA_ID INT AUTO_INCREMENT PRIMARY KEY, Boknings_ID TEXT NOT NULL, Kund_ID INT NOT NULL,
	AMOUNT DECIMAL(10,2) NOT NULL, last_modi TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    invoice_year INT NOT NULL, invoice_month INT NOT NULL, FOREIGN KEY (Kund_ID) REFERENCES Kunder(Kund_ID));

DELIMITER //
CREATE TRIGGER set_default_ut_adress		#TRIGGER FÖR ATT SÄTTA DEFAULT ADRESS OM INGET ANNAT ANGES VID BOKNING
BEFORE INSERT ON bokningar
FOR EACH ROW
BEGIN
    DECLARE kund_adress VARCHAR(256);
    
    -- Hämta Kundens Adress baserat på Kund_ID
    SELECT Adress INTO kund_adress
    FROM Kunder
    WHERE Kund_ID = NEW.Kund_ID;
    
    -- Sätt defaultvärdet för Ut_adress om inget värde har specificerats
    IF NEW.Ut_adress IS NULL OR NEW.Ut_adress = '' THEN
        SET NEW.Ut_adress = COALESCE(kund_adress, '');  -- Använd Kundens adress om tillgänglig, annars sätt till tom sträng
    END IF;
END//
DELIMITER ;

#__________________TRIGGER FÖR ATT ADDERA TILL MÅNADSFAKTURA FÖR KUNDEN VID BOKNING_____________
DELIMITER //
CREATE TRIGGER auto_invoice
AFTER INSERT ON bokningar
FOR EACH ROW
BEGIN
    DECLARE ID INT;
    declare tem_PASS_ID INT;
    
    SELECT FAKTURA_ID INTO ID from invoice 
	WHERE Kund_ID = NEW.Kund_ID AND invoice_month = MONTH(NEW.datum) AND invoice_year = YEAR(NEW.datum);
    
    SELECT Pris_pass INTO tem_PASS_ID from PASS
    WHERE PASS_INT = NEW.Pass_ID;
    
    IF ID IS NULL THEN
		INSERT INTO invoice(Kund_ID, AMOUNT, invoice_year, invoice_month)
        VALUES (NEW.Kund_ID, tem_PASS_ID, YEAR(NEW.datum), MONTH(NEW.datum));
	ELSE
		UPDATE invoice
        SET AMOUNT = AMOUNT + tem_PASS_ID
        WHERE FAKTURA_ID = ID;
	END IF;
END//
DELIMITER ;

#___________________TRIGER FÖR ATT RÄKNA BORT AVBOKADE PASS FRÅN TOTALEN__________
DELIMITER //
CREATE TRIGGER auto_neg_invoice
AFTER DELETE ON bokningar
FOR EACH ROW
BEGIN
	DECLARE ID INT;
    DECLARE pris INT;
    DECLARE new_AMOUNT INT;
    
    SELECT FAKTURA_ID INTO ID from invoice
    WHERE KUND_ID = OLD.Kund_ID AND invoice_month = MONTH(OLD.datum) AND invoice_year = YEAR(OLD.datum);
	
    SELECT Pris_pass INTO pris
    FROM PASS
    WHERE PASS.PASS_INT = OLD.Pass_ID;
    
    IF ID IS NOT NULL THEN
		SET new_AMOUNT = (SELECT amount FROM invoice WHERE FAKTURA_ID = ID AND invoice_month = MONTH(OLD.datum) 
        AND invoice_year = YEAR(OLD.datum)) - pris;
		
        IF new_AMOUNT <= 0 THEN
			DELETE FROM invoice WHERE FAKTURA_ID = ID;
		ELSE
			UPDATE invoice
            SET AMOUNT = new_AMOUNT
            WHERE FAKTURA_ID = ID;
		END IF;
	END IF;
END //
DELIMITER ;

#______TESTER AV INSERT______
insert into kunder (Fnamn, Lnamn, Mail, Adress)	#VID ATT SÄTTA IN LEDIGA DAGAR ELLER PASS I FÖRHAND
	Values ("LEDIG", "LEDIG", "LEDIG", "LEDIG");
update kunder set kund_ID = -1 WHERE kund_ID = 21;		#sätt den ny insatta kundbilden till -1 i id. Mitt fall hade den 21 innan jag bytte


SET FOREIGN_KEY_CHECKS = 0;    
insert into användare (Username, PassW, kund_ID, Roll)
	values('admin', '$2b$12$SDfvKZsx5rW/OYnLgeGlWuTZH.5tAG12t4Knk0cAkJ4IJbYSgXtju', 0, "ADMIN");
SET FOREIGN_KEY_CHECKS = 1; 
 
insert into kunder (Fnamn, Lnamn,mail,adress)
	values('Håkan', 'Lars', 'HEJSAN.com', "GATAN");
    
insert into bokningar (Kund_ID, datum, pass, pass_längd, state, message, ut_adress)
	values(2,'2024-05-15', 'mor', '12:00:00', 1, 'Test2', '123 Main Street');
insert into bokningar (Kund_ID, datum, pass, pass_längd, state, message)
	values(2,'2024-05-15', 'mor', '2', 1, 'Test3');
    
#Sätter int de för definerade passen.
insert into pass (PASS_INT, Varaktighet, Start_tid, PASS_NAMN, Pris_pass)
	values(1, 3, '8:00:00', 'morgon', 949), (2,3,'12:00:00','middag',949), (3,2,'17:00:00', 'kväll',674);



#____________SKAPA PROCEDURE FÖR LÄTTARE STANDARD SKAPANDE AV KUNDER o användare______
DELIMITER //
#FÖR NY KUND BILD
Create procedure insert_ny_kund(
	IN fnamn varchar(128), IN lnamn varchar(128), IN mail varchar(256), In adress varchar(256), OUT new_kund_ID INT)
BEGIN
	INSERT INTO kunder ( Fnamn, Lnamn, Mail, Adress)
		VALUES(fnamn, lnamn, mail, adress);
END//

create procedure insert_user(
	IN username varchar(256), IN passw varchar(512), IN kund_id INT, IN roll varchar(20))
BEGIN
	INSERT INTO användare (Username, PassW, Kund_ID, Roll)
		VALUES(username, passw, kund_id, roll);
END //
DELIMITER ;

DELIMITER //
create procedure new_booking (
	IN Ikund_ID INT, IN IDATUM DATE, IN IPass_ID INT, IN IMessage VARCHAR(512), IN IUt_adress VARCHAR(256))
BEGIN
	IF IUT_adress IS NOT NULL THEN
		INSERT INTO bokningar (Kund_ID, datum, Pass_ID, State, message, Ut_adress)
			VALUES(Ikund_ID, IDATUM, IPass_ID, IState, IMessage, IUt_adress);
	ELSE
		INSERT INTO bokningar (Kund_ID, datum, Pass_ID, State, message)
			VALUES(Ikund_ID, IDATUM, IPass_ID, IState, IMessage);
	END IF;
END //
DELIMITER ;
