import psycopg2
import re
db = psycopg2.connect(host='localhost',
                      port='5432',
                      user='postgres',
                      dbname='software',
                      password='123')

cursor = db.cursor()

# 使用psql进行数据持久化，用户可见自己的表，点击commit后才让root将信息进行同步，否则将一直存储于用户自己的视图中
# TODO:需要设计哈希函数，让重名的人也能够加入其中，现在只支持不重名的情况,可以加入电话号码来辅助生成hash值
# 已解决，使用电话号码作为哈希值，sprint1假设人不换电话号码，将更换电话号码的情况放在sprint2中处理

def user_exist(phone: int):
    sql = f"select * from pg_catalog.pg_tables where schemaname = 'public' and tableowner = 'u{phone}';"
    cursor.execute(sql)
    return cursor.fetchone() is not None
# TODO:需要设计哈希函数，让重名的人也能够加入其中，现在只支持不重名的情况
# TODO:个人师承关系树，维护自己写入的部分，只可见自己保存的记录



# 结点共用与个人树与服务器维护的树。或者说服务器只考虑个人树中的自己的结点，不存储树状结构，采用哈希表（字典）进行存储
class node:
    def __init__(self, name: str, phone: int, nc, ne, page: str = None):
        self.name = name
        self.page = page
        self.phone = phone
        self.id = str(phone)
        self.teacher = []
        self.student = []
        # learnPeriod使用字典，键值为self.teacher
        self.learnPeriod = {}
        # teachPeriod使用字典，键值为self.student
        self.teachPeriod = {}
        # to merge字段用于记录与自己相关的关系被修改部分，通过特定标识与规则确定被修改的操作，用于实现这些操作与提示被修改者
        self.toMerge = []
        # page用于存储个人主页的url
        self.nc = nc
        self.ne = ne

    # 不适用于树的初始化，仅供对于某一结点的前驱或者后继的加入
    # TODO:可以在增加结点的时候查询服务器中的hash值，并且给出提示，填写对应的结点
    def append(self, name: str, phone: int, t: bool, page: str = None, time: str = None):
        Node = node(name, phone, self.nc, page)
        if (page != None):
            sql = f"INSERT INTO u{self.phone}_view (id, name, phone, page) values ({phone}, '{name}', '{phone}', '{page}')"
        else:
            sql = f"INSERT INTO u{self.phone}_view (id, name, phone) values ({phone}, '{name}', '{phone}')"
        try:
            self.nc.execute(sql)
            self.ne.commit()
        except:
            self.ne.rollback()
            return
        if (t):
            self.teacher.append(str(phone))
            sql = f"INSERT INTO u{self.phone}_relation (id_t, id_s) values({phone}, {self.phone});"
            if (time != None):
                self.learnPeriod[str(phone)] = time
                sql = f"INSERT INTO u{self.phone}_relation (id_t, id_s, time) values({phone}, {self.phone}, '{time}');"
            self.nc.execute(sql)
            sql = f"select * from pg_catalog.pg_tables where schemaname = 'public' and tableowner = 'u{phone}';"
            self.nc.execute(sql)
            sql = f"INSERT INTO global_merge (id, oprand, val_1, val_2) values ({phone}, 'teastu', '{time}', '{phone}_{self.phone}');"
            if (self.nc.fetchone() != None):
                sql = f"INSERT INTO u{phone}_to_merge (oprand, val_1, val_2) values ('teastu', '{time}', '{phone}_{self.phone}');"
            self.nc.execute(sql)
            self.ne.commit()
        else:
            self.student.append(str(phone))
            sql = f"INSERT INTO u{self.phone}_relation (id_t, id_s) values({self.phone}, {phone});"
            if (time != None):
                self.teachPeriod[str(phone)] = time
                sql = f"INSERT INTO u{self.phone}_relation (id_t, id_s, time) values({self.phone}, {phone}, '{time}');"
            self.nc.execute(sql)
            sql = f"select * from pg_catalog.pg_tables where schemaname = 'public' and tableowner = 'u{phone}';"
            self.nc.execute(sql)
            sql = f"INSERT INTO global_merge (id, oprand, val_1, val_2) values ({phone}, 'teastu', '{time}', '{self.phone}_{phone}');"
            if (self.nc.fetchone() != None):
                sql = f"INSERT INTO u{phone}_to_merge (oprand, val_1, val_2) values ('teastu', '{time}', '{self.phone}_{phone}');"
            self.nc.execute(sql)
            self.ne.commit()

    def merge_mani(self, i: int):
        sql = f"SELECT * FROM u{self.phone}_to_merge WHERE id = {i};"
        self.nc.execute(sql)
        res = self.nc.fetchone()
        # 对应append
        if res[1] == "teastu":
            num = res[3].split("_")
            ph_t, ph_s = num[0], num[1]
            time = res[2]
            oth = ph_t
            if str(self.phone) == ph_t:
                oth = ph_s
            sql = f"SELECT * FROM global_view WHERE id = '{oth}';"
            self.nc.execute(sql)
            record = self.nc.fetchone()
            # 先要同步view记录
            sql = f"INSERT INTO u{self.phone}_view (id, name, page, phone) VALUES ({record[0]}, '{record[1]}', '{record[2]}', '{record[3]}');"
            self.nc.execute(sql)
            self.ne.commit()
            # 然后增加relation记录
            sql = f"INSERT INTO u{self.phone}_relation (id_t, id_s, time) VALUES ({ph_t}, {ph_s}, '{time}');"
            self.nc.execute(sql)
            self.ne.commit()
            sql = f"INSERT INTO global_relation (id_t, id_s, time) VALUES ({ph_t}, {ph_s}, '{time}');"
            self.nc.execute(sql)
            self.ne.commit()
        # 对于modify的情况，应该按照table.txt的形式
        elif res[1] == "modify":
            # 可供修改的属性只有：名字，网址，以及师生关系中的时间。对于电话的更换，需要本人自己操作，换号，因为电话号码是主键的一环
            if res[2] == "name":
                lines = res[3].split("_")
                # 在调用这些之前都需要在输入的平台内有逻辑对其进行判断
                sql = f"UPDATE u{self.phone}_view SET name = '{lines[1]}' WHERE id = '{lines[0]}'"
                sql1 = f"UPDATE global_view SET name = '{lines[1]}' WHERE id = '{lines[0]}'"
            elif res[2] == "page":
                lines = res[3].split("_")
                sql = f"UPDATE u{self.phone}_view SET page = '{lines[1]}' WHERE id = '{lines[0]}'"
                sql1 = f"UPDATE global_view SET page = '{lines[1]}' WHERE id = '{lines[0]}'"
            elif res[2] == "time":
                lines = res[3].split("_")
                sql = f"UPDATE u{self.phone}_relation SET time = '{lines[2]}' WHERE id_t = '{lines[0]}' AND id_s = '{lines[1]}';"
                sql1 = f"UPDATE global_relation SET time = '{lines[2]}' WHERE id_t = '{lines[0]}' AND id_s = '{lines[1]}';"
            self.nc.execute(sql)
            self.nc.execute(sql1)
            self.ne.commit()
        # 对应drop函数，这里也搞得复杂一点，需要两边确认，先检查一遍global_merge中有无相关确认，
        # 如果有，则删除global_merge与global_relation中的相关记录。
        # 如果没有，则添加val_1: id_t, val_2: id_s， oprand: drop
        # 这里解释一下，当且仅当两边都有账号且之前已经相互确认师徒关系才会将drop推送出来，所以不会有同名记录存在公共表中
        elif res[1] == "drop":
            sql = f"SELECT * FROM global_merge WHERE oprand = 'drop' AND val_1 = '{res[2]}' AND val_2 = '{res[3]}';"
            self.nc.execute(sql)
            if self.nc.fetchone is not None:
                sql = f"DELETE FROM global_merge WHERE oprand = 'drop' AND val_1 = '{res[2]}' AND val_2 = '{res[3]}';"
                sql1 = f"DELETE FROM global_relation WHERE id_t = '{res[2]}' AND id_s = '{res[3]}';"
                self.nc.execute(sql)
                self.nc.execute(sql1)
                self.ne.commit()
            else:
                sql = f"INSERT INTO global_merge (oprand, val_1, val_2) VALUES ('drop', '{res[2]}', '{res[3]}');"
                self.nc.execute(sql)
                self.ne.commit()

        # 最后将对应的to merge项删除
        sql = f"DELETE FROM u{self.phone}_to_merge WHERE id = {i};"
        self.nc.execute(sql)
        self.ne.commit()

    # TODO:做一个对自己进行修改时，不需要确认，直接可以同步到
    # 要做的不多，类似于append，中间的过程可以copy一下，要有个判断是否是已有用户，然后后面的部分就是按照table中的规划对格式进行要求就行
    def modify(self, item: str, value, id_t: str = None, id_s: str = None):
        try:
            b = user_exist(self.phone)
            if item == "name":
                if b:
                    table_name = 'u' + str(self.phone) + "_to_merge"
                    sql = f"INSERT INTO {table_name} (oprand, val_1, val_2) values ('modify', 'name', '{self.phone}_{value}');"
                else:
                    table_name = "global_merge"
                    sql = f"INSERT INTO {table_name} (id, oprand, val_1, val_2) values ('{self.phone}', 'modify', 'name', '{self.phone}_{value}');"
            elif item == "page":
                if b:
                    table_name = 'u' + str(self.phone) + "_to_merge"
                    sql = f"INSERT INTO {table_name} (oprand, val_1, val_2) values ('modify', 'page', '{self.phone}_{value}');"
                else:
                    table_name = "global_merge"
                    sql = f"INSERT INTO {table_name} (id, oprand, val_1, val_2) values ('{self.phone}', 'modify', 'page', '{self.phone}_{value}');"
            elif item == "time":
                if b:
                    table_name = 'u' + str(self.phone) + "_to_merge"
                    sql = f"INSERT INTO {table_name} (oprand, val_1, val_2) values ('modify', 'time', '{id_t}_{id_s}_{value}');"
                else:
                    table_name = "global_merge"
                    sql = f"INSERT INTO {table_name} (id, oprand, val_1, val_2) values ('{self.phone}', 'modify', 'time', '{id_t}_{id_s}_{value}');"
            cursor.execute(sql)
            db.commit()
        except:
            db.rollback()

    # 删除操作只能针对关系进行，对于个人纪录，有电话的保证肯定确有其人，只是信息需要修改，只有关系可能会被误操作
    # 先对总表进行查询，如果其中不含该记录，则这条记录属于单人误操作的，可以将其删除，如果总表包含该记录，则
    def drop(self, id_t: str, id_s: str, id_u: str):
        sql = f"SELECT * FROM global_relation WHERE id_t = '{id_t}' AND id_s = '{id_s}';"
        cursor.execute(sql)
        # 如果从全局关系表中没有相关记录，推测是个人的意淫，可以直接删除
        if cursor.fetchone() is None:
            sql = f"DELETE FROM u{id_u}_relation WHERE id_t = '{id_t}' AND id_s = '{id_s}';"
            cursor.execute(sql)
            db.commit()
            sql = f"SELECT * FROM u{id_u}_relation WHERE id_t = '{id_t}' OR id_s = '{id_t}';"
            cursor.execute(sql)
            if cursor.fetchone() is None and id_t != id_u:
                self.drop_user(id_t, id_u)
            sql = f"SELECT * FROM u{id_u}_relation WHERE id_t = '{id_s}' OR id_s = '{id_s}';"
            cursor.execute(sql)
            if cursor.fetchone() is None and id_s != id_u:
                self.drop_user(id_s, id_u)
            return
        # 对于一般情况，双方都有记录的情况，一方面为了简化（可以让从查询中删除与从个人树中删除合并），另一方面可以说是希望再次确认，所以就算是删除的发起者，
        # 也将会被对方调用该函数时接收到相关的to merge信息，需要再次确认
        table_name = 'u' + str(self.phone) + "_to_merge"
        sql = f"INSERT INTO {table_name} (oprand, val_1, val_2) values ('drop', '{id_t}', '{id_s}');"
        cursor.execute(sql)
        db.commit()

    #   只用于删除个人的表中的某个人，直接将其信息删除不需同步，不进入merge
    def drop_user(self, id: str, id_u: str):
        sql = f"DELETE FROM u{id_u}_view WHERE id = '{id}';"
        cursor.execute(sql)
        db.commit()

class selfTree:
    def __init__(self, no: node, nc, ne, nodes: dict):
        self.id = no.id
        self.name = no.name
        # cursor指向自己的结点，该结点应当与name有相同的名字
        self.cursor = no
        self.nc = nc
        self.ne = ne
        self.nodes = nodes


# TODO：注册，新用户注册，输入手机号与账号密码即可注册。注册时需要新建一个角色在psql中并且建立相关的表
def register(phone: int, psw: str, name: str):
    sql = f"SELECT usename FROM pg_catalog.pg_user WHERE usename=\'u{phone}\'"
    cursor.execute(sql)
    if (cursor.fetchone() != None):
        print("该手机号已注册账号")
        return
    sql = f"CREATE USER u{phone} WITH PASSWORD '{psw}';"
    cursor.execute(sql)
    db.commit()
    sql = f"grant all privileges on database software to u{phone};"
    cursor.execute(sql)
    sql = f"grant all privileges on schema public to u{phone};"
    cursor.execute(sql)
    db.commit()
    ne = psycopg2.connect(host='localhost',
                          port='5432',
                          user='u' + str(phone),
                          dbname='software',
                          password=str(psw))
    rc = ne.cursor()
    sql = f"CREATE TABLE u{phone}_view (id VARCHAR(20) PRIMARY KEY, name VARCHAR(100), page VARCHAR(100), phone VARCHAR(20));"
    rc.execute(sql)
    ne.commit()
    sql = f"CREATE TABLE u{phone}_relation (id_t VARCHAR(20) , id_s VARCHAR(20) , time VARCHAR(20), PRIMARY KEY (id_t, id_s)" \
          f",FOREIGN KEY (id_t) REFERENCES u{phone}_view(id), FOREIGN KEY (id_s) REFERENCES u{phone}_view(id));"
    rc.execute(sql)
    ne.commit()
    idt = str(phone)
    sql = f"INSERT INTO u{phone}_view (id, phone, name) VALUES ({idt}, '{phone}', '{name}');"
    rc.execute(sql)
    sql = f"INSERT INTO global_view (id, phone, name) VALUES ({idt}, '{phone}', '{name}');"
    rc.execute(sql)
    ne.commit()
    sql = f"CREATE TABLE u{phone}_to_merge (id SERIAL PRIMARY KEY , oprand VARCHAR (6), val_1 VARCHAR (20), val_2 VARCHAR (100));"
    rc.execute(sql)
    ne.commit()
    # TODO：查询一下global_merge表中有没有需要加入的操作
    sql = f"SELECT * FROM global_merge WHERE id = '{phone}';"
    rc.execute(sql)
    lis = rc.fetchall()
    for li in lis:
        sql = f"INSERT INTO u{phone}_to_merge (oprand, val_1, val_2) values ('{li[2]}', '{li[3]}', '{li[4]}');"
        rc.execute(sql)
    sql = f"DELETE FROM global_merge WHERE id = '{phone}';"
    rc.execute(sql)
    ne.commit()
    return


# TODO：登录，输入手机号码与密码登录账号，登录后需要初始化selfTree以及构造相关结点,返回一个selfTree，使用其中结点可视化，以及其中保存的cursor进行操作
def login(phone: int, psw: str):
    try:
        ne = psycopg2.connect(host='localhost',
                              port='5432',
                              user='u' + str(phone),
                              dbname='software',
                              password=str(psw))
        nc = ne.cursor()
    except:
        print("密码错误或未注册")
        return
    sql = f"SELECT * FROM u{phone}_view;"
    nc.execute(sql)
    blocks = nc.fetchall()
    sql = f"SELECT * FROM u{phone}_relation;"
    nc.execute(sql)
    relation = nc.fetchall()
    sql = f"SELECT * FROM u{phone}_to_merge;"
    nc.execute(sql)
    to_merge = nc.fetchall()
    nodes = {}
    for block in blocks:
        nodes[block[0]] = node(block[1], block[3], cursor, db, block[2])
    for rel in relation:
        nodes[rel[0]].student.append(rel[1])
        nodes[rel[0]].teachPeriod[rel[1]] = rel[2]
        nodes[rel[1]].teacher.append(rel[0])
        nodes[rel[1]].teachPeriod[rel[0]] = rel[2]
    nodes[str(phone)].toMerge = to_merge
    # print(nodes[str(phone)].toMerge)
    # 这个地方好像又说不能更换用户，再看看
    st = selfTree(nodes[str(phone)], cursor, db, nodes)
    return st


def ret_list(string: str):
    # 提取数字的正则表达式模式
    pattern = re.compile(r'\d+')

    # 存储匹配结果的列表
    matches = []
    # 遍历数据并匹配数字
    for item in string:
        for element in item:
            match = pattern.search(element)
            if match:
                matches.append(match.group())
    return matches


def getNode(i: str):
    sql = f"SELECT * FROM global_view WHERE id = '{i}';"
    cursor.execute(sql)
    res = cursor.fetchone()
    if res is None:
        # 处理 res 是 None 的情况
        print("查询结果为空")
        return None
    else:
        # res 不是 None，继续执行
        n = node(res[1], res[3], cursor, db, res[2])
        return n


# 此处的i表示需要查询的结点
def lookup(i: str):
    sql_stu = f"SELECT id_s FROM global_relation WHERE id_t = '{i}';"
    sql_tea = f"SELECT id_t FROM global_relation WHERE id_s = '{i}';"
    sql_merge = f"SELECT * FROM u{i}_to_merge;"
    cursor.execute(sql_stu)
    stu = ret_list(cursor.fetchall())
    cursor.execute(sql_tea)
    tea = ret_list(cursor.fetchall())
    i_node = getNode(i)
    i_node.teacher = tea
    i_node.student = stu
    cursor.execute(sql_merge)
    i_node.toMerge = cursor.fetchall()
    nodes = {i: i_node}
    for no in stu:
        nodes[no] = getNode(no)
        nodes[no].teacher.append(i)
    for no in tea:
        nodes[no] = getNode(no)
        nodes[no].student.append(i)
        sql_bro = f"SELECT id_s FROM global_relation WHERE id_t = '{no}';"
        cursor.execute(sql_bro)
        bro = ret_list(cursor.fetchall())
        for br in bro:
            nodes[br] = getNode(br)
            nodes[br].teacher.append(no)
            nodes[no].student.append(br)
    st = selfTree(i_node, cursor, db, nodes)
    return st


# phone = 123
# idt = str(phone)
# name = 'y'
# page = None
# phone_2 = 322
# sql = f"INSERT INTO global_merge (id, oprand, val_1, val_2) values ({phone}, 'teastu', '{page}', '{phone_2}_{phone}')"
# cursor.execute(sql)
# db.commit()
# lis = cursor.fetchall()
# for l in lis:
#     print(l)
# db.commit()
# print(cursor.fetchall())

# register(123, 123, 'l')
# st = login(123, 123)
# st.cursor.append('abc', 345, True, time='2022.1.1-2023.1.1')
# st.cursor.append('xyz', 456, True, time='2022.1.1-2023.1.1')
#
# register(345, 345, 'l')
# st = login(345, 345)
# print(st.cursor.toMerge[0])
# st.cursor.merge_mani(1)
# st.cursor.modify('name', 'xl')
# st.nodes['123'].modify('name', 'xl')
# register(456, 456, 'xyz')
# st = login(456, 456)
# st.cursor.merge_mani(1)
#
# i = 123
# sql_stu = f"SELECT id_t FROM global_relation WHERE id_s = '{i}';"
# cursor.execute(sql_stu)
# stu = cursor.fetchall()
#
# print(stu)
# matches = ret_list(stu)
# # 打印匹配结果
# print(matches)

# st = lookup('123')
# print(st)