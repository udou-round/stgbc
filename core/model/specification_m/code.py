

class Code():
    def __init__(self):
        self.name = None
        self.number = None
        self.date = None

    def __str__(self):
        return (f"规范名称为{self.name}，编号为{self.number}，发布日期为{self.date}")