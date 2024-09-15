"""
这个类中定义了节点的各个参数
@param x, y, z 为坐标
@param id 为节点的编号，从1开始
"""


class Node:
    node_dict = {}  # 存储编号到实例的映射
    _current_id = 1  # 当前编号
    _coordinates = []

    def __new__(cls, x, y, z):
        coordinate = [x, y, z]
        # 如果坐标已经存在，则不创建
        if coordinate in cls._coordinates:
            print("重复坐标，创建失败")
            return None
        else:
            return super().__new__(cls)

    def __init__(self, x, y, z):

        self.id = self.__class__._current_id
        # 若该编号已经存在，重新获取编号
        if self.id in self.__class__.node_dict:
            self.id = self.__class__.__get_next_id()

        (self.x, self.y, self.z) = (x, y, z)
        self.coordinate = [x, y, z]

        Node.node_dict[self.id] = self
        Node._coordinates.append(self.coordinate)
        Node._current_id += 1
        self.name = None

    def get_coordinate(self):
        return [self.x, self.y, self.z]

    @classmethod
    def __get_all_coordinates(cls):
        """获取所有坐标"""
        for node in cls.node_dict.values():
            cls._coordinates.append(node.get_coordinate())

    @classmethod
    def __get_next_id(cls):
        """获取下一个可用编号"""
        next_id = 1
        while True:
            if next_id not in cls.node_dict:
                cls._current_id = next_id
                return next_id
            next_id += 1

    @classmethod
    def reset_id(cls):
        """重置编号"""
        cls._current_id = 1
        cls.node_dict.clear()
        cls._coordinates.clear()

    def delete(self):
        """删除节点"""
        if self.id in self.__class__.node_dict:
            del self.__class__.node_dict[self.id]
            self.__class__._current_id = 1
            self.__class__._coordinates.remove(self.get_coordinate())
            self.id = 0  # 重置为0，表示已删除
            print("删除成功")

    def __del__(self):
        """当实例删除后，从字典中删除实例"""
        if self.id in self.__class__.node_dict:
            del self.__class__.node_dict[self.id]
            self.__class__._current_id = 1
            self.__class__._coordinates.remove(self.get_coordinate())

    def __str__(self):
        return f"Node ID: {self.id}, Coordinate: {self.x}, {self.y}, {self.z}"
