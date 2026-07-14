import jaydebeapi

def get_connection():

    connectServer = "P"
    if connectServer == "P":
        conn = jaydebeapi.connect(
            "com.ibm.as400.access.AS400JDBCDriver",
            "jdbc:as400://185.113.5.134;libraries=ADITHYA1",
            ["adithya", "adithya123"],
            r"C:\Users\user\Downloads\jt400.jar",
        )
    elif connectServer == "T":    
        conn = jaydebeapi.connect(
            "com.ibm.as400.access.AS400JDBCDriver",
            "jdbc:as400://192.168.90.205;libraries=TYKSFLIB",
            ["QSECOFR","QSECOFR"],

	r"C:\Users\is_144\Desktop\project\ScmHandy\backend\jar\jt400.jar"
    )

    return conn



       