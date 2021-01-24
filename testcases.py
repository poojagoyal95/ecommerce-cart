import unittest
import os
from dotenv import load_dotenv
load_dotenv()
import mysql.connector

class Orders(unittest.TestCase):

    def test_dbconnection(self):
        mydb = mysql.connector.connect(
            host = os.getenv("HOST"),
            user = os.getenv("DB_USERNAME"),
            password =os.getenv("DB_PASSWORD"),
            database = os.getenv("DB_DATABASE")
        )
        assert mydb is not None

    

unittest.main()
