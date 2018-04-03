import unittest
import utils
import config
import requests
import json
import time


class ContractFunctionsTestCase(unittest.TestCase):
    def setUp(self):
        self.config = config.readMainConfig()
        global url, prKey,token
        self.contracts = config.readFixtures("contracts")
        url = self.config["url"]
        prKey = self.config['private_key']
        self.data = utils.login(url,prKey)
        token = self.data["jwtToken"]

    def assertTxInBlock(self, result, jwtToken):
        self.assertIn("hash",  result)
        status = utils.txstatus(url,
                                self.config["time_wait_tx_in_block"],
                                result['hash'], jwtToken)
        self.assertNotIn(json.dumps(status), 'errmsg')
        self.assertGreater(len(status['blockid']), 0)

    def generate_name_and_code(self, sourseCode):
        name = utils.generate_random_name()
        code = "contract " + name + sourseCode
        return code, name

    def create_contract(self, code):
        data = {"Wallet": "",
                "Value": code,
                "Conditions": "ContractConditions(`MainCondition`)"}
        result = utils.call_contract(url, prKey, "NewContract",
                                     data, token)
        self.assertTxInBlock(result, token)

    def check_contract(self, sourse, checkPoint):
        code, name = self.generate_name_and_code(sourse)
        self.create_contract(code)
        url = self.config["url"]
        prKey = self.config['private_key']
        token = self.data["jwtToken"]
        sleep = self.config["time_wait_tx_in_block"]
        res = utils.call_contract(url, prKey, name, {}, token)
        hash = res["hash"]
        result = utils.txstatus(url, sleep, hash, token)
        self.assertIn(checkPoint, result["result"], "error")

    def test_contract_dbfind(self):
        contract = self.contracts["dbFind"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_ecosysParam(self):
        contract = self.contracts["ecosysParam"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_dbRow(self):
        contract = self.contracts["dbRow"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_ifMap(self):
        contract = self.contracts["ifMap"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_evalCondition(self):
        contract = self.contracts["evalCondition"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_validateCondition(self):
        contract = self.contracts["validateCondition"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_addressToId(self):
        contract = self.contracts["addressToId"]
        self.check_contract(contract["code"], contract["asert"])
        
    def test_contract_one(self):
        contract = self.contracts["one"]
        self.check_contract(contract["code"], contract["asert"])
    
    def test_contract_row(self):
        contract = self.contracts["row"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_contains(self):
        contract = self.contracts["contains"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_float(self):
        contract = self.contracts["float"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_hasPrefix(self):
        contract = self.contracts["hasPrefix"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_hexToBytes(self):
        contract = self.contracts["hexToBytes"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_Int(self):
        contract = self.contracts["int"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_len(self):
        contract = self.contracts["len"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_pubToID(self):
        contract = self.contracts["pubToID"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_replace(self):
        contract = self.contracts["replace"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_size(self):
        contract = self.contracts["size"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_sha256(self):
        contract = self.contracts["sha256"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_Sprintf(self):
        contract = self.contracts["sprintf"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_str(self):
        contract = self.contracts["str"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_substr(self):
        contract = self.contracts["substr"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_updateLang(self):
        contract = self.contracts["updateLang"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_sysParamString(self):
        contract = self.contracts["sysParamString"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_sysParamInt(self):
        contract = self.contracts["updSysParam"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_updSysParam(self):
        contract = self.contracts["updSysParam"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_getContractById(self):
        contract = self.contracts["getContractById"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_getContractByName(self):
        contract = self.contracts["getContractByName"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_random(self):
        contract = self.contracts["random"]
        self.check_contract(contract["code"], contract["asert"])
        
    def test_contract_langRes(self):
        data = {"Name": "test",
                "Trans": "{\"en\": \"test_en\", \"de\" : \"test_de\"}"}
        utils.call_contract(url, prKey, "NewLang", data, token)
        time.sleep(8)
        contract = self.contracts["langRes"]
        self.check_contract(contract["code"], contract["asert"])
        
    def test_contract_dbInsert(self):
        columns = """[{"name":"name","type":"varchar",
        "index": "1",  "conditions":"true"},
        {"name":"test","type":"varchar",
        "index": "0",  "conditions":"true"}]"""
        permission = """{"insert": "true",
        "update" : "true","new_column": "true"}"""
        data = {"Name": "test",
                "Columns": columns,
                "Permissions": permission}
        result = utils.call_contract(url, prKey, "NewTable", data, token)
        tx = utils.txstatus(url,
                                self.config["time_wait_tx_in_block"],
                                result['hash'], token)
        contract = self.contracts["dbInsert"]
        self.check_contract(contract["code"], contract["asert"])
        
    def test_contract_dbUpdate(self):        
        columns = """[{"name":"name","type":"varchar",
        "index": "1",  "conditions":"true"},
        {"name":"test","type":"varchar",
        "index": "0",  "conditions":"true"}]"""
        permission = """{"insert": "true",
        "update" : "true","new_column": "true"}"""
        data = {"Name": "test",
                "Columns": columns,
                "Permissions": permission}
        result = utils.call_contract(url, prKey, "NewTable", data, token)
        tx = utils.txstatus(url,
                                self.config["time_wait_tx_in_block"],
                                result['hash'], token)
        contract = self.contracts["dbInsert"]
        self.check_contract(contract["code"], contract["asert"])
        contract = self.contracts["dbUpdate"]
        self.check_contract(contract["code"], contract["asert"])
        
    def test_contract_idToAddress(self):
        contract = self.contracts["idToAddress"]
        self.check_contract(contract["code"], contract["asert"])    
        
    def test_contract_join(self):
        contract = self.contracts["join"]
        self.check_contract(contract["code"], contract["asert"])
        
    def test_contract_split(self):
        contract = self.contracts["split"]
        self.check_contract(contract["code"], contract["asert"])
        
    def test_contracts_dbUpdateExt(self):
        columns = """[{"name":"name","type":"varchar",
        "index": "1",  "conditions":"true"},
        {"name":"test","type":"varchar",
        "index": "0",  "conditions":"true"}]"""
        permission = """{"insert": "true",
        "update" : "true","new_column": "true"}"""
        data = {"Name": "test",
                "Columns": columns,
                "Permissions": permission}
        result = utils.call_contract(url, prKey, "NewTable", data, token)
        tx = utils.txstatus(url,
                                self.config["time_wait_tx_in_block"],
                                result['hash'], token)
        contract = self.contracts["dbInsert"]
        self.check_contract(contract["code"], contract["asert"])
        contract = self.contracts["dbUpdateExt"]
        self.check_contract(contract["code"], contract["asert"])
        
    def test_contract_callContract(self):
        contract = self.contracts["myContract"]
        code = "contract MyContract" + contract["code"]
        data = {"Value": code, "Conditions": "true"}
        res = utils.call_contract(url, prKey, "NewContract", data, token)
        time.sleep(10)
        contract = self.contracts["callContract"]
        self.check_contract(contract["code"], contract["asert"])
    
    def test_type_bool(self):
        contract = self.contracts["type_bool"]
        self.check_contract(contract["code"], contract["asert"])

    def test_type_bytes(self):
        contract = self.contracts["type_bytes"]
        self.check_contract(contract["code"], contract["asert"])

    def test_type_int(self):
        contract = self.contracts["type_int"]
        self.check_contract(contract["code"], contract["asert"])

    def test_type_address(self):
        contract = self.contracts["type_address"]
        self.check_contract(contract["code"], contract["asert"])

    def test_type_array(self):
        contract = self.contracts["type_array"]
        self.check_contract(contract["code"], contract["asert"])

    def test_type_map(self):
        contract = self.contracts["type_map"]
        self.check_contract(contract["code"], contract["asert"])

    def test_type_money(self):
        contract = self.contracts["type_money"]
        self.check_contract(contract["code"], contract["asert"])

    def test_type_float(self):
        contract = self.contracts["type_float"]
        self.check_contract(contract["code"], contract["asert"])

    def test_type_string(self):
        contract = self.contracts["type_string"]
        self.check_contract(contract["code"], contract["asert"])

    def test_uuid(self):
        contract = self.contracts["uuid"]
        self.check_contract(contract["code"], contract["asert"])
        
    def test_getBlock(self):
        contract = self.contracts["getBlock"]
        self.check_contract(contract["code"], contract["asert"])

    def test_getColumnType(self):
        contract = self.contracts["getColumnType"]
        self.check_contract(contract["code"], contract["asert"])

if __name__ == '__main__':
    unittest.main()
