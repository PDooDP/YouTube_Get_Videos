import pymysql

class dbConn():
    def __init__(self):
        pass

    def connStart(self):
        self.db = pymysql.connect(host="Your_IP", port=port, user="Your_UserName", passwd="Your_Password", database="Your_DataBase")
        self.c = self.db.cursor()

    def connEnd(self):
        return (self.c.close(), self.db.close())

    # 找出所有的資料
    def sql_selectFetchAll(self, sql):
        self.connStart()
        self.c.execute(sql)
        self.db.commit()
        data = self.c.fetchall()
        self.connEnd()
        return data

    # 取回來的資料是tuple串列型態，故需設定index位置 (pos)
    def sql_selectFetchOne(self, sql, pos=-1):
        self.connStart()
        self.c.execute(sql)
        self.db.commit()
        data = self.c.fetchone()[pos]
        self.connEnd()
        return data

    # update, insert, delete
    def sql_execute(self, sql):
        self.connStart()
        self.c.execute(sql)
        self.db.commit()
        self.connEnd()


    
