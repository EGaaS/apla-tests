import unittest

from libs import actions
from libs import tools


class TestMultiApi(unittest.TestCase):

    @classmethod
    def setup_class(self):
        global url, token, prKey, pause
        self.config = tools.read_config("nodes")
        url = self.config["2"]["url"]
        pause = tools.read_config("test")["wait_tx_status"]
        prKey = self.config["1"]['private_key']
        self.data = actions.login(url, prKey, 0)
        token = self.data["jwtToken"]

    def assert_multi_tx_in_block(self, result, jwtToken):
        self.assertIn("hashes", result)
        hashes = result['hashes']
        result = actions.tx_status_multi(url, pause, hashes, jwtToken)
        for status in result.values():
            self.assertNotIn('errmsg', status)
            self.assertGreater(int(status["blockid"]), 0, "BlockID not generated")

    def call_multi(self, name, data):
        resp = actions.call_multi_contract(url, prKey, name, data, token)
        resp = self.assert_multi_tx_in_block(resp, token)
        return resp


    def test_new_interface_block(self):
        contractName = "NewBlock"
        block = "Block_" + tools.generate_random_name()
        data = [{"contract": contractName,
                 "params":{"Name": block, "Value": "Hello page!", "ApplicationId": "1",
                "Conditions": "true"}}]
        res = self.call_multi(contractName, data)

    def test_new_interface_block_multi(self):
        contractName = "NewBlock"
        data = [{"contract": contractName,
                 "params": {"Name": "Block_" + tools.generate_random_name(), "Value": "Hello page!",
                            "ApplicationId": "1",
                            "Conditions": "true"}} for _ in range(2)]
        res = self.call_multi(contractName, data)
     
    def test_new_lang(self):
        contractName = "NewLang"
        nameLang = "Lang_" + tools.generate_random_name()
        data = [{"contract": contractName,
                 "params": {"ApplicationId": "1", "Name": nameLang,
                "Trans": "{\"en\": \"World_en\", \"ru\" : \"Мир_ru\"," +\
                "\"fr-FR\": \"Monde_fr-FR\", \"de\": \"Welt_de\"}"}}]
        res = self.call_multi(contractName, data)

    def test_new_page(self):
        contractName = "NewPage"
        name = "Page_" + tools.generate_random_name()
        data = [{"contract": contractName,
                 "params":{"Name":name, "Value":"SetVar(a,\"Hello\") \n Div(Body: #a#)", "Conditions":"true", "Menu":"default_menu", "ApplicationId": "1"}}]
        res = self.call_multi(contractName, data)