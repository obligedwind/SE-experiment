
# TODO:需要设计哈希函数，让重名的人也能够加入其中，现在只支持不重名的情况
# TODO:个人师承关系树，维护自己写入的部分，只可见自己保存的记录
class selfTree:
    def __init__(self, name: str):
        Node = node(name)
        self.id = Node.id
        self.name = name
        # cursor指向自己的结点，该结点应当与name有相同的名字
        self.cursor = Node


# 结点共用与个人树与服务器维护的树。或者说服务器只考虑个人树中的自己的结点，不存储树状结构，采用哈希表（字典）进行存储
class node:
    def __init__(self, name: str):
        self.name = name
        self.id = hash(name)
        self.teacher = []
        self.student = []
        # learnPeriod 按照顺序对应self.teacher
        self.learnPeriod = []
        # teachPeriod 按照顺序对应self.student
        self.teachPeriod = []
        # to merge字段用于记录与自己相关的关系被修改部分，通过特定标识与规则确定被修改的操作，用于实现这些操作与提示被修改者
        self.toMerge = []

