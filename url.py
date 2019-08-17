
class Url:

    def __init__(self, string):
        self.string = string
        try:
            self.body = str(self.string).split("?")[0]
            self.keys = str(self.string).split("?")[1].split("&")
        except IndexError:
            self.body = string
            self.keys = list()
        self.params = dict()
        for key in self.keys:
            self.params[str(key).split("=")[0]] = str(key).split("=")[1]

    def add_key(self, name, value):
        if name not in self.params:
            self.params[name] = value
        else:
            print("Can't add. Key is in URL already.")

    def check_key(self, name):
        if name in self.params:
            return True
        else:
            return False

    def change_key(self, name, value):
        if name in self.params:
            self.params[name] = value
        else:
            print("Can't change. No such key in URL.")

    def get_url(self):
        param_string = ""
        if len(self.params):
            for value in self.params:
                param_string += f"{value}={self.params[value]}&"
            return f"{self.body}?{param_string[:-1]}"
        else:
            return self.body
