import os
import json

from libs.actions import Actions


class Tools(object):


    def readExample(self):
        path = os.path.join(os.getcwd(), "fixtures", "example.json")
        with open(path, 'r', encoding='UTF-8') as f:
            data = f.read()
        return json.loads(data)
    
    def jsonToList(self, js):
        fullList = []
        list = []
        tup = ()
        for i in js:
            for element in i:
                list.append(i[element])
            tup = tuple(list)
            fullList.append(tup)
        return fullList
    
    def generate_random_name(self):
        name = []
        for _ in range(1, 30):
            sym = random.choice(string.ascii_lowercase)
            name.append(sym)
        return "".join(name)

    def generate_name_and_code(self, sourceCode):
        name = "Cont_" + self.generate_random_name()
        code = self.generate_code(sourceCode)
        return code, name

    def generate_code(self, contractName, sourceCode):
        if sourceCode == "":
            sCode = """{data { }    conditions {    }    action {    }    }"""
        else:
            sCode = sourceCode
        code = "contract " + contractName + sCode
        return code
    
    def readConfig(type):
        if type is "main":
            path = os.path.join(os.getcwd(), "config.json")
        if type is "nodes":
            path = os.path.join(os.getcwd(), "nodesConfig.json")
        if type is "test":
            path = os.path.join(os.getcwd(), "testConfig.json")
        with open(path, 'r') as f:
            data = f.read()
        return json.loads(data)

    def readFixtures(type):
        path = ""
        if type == "contracts":
            path = os.path.join(os.getcwd(), "fixtures", "contracts.json")
        if type == "pages":
            path = os.path.join(os.getcwd(), "fixtures", "pages.json")
        if type == "api":
            path = os.path.join(os.getcwd(), "fixtures", "api.json")
        if type == "keys":
            path = os.path.join(os.getcwd(), "fixtures", "prKeys.json")
        if type == "simvolio":
            path = os.path.join(os.getcwd(), "fixtures", "simvolio.json")
        with open(path, 'r', encoding='UTF-8') as f:
            data = f.read()
        return json.loads(data)

