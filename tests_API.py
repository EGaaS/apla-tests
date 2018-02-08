import unittest
import utils
import config
import requests
import json
import funcs


class ApiTestCase(unittest.TestCase):
    def setUp(self):
        global url, token, prKey, pause
        self.config = config.readMainConfig()
        url = self.config["url"]
        pause = self.config["time_wait_tx_in_block"]
        prKey = self.config['private_key']
        self.data = utils.login(url, prKey)
        token = self.data["jwtToken"]

    def assertTxInBlock(self, result, jwtToken):
        self.assertIn("hash", result)
        hash = result['hash']
        status = utils.txstatus(url, pause, hash, jwtToken)
        if len(status['blockid']) > 0:
            self.assertNotIn(json.dumps(status), 'errmsg')
            return status["blockid"]
        else:
            return status["errmsg"]["error"]

    def check_get_api(self, endPoint, data, keys):
        end = url + endPoint
        result = funcs.call_get_api(end, data, token)
        for key in keys:
            self.assertIn(key, result)

    def check_post_api(self, endPoint, data, keys):
        end = url + endPoint
        result = funcs.call_post_api(end, data, token)
        for key in keys:
            self.assertIn(key, result)
            
    def get_error_api(self, endPoint, data):
        end = url + endPoint
        result = funcs.call_get_api(end, data, token)
        error = result["error"]
        message = result["msg"]
        return error, message

    def call(self, name, data):
        resp = utils.call_contract(url, prKey, name, data, token)
        resp = self.assertTxInBlock(resp, token)
        return resp

    def test_balance(self):
        asserts = ["amount", "money"]
        self.check_get_api('/balance/' + self.data['address'], "", asserts)
        
    def test_balance_incorrect_wallet(self):
        wallet = "0000-0990-3244-5453-2310"
        msg = "Wallet " + wallet + " is not valid"
        error, message = self.get_error_api('/balance/' + wallet, "")
        self.assertEqual(error, "E_INVALIDWALLET", "Incorrect error")

    def test_getEcosystem(self):
        asserts = ["number"]
        self.check_get_api("/ecosystems/", "", asserts)

    def test_get_param_ecosystem(self):
        asserts = ["list"]
        data = {'ecosystem': 1}
        self.check_get_api("/ecosystemparams/", data, asserts)

    def test_get_param_current_ecosystem(self):
        asserts = ["list"]
        self.check_get_api("/ecosystemparams/", "", asserts)

    def test_get_params_ecosystem_with_names(self):
        asserts = ["list"]
        data = {'ecosystem': 1, 'names': "name"}
        self.check_get_api("/ecosystemparams/", data, asserts)

    def test_get_parametr_of_current_ecosystem(self):
        asserts = ["id", "name", "value", "conditions"]
        data = {}
        self.check_get_api("/ecosystemparam/founder_account/", data, asserts)

    def test_get_tables_of_current_ecosystem(self):
        asserts = ["list", "count"]
        data = {}
        self.check_get_api("/tables", data, asserts)

    def test_get_table_information(self):
        asserts = ["name"]
        data = {}
        self.check_get_api("/table/contracts", data, asserts)
        
    def test_get_incorrect_table_information(self):
        table = "tab"
        data = {}
        error, message = self.get_error_api("/table/" + table, data)
        err = "E_TABLENOTFOUND"
        msg = "Table " + table + " has not been found"
        self.assertEqual(err, error, "Incorrect error")
        self.assertEqual(message, msg, "Incorrect error massege")

    def test_get_table_data(self):
        asserts = ["list"]
        data = {}
        self.check_get_api("/list/menu", data, asserts)
        
    def test_get_incorrect_table_data(self):
        table = "tab"
        data = {}
        error, message = self.get_error_api("/list/" + table, data)
        err = "E_TABLENOTFOUND"
        msg = "Table " + table + " has not been found"
        self.assertEqual(err, error, "Incorrect error")
        self.assertEqual(message, msg, "Incorrect error massege")

    def test_get_table_data_row(self):
        asserts = ["value"]
        data = {}
        self.check_get_api("/row/contracts/2", data, asserts)
        
    def test_get_incorrect_table_data_row(self):
        table = "tab"
        data = {}
        error, message = self.get_error_api("/row/" + table + "/2", data)
        err = "E_QUERY"
        msg = "DB query is wrong"
        self.assertEqual(err, error, "Incorrect errror")
        self.assertEqual(msg, message, "Incorrect error message")

    def test_get_contract_information(self):
        asserts = ["name"]
        data = {}
        self.check_get_api("/contract/MainCondition", data, asserts)
        
    def test_get_incorrect_contract_information(self):
        contract = "contract"
        data = {}
        error, message = self.get_error_api("/contract/" + contract, data)
        err = "E_CONTRACT"
        msg = "There is not " + contract + " contract"

    def test_create_ecosystem(self):
        name = "Ecosys" + utils.generate_random_name()
        data = {"name": name}
        res = self.call("NewEcosystem", data)

    def test_money_transfer(self):
        data = {"Recipient": "0005-2070-2000-0006-0200", "Amount": "1000"}
        self.call("MoneyTransfer", data)
        
    def test_money_transfer_incorrect_wallet(self):
        wallet = "0005-2070-2000-0006"
        msg = "Recipient " + wallet + " is invalid"
        data = {"Recipient": wallet, "Amount": "1000"}
        ans = self.call("MoneyTransfer", data)
        self.assertEqual(ans, msg, "Incorrect message" + msg)
        
    def test_money_transfer_zero_amount(self):
        wallet = "0005-2070-2000-0006-0200"
        msg = "Amount is zero"
        data = {"Recipient": wallet, "Amount": "ttt"}
        ans = self.call("MoneyTransfer", data)
        self.assertEqual(ans, msg, "Incorrect message" + msg)

    def test_money_transfer_with_comment(self):
        wallet = "0005-2070-2000-0006-0200"
        data = {"Recipient": wallet, "Amount": "1000", "Comment": "Test"}
        self.call("MoneyTransfer", data)

    def test_new_contract(self):
        code, name = utils.generate_name_and_code("")
        data = {"Value": code, "Conditions": "true"}
        self.call("NewContract", data)
        
    def test_new_contract_exists_name(self):
        code, name = utils.generate_name_and_code("")
        data = {"Value": code, "Conditions": "true"}
        self.call("NewContract", data)
        ans = self.call("NewContract", data)
        msg = "Contract or function " + name + " exists"
        self.assertEqual(ans, msg, "Incorrect message: " + ans)
        
    def test_new_contract_without_name(self):
        code = "contract {data { }    conditions {    }    action {    }    }"
        data = {"Value": code, "Conditions": "true"}
        self.call("NewContract", data)
        ans = self.call("NewContract", data)
        msg = "must be the name"
        self.assertIn(msg, ans, "Incorrect message: " + ans)
        
    def test_new_contract_incorrect_condition(self):
        code, name = utils.generate_name_and_code("")
        data = {"Value": code, "Conditions": "condition"}
        self.call("NewContract", data)
        ans = self.call("NewContract", data)
        msg = "unknown identifier condition"
        self.assertEqual(msg, ans, "Incorrect message: " + ans)

    def test_activate_contract(self):
        code, name = utils.generate_name_and_code("")
        data = {"Value": code, "Conditions": "true"}
        self.call("NewContract", data)
        id = funcs.get_contract_id(url, name, token)
        data2 = {"Id": id}
        self.call("ActivateContract", data2)
        
    def test_activate_incorrect_contract(self):
        id = "9999"
        data = {"Id": id}
        ans = self.call("ActivateContract", data)
        msg = "Contract " + id + " does not exist"
        self.assertEqual(msg, ans, "Incorrect message: " + ans)

    def test_deactivate_contract(self):
        code, name = utils.generate_name_and_code("")
        data = {"Value": code, "Conditions": "true"}
        self.call("NewContract", data)
        id = funcs.get_contract_id(url, name, token)
        data2 = {"Id": id}
        self.call("ActivateContract", data2)
        self.call("DeactivateContract", data2)
        
    def test_deactivate_incorrect_contract(self):
        id = "9999"
        data = {"Id": id}
        ans = self.call("DeactivateContract", data)
        msg = "Contract " + id + " does not exist"
        self.assertEqual(msg, ans, "Incorrect message: " + ans)

    def test_edit_contract_incorrect_condition(self):
        newWallet = "0005-2070-2000-0006-0200"
        code, name = utils.generate_name_and_code("")
        data = {"Value": code, "Conditions": "true"}
        self.call("NewContract", data)
        data2 = {}
        data2["Id"] = funcs.get_contract_id(url, name, token)
        data2["Value"] = code
        data2["Conditions"] = "tryam"
        data2["WalletId"] = newWallet
        ans = self.call("EditContract", data2)
        msg = "unknown identifier tryam"
        self.assertEqual(msg, ans, "Incorrect message: " + ans)
        
    def test_edit_contract(self):
        newWallet = "0005-2070-2000-0006-0200"
        code, name = utils.generate_name_and_code("")
        data = {"Value": code, "Conditions": "true"}
        self.call("NewContract", data)
        data2 = {}
        data2["Id"] = funcs.get_contract_id(url, name, token)
        data2["Value"] = code
        data2["Conditions"] = "true"
        data2["WalletId"] = newWallet
        self.call("EditContract", data2)
        end = url + "/contract/" + name
        ans = funcs.call_get_api(end, "", token)
        self.assertEqual(ans["address"], newWallet, "Wallet didn't change.")
        
    def test_edit_name_of_contract(self):
        newWallet = "0005-2070-2000-0006-0200"
        code, name = utils.generate_name_and_code("")
        data = {"Value": code, "Conditions": "true"}
        self.call("NewContract", data)
        data2 = {}
        data2["Id"] = funcs.get_contract_id(url, name, token)
        code1, name = utils.generate_name_and_code("")
        data2["Value"] = code1
        data2["Conditions"] = "true"
        data2["WalletId"] = newWallet
        msg = "Contracts or functions names cannot be changed"
        ans = self.call("EditContract", data2)
        self.assertEqual(msg, ans, "Incorrect message: " + ans)
        
    def test_edit_incorrect_contract(self):
        code, name = utils.generate_name_and_code("")
        newWallet = "0005-2070-2000-0006-0200"
        id = "9999"
        data2 = {}
        data2["Id"] = id
        data2["Value"] = code
        data2["Conditions"] = "true"
        data2["WalletId"] = newWallet
        ans = self.call("EditContract", data2)
        msg = "Item " + id + " has not been found"
        self.assertEqual(msg, ans, "Incorrect message: " + ans)

    def test_new_parameter(self):
        name = "Par_" + utils.generate_random_name()
        data = {"Name": name, "Value": "test", "Conditions": "true"}
        self.call("NewParameter", data)

    def test_edit_parameter(self):
        newVal = "test_edited"
        name = "Par_" + utils.generate_random_name()
        data = {"Name": name, "Value": "test", "Conditions": "true"}
        self.call("NewParameter", data)
        id = funcs.get_parameter_id(url, name, token)
        data2 = {"Id": id, "Value": newVal, "Conditions": "true"}
        self.call("EditParameter", data2)
        value = funcs.get_parameter_value(url, name, token)
        self.assertEqual(value, newVal, "Parameter didn't change")

    def test_new_menu(self):
        name = "Menu_" + utils.generate_random_name()
        data = {"Name": name, "Value": "Item1", "Conditions": "true"}
        self.call("NewMenu", data)
        content = {'tree': [{'tag': 'text', 'text': 'Item1'}]}
        mContent = funcs.get_content(url, "menu", name, "", token)
        self.assertEqual(mContent, content)

    def test_edit_menu(self):
        name = "Menu_" + utils.generate_random_name()
        data = {"Name": name, "Value": "Item1", "Conditions": "true"}
        self.call("NewMenu", data)
        count = funcs.get_count(url, "menu", token)
        dataEdit = {"Id": count, "Value": "ItemEdited", "Conditions": "true"}
        self.call("EditMenu", dataEdit)
        content = {'tree': [{'tag': 'text', 'text': 'ItemEdited'}]}
        mContent = funcs.get_content(url, "menu", name, "", token)
        self.assertEqual(mContent, content)

    def test_append_menu(self):
        name = "Menu_" + utils.generate_random_name()
        data = {"Name": name, "Value": "Item1", "Conditions": "true"}
        self.call("NewMenu", data)
        count = funcs.get_count(url, "menu", token)
        dataEdit = {"Id": count, "Value": "AppendedItem", "Conditions": "true"}
        self.call("AppendMenu", dataEdit)
        content = {'tree': [{'tag': 'text', 'text': 'Item1\r\nAppendedItem'}]}
        mContent = funcs.get_content(url, "menu", name, "", token)
        self.assertEqual(mContent, content)

    def test_new_page(self):
        name = "Page_" + utils.generate_random_name()
        data = {}
        data["Name"] = name
        data["Value"] = "Hello page!"
        data["Conditions"] = "true"
        data["Menu"] = "default_menu"
        self.call("NewPage", data)
        content = {}
        content["menu"] = 'default_menu'
        menutree = {}
        menutree["tag"] = 'menuitem'
        menutree["attr"] = {'page': 'Default Ecosystem Menu', 'title': 'main'}
        content["menutree"] = []
        content["tree"] = [{'tag': 'text', 'text': 'Hello page!'}]
        cont = funcs.get_content(url, "page", name, "", token)
        self.assertEqual(cont, content)

    def test_edit_page(self):
        name = "Page_" + utils.generate_random_name()
        data = {}
        data["Name"] = name
        data["Value"] = "Hello page!"
        data["Conditions"] = "true"
        data["Menu"] = "default_menu"
        self.call("NewPage", data)
        dataEdit = {}
        dataEdit["Id"] = funcs.get_count(url, "pages", token)
        dataEdit["Value"] = "Good by page!"
        dataEdit["Conditions"] = "true"
        dataEdit["Menu"] = "default_menu"
        self.call("EditPage", dataEdit)
        content = {}
        content["menu"] = 'default_menu'
        menutree = {}
        menutree["tag"] = 'menuitem'
        menutree["attr"] = {'page': 'Default Ecosystem Menu', 'title': 'main'}
        content["menutree"] = []
        content["tree"] = [{'tag': 'text', 'text': 'Good by page!'}]
        pContent = funcs.get_content(url, "page", name, "", token)
        self.assertEqual(pContent, content)

    def test_append_page(self):
        name = "Page_" + utils.generate_random_name()
        data = {}
        data["Name"] = name
        data["Value"] = "Hello!"
        data["Conditions"] = "true"
        data["Menu"] = "default_menu"
        self.call("NewPage", data)
        count = funcs.get_count(url, "pages", token)
        dataEdit = {}
        dataEdit["Id"] = funcs.get_count(url, "pages", token)
        dataEdit["Value"] = "Good by!"
        dataEdit["Conditions"] = "true"
        dataEdit["Menu"] = "default_menu"
        self.call("AppendPage", dataEdit)
        content = {}
        content["menu"] = 'default_menu'
        menutree = {}
        menutree["tag"] = 'menuitem'
        menutree["attr"] = {'page': 'Default Ecosystem Menu', 'title': 'main'}
        content["menutree"] = []
        content["tree"] = [{'tag': 'text', 'text': 'Hello!\r\nGood by!'}]
        pContent = funcs.get_content(url, "page", name, "", token)
        self.assertEqual(pContent, content)

    def test_new_block(self):
        name = "Block_" + utils.generate_random_name()
        data = {"Name": name, "Value": "Hello page!", "Conditions": "true"}
        self.call("NewBlock", data)

    def test_edit_block(self):
        name = "Block_" + utils.generate_random_name()
        data = {"Name": name, "Value": "Hello block!", "Conditions": "true"}
        self.call("NewBlock", data)
        count = funcs.get_count(url, "blocks", token)
        dataEdit = {"Id": count, "Value": "Good by!", "Conditions": "true"}
        self.call("EditBlock", dataEdit)

    def test_new_table(self):
        data = {}
        data["Name"] = "Tab_" + utils.generate_random_name()
        col1 = "[{\"name\":\"MyName\",\"type\":\"varchar\","
        col2 = "\"index\": \"1\",  \"conditions\":\"true\"}]"
        data["Columns"] = col1 + col2
        per1 = "{\"insert\": \"false\","
        per2 = " \"update\" : \"true\","
        per3 = " \"new_column\": \"true\"}"
        data["Permissions"] = per1 + per2 + per3
        self.call("NewTable", data)

    def test_edit_table(self):
        name = "Tab_" + utils.generate_random_name()
        data = {}
        data["Name"] = name
        col1 = "[{\"name\":\"MyName\",\"type\":\"varchar\","
        col2 = "\"index\": \"1\",  \"conditions\":\"true\"}]"
        data["Columns"] = col1 + col2
        per1 = "{\"insert\": \"false\","
        per2 = " \"update\" : \"true\","
        per3 = " \"new_column\": \"true\"}"
        data["Permissions"] = per1 + per2 + per3
        self.call("NewTable", data)
        dataEdit = {}
        dataEdit["Name"] = name
        col1 = "[{\"name\":\"MyName\",\"type\":\"varchar\","
        col2 = "\"index\": \"1\",  \"conditions\":\"true\"}]"
        data["Columns"] = col1 + col2
        per1E = "{\"insert\": \"true\","
        per2E = " \"update\" : \"true\","
        per3E = " \"new_column\": \"true\"}"
        dataEdit["Permissions"] = per1E + per2E + per3E
        self.call("EditTable", dataEdit)

    def test_new_column(self):
        nameTab = "Tab_" + utils.generate_random_name()
        data = {}
        data["Name"] = nameTab
        col1 = "[{\"name\":\"MyName\",\"type\":\"varchar\","
        col2 = "\"index\": \"1\",  \"conditions\":\"true\"}]"
        data["Columns"] = col1 + col2
        per1 = "{\"insert\": \"false\","
        per2 = " \"update\" : \"true\","
        per3 = " \"new_column\": \"true\"}"
        data["Permissions"] = per1 + per2 + per3
        self.call("NewTable", data)
        name = "Col_" + utils.generate_random_name()
        dataCol = {}
        dataCol["TableName"] = nameTab
        dataCol["Name"] = name
        dataCol["Type"] = "number"
        dataCol["Index"] = "0"
        dataCol["Permissions"] = "true"
        self.call("NewColumn", dataCol)

    def test_edit_column(self):
        nameTab = "tab_" + utils.generate_random_name()
        data = {}
        data["Name"] = nameTab
        col1 = "[{\"name\":\"MyName\",\"type\":\"varchar\","
        col2 = "\"index\": \"1\",  \"conditions\":\"true\"}]"
        data["Columns"] = col1 + col2
        per1 = "{\"insert\": \"false\","
        per2 = " \"update\" : \"true\","
        per3 = " \"new_column\": \"true\"}"
        data["Permissions"] = per1 + per2 + per3
        self.call("NewTable", data)
        name = "Col_" + utils.generate_random_name()
        dataCol = {}
        dataCol["TableName"] = nameTab
        dataCol["Name"] = name
        dataCol["Type"] = "number"
        dataCol["Index"] = "0"
        dataCol["Permissions"] = "true"
        self.call("NewColumn", dataCol)
        dataEdit = {"TableName": nameTab, "Name": name, "Permissions": "false"}
        self.call("EditColumn", dataEdit)

    def test_new_lang(self):
        data = {}
        data["Name"] = "Lang_" + utils.generate_random_name()
        data["Trans"] = "{\"en\": \"false\", \"ru\" : \"true\"}"
        self.call("NewLang", data)

    def test_edit_lang(self):
        name = "Lang_" + utils.generate_random_name()
        data = {}
        data["Name"] = name
        data["Trans"] = "{\"en\": \"false\", \"ru\" : \"true\"}"
        self.call("NewLang", data)
        dataEdit = {}
        dataEdit["Name"] = name
        dataEdit["Trans"] = "{\"en\": \"true\", \"ru\" : \"true\"}"
        self.call("EditLang", dataEdit)

    def test_new_sign(self):
        name = "Sign_" + utils.generate_random_name()
        data = {}
        data["Name"] = name
        value = "{ \"forsign\" :\"" + name
        value += "\" ,  \"field\" :  \"" + name
        value += "\" ,  \"title\": \"" + name
        value += "\", \"params\":[{\"name\": \"test\", \"text\": \"test\"}]}"
        data["Value"] = value
        data["Conditions"] = "true"
        self.call("NewSign", data)

    def test_edit_sign(self):
        name = "Sign_" + utils.generate_random_name()
        data = {}
        data["Name"] = name
        value = "{ \"forsign\" :\"" + name
        value += "\" ,  \"field\" :  \"" + name
        value += "\" ,  \"title\": \"" + name
        value += "\", \"params\":[{\"name\": \"test\", \"text\": \"test\"}]}"
        data["Value"] = value
        data["Conditions"] = "true"
        self.call("NewSign", data)
        count = funcs.get_count(url, "signatures", token)
        dataEdit = {}
        dataEdit["Id"] = count
        valueE = "{ \"forsign\" :\"" + name
        valueE += "\" ,  \"field\" :  \"" + name
        valueE += "\" ,  \"title\": \"" + name
        valueE += "\", \"params\":[{\"name\": \"test\", \"text\": \"test\"}]}"
        dataEdit["Value"] = valueE
        dataEdit["Conditions"] = "true"
        self.call("EditSign", dataEdit)

    def test_content_lang(self):
        nameLang = "Lang_" + utils.generate_random_name()
        data = {}
        data["Name"] = nameLang
        data["Trans"] = "{\"en\": \"fist\", \"ru\" : \"second\"}"
        self.call("NewLang", data)
        namePage = "Page_" + utils.generate_random_name()
        valuePage = "Hello, LangRes(" + nameLang + ")"
        dataPage = {}
        dataPage["Name"] = namePage
        dataPage["Value"] = valuePage
        dataPage["Conditions"] = "true"
        dataPage["Menu"] = "default_menu"
        self.call("NewPage", dataPage)
        content = {}
        content["menu"] = 'default_menu'
        menutree = {}
        menutree["tag"] = 'menuitem'
        menutree["attr"] = {'page': 'Default Ecosystem Menu', 'title': 'main'}
        content["menutree"] = []
        content["tree"] = [{'tag': 'text', 'text': 'Hello, fist'}]
        contentRu = {}
        contentRu["menu"] = 'default_menu'
        contentRu["menutree"] = []
        contentRu["tree"] = [{'tag': 'text', 'text': 'Hello, second'}]
        ruPContent = funcs.get_content(url, "page", namePage, "ru", token)
        pContent = funcs.get_content(url, "page", namePage, "", token)
        self.assertEqual(ruPContent, contentRu)
        self.assertEqual(pContent, content)

    def test_get_table_vde(self):
        asserts = ["name"]
        data = {"vde": "true"}
        self.check_get_api("/table/contracts", data, asserts)

    def test_create_vde(self):
        asserts = ["result"]
        data = {}
        #self.check_post_api("/vde/create", data, asserts)

if __name__ == '__main__':
    unittest.main()
