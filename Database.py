import mysql.connector
class Database:
    
    def __init__(self):
        self.initializeDatabase()
        self.initializeWordsTable()
        self.initializeFontsTable()

    def initializeDatabase(self):
        database = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="WriteBot"
        )

        cursor = database.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS WriteBot")
        
        self.database = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="WriteBot",
            database="WriteBot"
        )
        return

    def initializeWordsTable(self):
        self.database.cursor().execute("CREATE TABLE IF NOT EXISTS words (id INT AUTO_INCREMENT PRIMARY KEY, word VARCHAR(8000))")
        return

    def initializeFontsTable(self):
        self.database.cursor().execute("CREATE TABLE IF NOT EXISTS fonts (id INT AUTO_INCREMENT PRIMARY KEY, fontName VARCHAR(8000))")
        return

    def storeWord(self, str):
        sql = "INSERT INTO words(word) VALUES (%s)"
        self.database.cursor().execute(sql, (str,))
        self.database.commit()
        return

    def storeFont(self, str):
        sql = "INSERT INTO fonts(fontName) VALUES (%s)"
        self.database.cursor().execute(sql, (str,))
        self.database.commit()
        return

    def deleteWordByID(self, id):
        sql = "DELETE FROM words WHERE id = %s"
        self.database.cursor().execute(sql, (id,))
        self.database.commit()
        return
    
    def deleteAllWords(self):
        sql = "truncate table words"
        self.database.cursor().execute(sql)
        self.database.commit()
        return

    def deleteAllFonts(self):
        sql = "truncate table fonts"
        self.database.cursor().execute(sql)
        self.database.commit()
        return

    def dequeueNextWord(self):
        sql = "SELECT * FROM words"
        cursor = self.database.cursor(buffered=True)
        cursor.execute(sql)
        wordTuple = cursor.fetchone()
        if wordTuple is not None:
            self.deleteWordByID(wordTuple[0])
            return wordTuple[1]
        else:
            return None
    
    def getSelectedFont(self):
        sql = "SELECT * FROM fonts"
        cursor = self.database.cursor(buffered=True)
        cursor.execute(sql)
        wordTuple = cursor.fetchone()
        if wordTuple is not None:
            return wordTuple[1]
        else:
            return None
        
    def getAllWords(self):
        words = []
        sql = "SELECT * FROM words"
        cursor = self.database.cursor(buffered=True)
        cursor.execute(sql)
        for wordTuple in cursor.fetchall():
            words.append(wordTuple[1])
            
        return words