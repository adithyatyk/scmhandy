import jaydebeapi

def get_connection():

    conn = jaydebeapi.connect(
     "com.ibm.as400.access.AS400JDBCDriver",
     "jdbc:as400://185.113.5.134;libraries=ADITHYA1",
    ["adithya", "adithya123"],

	r"C:\Users\user\Desktop\Scmhandy\scmhandy\backend\jar\jt400.jar"
    )

    return conn