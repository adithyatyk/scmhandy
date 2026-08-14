import jaydebeapi

def get_connection():

    conn = jaydebeapi.connect(
     "com.ibm.as400.access.AS400JDBCDriver",
     "jdbc:as400://192.168.90.205;libraries=TYKSFLIB",
      ["QSECOFR","QSECOFR"],

	r".\jar\jt400.jar"
    )

    return conn
