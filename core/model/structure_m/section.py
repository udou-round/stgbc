class Section:
    all_sections = []

    def __init__(self, height, width):
        Section.all_sections.append(self)

        self.height = height
        self.width = width

    @classmethod
    def create_section(cls):
        pass

    def calculate_Ix(self):
        pass

    def calculate_A(self):
        pass

    def calculate_Iy(self):
        pass


