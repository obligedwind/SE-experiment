# 项目目标

 开发一个B/S网站，支持学术师承树的构建、查询、维护；
  
 用户可以在网站上建立个人的师承关系树：向上是导师、导师的导师、导师的师兄弟、…；向下是学生、学生的学生、…；

 用户也可以在其他人的师承关系树上进行补充（增加某些人）或修正（对错误的关系进行修改删除）；

 根据师生关系，可将多棵树连接在一起；

 树中唯一的关系类型是“师生关系”，该关系有时间属性（意即在哪个时间段内两人产生师生关系）。

 一个人可以有多个导师（多重继承）。

 用户输入某个人，查询他的师承关系、学生、师兄弟等等；

 当用户点击某个节点时，可连接到LinkedIn或Google Scholar查看该节点人员的职业和publication等信息。

# 项目部署
Python版本 python    3.10

psycopg2             2.99

django

psql                 15.5

# 后端部署
**使用psql进行数据的持久化**
关系表:
u{user id}_view:(保存用户自己视图内的各种信息)
```CREATE TABLE u{phone}_view (id VARCHAR(20) PRIMARY KEY, name VARCHAR(100), page VARCHAR(100), phone INT);```

u{user id}_relation:(保存用户自己视图内的关系)
```CREATE TABLE u{phone}_relation (id_t VARCHAR(20) , id_s VARCHAR(20) , time VARCHAR(20), PRIMARY KEY (id_t, id_s),FOREIGN KEY (id_t) REFERENCES u{phone}_view(id), FOREIGN KEY (id_s) REFERENCES u{phone}_view(id));```

u{user id}_to_merge:(保存他人修改后未经用户确认修改的信息)
```CREATE TABLE u{phone}_to_merge (id SERIAL PRIMARY KEY , oprand VARCHAR (6), val_1 VARCHAR (20), val_2 VARCHAR (100));```

global_view:(所有经过本人确认的所有信息的最后版本，用于在查询师承关系时的展示)
```create table global_view (id VARCHAR(20) PRIMARY KEY, name VARCHAR(100), page VARCHAR(100), phone INT);```

global_relation:(所有经过本人确认的师生关系的最后版本，用于查询师承关系)
```global_relation (id_t VARCHAR(20) , id_s VARCHAR(20) , time VARCHAR(20), PRIMARY KEY (id_t, id_s),FOREIGN KEY (id_t) REFERENCES global_view(id), FOREIGN KEY (id_s) REFERENCES global_view(id));```

global_merge:(所有未确认的，并且由于对方不存在而无法加入对方的u{user id}_to_merge表中。当对方注册时，用于将这类被修改信息提供给对方)
```create table global_merge (id VARCHAR(20), i int, oprand VARCHAR(6), val_1 VARCHAR(20), val_2 VARCHAR(100));```

可以通过执行项目中提供的reset.sql进行对数据库的重置与设置

# 服务器端
迭代2时搬上云

# 前端部署
使用django

# TODO
1. 将服务应用于云服务器中
2. 优化前端中使用的输入，使用户体验提高




