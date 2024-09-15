import json


class VerifyResult:
    def __init__(self, error_file=
    'C:\My Factory\Python\SimpleTrussGirderBridgesCaculator\core\model\specification_m\error_messages.json'):
        self.errors = []
        self.results = {}
        self.error_messages = self.load_error_messages(error_file)

    def load_error_messages(self, error_file):
        with open(error_file, 'r', encoding='utf-8') as file:
            return json.load(file)

    def add_error(self, error_type, error_code, result_key=None):
        description = self.error_messages.get(error_type, {}).get(error_code, "未知错误")
        error_entry = {"code": error_code, "description": description, "result_key": result_key}
        self.errors.append(error_entry)

    def add_result(self, key, value):
        self.results[key] = value

    def get_errors(self):
        return self.errors

    def get_results(self):
        return self.results

    def get_error_to_result_mapping(self):
        mapping = {}
        for error in self.errors:
            if error['result_key']:
                mapping[error['code']] = self.results.get(error['result_key'])
        return mapping

    def __str__(self):
        return f"VerifyResult( results: {self.results},errors: {self.errors})"
