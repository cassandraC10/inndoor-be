import pymysql

# Use PyMySQL as MySQLdb replacement for Django on environments where
# the native mysqlclient is not available/compilable.
pymysql.install_as_MySQLdb()
