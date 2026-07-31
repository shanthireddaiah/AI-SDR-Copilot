# Initialize PyMySQL driver to replace default MySQLdb driver for Django
import pymysql

pymysql.install_as_MySQLdb()
