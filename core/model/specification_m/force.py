"""
这个类为力的计算
@param object_：力的作用对象
@param name：力的名字
@param magnitude：力的大小
@param direction：力的方向，传入单位向量如[0,0,1]
@param type：力的类型，如：dead_load（建规）,main_force（铁桥规）
@param applied：施加对象，whole、group、single
"""


class Force():
    _current_id = 1
    element_dict = {}

    def __init__(self, object_, name, magnitude, direction, type_=None, applied=None):

        self.id = self.__class__._current_id
        # 若该编号已经存在，重新获取编号
        if self.id in self.__class__.element_dict:
            self.id = self.__class__.__get_next_id()

        Force.element_dict[self.id] = self
        Force._current_id += 1
        self.name = name
        self.magnitude = magnitude
        self.direction = direction
        self.type_ = type_
        self.applied = applied
        self.Fx = direction[0] * magnitude
        self.Fy = direction[1] * magnitude
        self.Fz = direction[2] * magnitude

    def set_force(self, force):
        self.force = force

    @classmethod
    def __get_next_id(cls):
        """遍历获取下一个可用编号"""
        next_id = 1
        while True:
            if next_id not in cls.element_dict:
                cls._current_id = next_id
                return next_id
            next_id += 1

    @classmethod
    def reset_id(cls):
        """重置编号"""
        cls._current_id = 1
        cls.element_dict.clear()

    def delete(self):
        """删除节点"""
        if self.id in self.__class__.element_dict:
            del self.__class__.element_dict[self.id]
            self.__class__._current_id = 1
            self.id = 0  # 重置为0，表示已删除
            print("删除成功")

    def __del__(self):
        """当实例删除后，从字典中删除实例"""
        if self.id in self.__class__.element_dict:
            del self.__class__.element_dict[self.id]
            self.__class__._current_id = 1

    def __str__(self):
        return f"Force ID: {self.id}, Force Name: {self.name}, Fx: {self.Fx}, Fy: {self.Fy}, Fz: {self.Fx}, type: {self.type_}"
