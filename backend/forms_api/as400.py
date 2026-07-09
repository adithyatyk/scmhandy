import jaydebeapi

def get_connection():

    conn = jaydebeapi.connect(
     "com.ibm.as400.access.AS400JDBCDriver",
     "jdbc:as400://192.168.90.205;libraries=TYKSFLIB",
      ["QSECOFR","QSECOFR"],

	r"C:\Users\is_144\Desktop\project\ScmHandy\backend\jar\jt400.jar"
    )

    return conn