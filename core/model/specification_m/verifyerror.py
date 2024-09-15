import json

"""
原用作生成错误信息，已被VerifyResult替代功能，已作废
"""

class VerifyError:
    def __init__(self, error_type, code, config_file='C:\My Factory\Python\SimpleTrussGirderBridgesCaculator\core\model\specification_m\error_messages.json'):
        self.error_type = error_type
        self.code = code
        self.message = self.load_error_messages(config_file).get(error_type, {}).get(code, "未知错误")

    def load_error_messages(self, config_file):
        with open(config_file, 'r', encoding='utf-8') as file:
            return json.load(file)

    def __str__(self):
        return f"{self.error_type}: {self.message} (错误代码: {self.code})"