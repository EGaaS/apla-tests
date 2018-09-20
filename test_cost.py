import unittest
import time
import pytest
from genesis_blockchain_tools.crypto import sign
from genesis_blockchain_tools.crypto import get_public_key

from conftest import setup_vars

from libs import tools, actions, db


class TestCost():

    def setup_class(self):
        print("setup_class")
        self.u = unittest.TestCase()
        print("setup_class finished")
        TestCost.createContracts(setup_vars())

    def setup(self, setup_vars):
        print("setup")
        self.data = actions.login(setup_vars["conf"]["2"]["url"], setup_vars["keys"]["key2"], 0)
        self.token = self.data["jwtToken"]

    def getNodeBalances(self, setup_vars):
        nodeCount = len(setup_vars["conf"])
        i = 1
        nodeBalance = []
        while i < nodeCount + 1:
            nodeBalance.append(db.get_balance_from_db(setup_vars["conf"]["1"]["db"],
                                                      setup_vars["conf"][str(i)]["keyID"]))
            i = i + 1
        return nodeBalance

    @staticmethod
    def createContracts(setup_vars):
        global dataCreater
        dataCreater = actions.login(setup_vars["conf"]["1"]["url"], setup_vars["conf"]["1"]["private_key"], 0)
        tokenCreater = dataCreater["jwtToken"]
        contract = tools.read_fixtures("contracts")
        code = "contract CostContract" + contract["for_cost"]["code"]
        data = {"Wallet": "", "Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        print("wait: ", setup_vars["wait"])
        result = actions.call_contract(setup_vars["conf"]["1"]["url"], setup_vars["conf"]["1"]["private_key"],
                                       "NewContract", data, tokenCreater)
        status = actions.tx_status(setup_vars["conf"]["1"]["url"], setup_vars["wait"],
                                   result['hash'], tokenCreater)

    def activateContract(self, setup_vars):
        dataCreater = actions.login(setup_vars["conf"]["2"]["url"], setup_vars["conf"]["1"]["private_key"], 0)
        tokenCreater = dataCreater["jwtToken"]
        id = actions.get_contract_id(setup_vars["conf"]["2"]["url"], "CostContract", tokenCreater)
        data = {"Id": id}
        result = actions.call_contract(setup_vars["conf"]["2"]["url"], setup_vars["conf"]["1"]["private_key"],
                                       "ActivateContract", data, tokenCreater)

        status = actions.tx_status(setup_vars["conf"]["2"]["url"], setup_vars["wait"],
                                   result['hash'], tokenCreater)

    def deactivateContract(self, setup_vars):
        dataCreater = actions.login(setup_vars["conf"]["1"]["url"], setup_vars["conf"]["1"]["private_key"], 0)
        tokenCreater = dataCreater["jwtToken"]
        id = actions.get_contract_id(setup_vars["conf"]["1"]["url"], "CostContract", tokenCreater)
        data = {"Id": id}
        result = actions.call_contract(setup_vars["conf"]["1"]["url"], setup_vars["conf"]["1"]["private_key"],
                                       "DeactivateContract", data, tokenCreater)
        status = actions.tx_status(setup_vars["conf"]["1"]["url"], setup_vars["wait"], result['hash'], tokenCreater)

    def isCommissionsInHistory(self, setup_vars, nodeCommision, idFrom, platformaCommission, node):
        isNodeCommission = db.is_commission_in_history(setup_vars["conf"]["1"]["db"], idFrom,
                                                         setup_vars["conf"][str(node + 1)]["keyID"],
                                                         nodeCommision)
        isPlatformCommission = db.is_commission_in_history(setup_vars["conf"]["1"]["db"], idFrom,
                                                             setup_vars["conf"]["1"]["keyID"],
                                                             platformaCommission)
        if isNodeCommission and isPlatformCommission:
            return True
        else:
            return False

    def test_activated_contract(self, setup_vars):
        if actions.is_contract_activated(setup_vars["conf"]["2"]["url"], "CostContract", self.token) == False:
            self.activateContract(setup_vars())
        time.sleep(10)
        walletId = actions.get_activated_wallet(setup_vars["conf"]["2"]["url"],
                                                "CostContract", self.token)
        sumsBefore = db.get_user_token_amounts(setup_vars["conf"]["1"]["db"])
        summBefore = sum(summ[0] for summ in sumsBefore)
        bNodeBalance = self.getNodeBalances(setup_vars())
        tokenRunner, uid = actions.get_uid(setup_vars["conf"]["2"]["url"])
        signature = sign(setup_vars["keys"]["key2"], uid)
        pubRunner = get_public_key(setup_vars["keys"]["key2"])
        balanceRunnerB = db.get_balance_from_db_by_pub(setup_vars["conf"]["1"]["db"], pubRunner)
        dataRunner = actions.login(setup_vars["conf"]["2"]["url"], setup_vars["keys"]["key2"], 0)
        tokenRunner = dataRunner["jwtToken"]
        res = actions.call_contract(setup_vars["conf"]["2"]["url"], setup_vars["keys"]["key2"],
                                    "CostContract", {"State": 1}, tokenRunner)
        result = actions.tx_status(setup_vars["conf"]["2"]["url"], setup_vars["wait"], res["hash"], tokenRunner)
        time.sleep(10)
        node = db.get_block_gen_node(setup_vars["conf"]["1"]["db"], result["blockid"])
        sumsAfter = db.get_user_token_amounts(setup_vars["conf"]["1"]["db"])
        summAfter = sum(summ[0] for summ in sumsAfter)
        aNodeBalance = self.getNodeBalances(setup_vars())
        nodeCommission = 141620000000000000
        platformaCommission = 4380000000000000
        balanceRunnerA = db.get_balance_from_db_by_pub(setup_vars["conf"]["1"]["db"], pubRunner)
        balanceContractOwnerA = db.get_balance_from_db(setup_vars["conf"]["1"]["db"], walletId)
        inHistory = self.isCommissionsInHistory(setup_vars(), nodeCommission, setup_vars["conf"]["1"]["keyID"],
                                                platformaCommission, node)
        if node == 0:
            dictValid = dict(balanceRunner=balanceRunnerA,
                             platformBalance=aNodeBalance[0],
                             summ=summBefore,
                             history=inHistory)
            dictExpect = dict(balanceRunner=balanceRunnerB,
                              platformBalance=aNodeBalance[0],
                              summ=summBefore,
                              history=True)
        else:
            dictValid = dict(balanceRunner=balanceRunnerA,
                             platformBalance=aNodeBalance[0],
                             nodeBalance=aNodeBalance[node],
                             summ=summBefore,
                             history=inHistory)
            dictExpect = dict(balanceRunner=balanceRunnerB,
                              platformBalance=bNodeBalance[0] - nodeCommission,
                              nodeBalance=bNodeBalance[node] + nodeCommission,
                              summ=summAfter,
                              history=True)
        self.u.assertDictEqual(dictValid, dictExpect,
                                          "Error in comissions run activated contract")


    def test_deactive_contract(self, setup_vars):
        if actions.is_contract_activated(setup_vars["conf"]["2"]["url"], "CostContract", self.token) == True:
            self.deactivateContract(setup_vars())
        walletId = actions.get_activated_wallet(setup_vars["conf"]["2"]["url"],
                                                "CostContract", self.token)
        sumsBefore = db.get_user_token_amounts(setup_vars["conf"]["1"]["db"])
        summBefore = sum(summ[0] for summ in sumsBefore)
        bNodeBalance = self.getNodeBalances(setup_vars())
        tokenRunner, uid = actions.get_uid(setup_vars["conf"]["2"]["url"])
        signature = sign(setup_vars["keys"]["key2"], uid)
        pubRunner = get_public_key(setup_vars["keys"]["key2"])
        balanceRunnerB = db.get_balance_from_db_by_pub(setup_vars["conf"]["1"]["db"], pubRunner)
        dataRunner = actions.login(setup_vars["conf"]["2"]["url"], setup_vars["keys"]["key2"], 0)
        tokenRunner = dataRunner["jwtToken"]
        res = actions.call_contract(setup_vars["conf"]["2"]["url"], setup_vars["keys"]["key2"],
                                    "CostContract", {"State": 1}, tokenRunner)
        result = actions.tx_status(setup_vars["conf"]["2"]["url"], setup_vars["wait"], res["hash"], tokenRunner)
        time.sleep(10)
        node = db.get_block_gen_node(setup_vars["conf"]["1"]["db"], result["blockid"])
        sumsAfter = db.get_user_token_amounts(setup_vars["conf"]["1"]["db"])
        summAfter = sum(summ[0] for summ in sumsAfter)
        aNodeBalance = self.getNodeBalances(setup_vars())
        nodeCommission = 141620000000000000
        platformaCommission = 4380000000000000
        commission = nodeCommission + platformaCommission
        balanceRunnerA = db.get_balance_from_db_by_pub(setup_vars["conf"]["1"]["db"], pubRunner)
        balanceContractOwnerA = db.get_balance_from_db(setup_vars["conf"]["1"]["db"], walletId)
        inHistory = self.isCommissionsInHistory(setup_vars(), nodeCommission, dataRunner["key_id"],
                                                platformaCommission, node)
        if node == 0:
            dictValid = dict(balanceRunner=balanceRunnerA,
                             platformBalance=aNodeBalance[0],
                             summ=summBefore,
                             history=inHistory)
            dictExpect = dict(balanceRunner=balanceRunnerB - commission,
                              platformBalance=bNodeBalance[0] + commission,
                              summ=summAfter,
                              history=True)
        else:
            dictValid = dict(balanceRunner=balanceRunnerA,
                             platformBalance=aNodeBalance[0],
                             nodeBalance=aNodeBalance[node],
                             summ=summBefore,
                             history=inHistory)
            dictExpect = dict(balanceRunner=balanceRunnerB - commission,
                              platformBalance=bNodeBalance[0] + platformaCommission,
                              nodeBalance=bNodeBalance[node] + nodeCommission,
                              summ=summAfter,
                              history=True)
        self.u.assertDictEqual(dictValid, dictExpect,
                             "Error in comissions run deactivated contract")

    def test_activated_contract_with_err(self, setup_vars):
        if actions.is_contract_activated(setup_vars["conf"]["2"]["url"], "CostContract", self.token) == False:
            self.activateContract(setup_vars())
        walletId = actions.get_activated_wallet(setup_vars["conf"]["2"]["url"], "CostContract", self.token)
        balanceContractOwnerB = db.get_balance_from_db(setup_vars["conf"]["1"]["db"], walletId)
        balanceNodeOwnerB = db.get_balance_from_db(setup_vars["conf"]["1"]["db"], setup_vars["conf"]["2"]["keyID"])
        commisionWallet = db.get_commission_wallet(setup_vars["conf"]["1"]["db"], 1)
        balanceCommisionB = db.get_balance_from_db(setup_vars["conf"]["1"]["db"], commisionWallet)
        tokenRunner, uid = actions.get_uid(setup_vars["conf"]["2"]["url"])
        signature = sign(setup_vars["keys"]["key2"], uid)
        pubRunner = get_public_key(setup_vars["keys"]["key2"])
        balanceRunnerB = db.get_balance_from_db_by_pub(setup_vars["conf"]["1"]["db"], pubRunner)
        dataRunner = actions.login(setup_vars["conf"]["2"]["url"], setup_vars["keys"]["key2"], 0)
        tokenRunner = dataRunner["jwtToken"]
        res = actions.call_contract(setup_vars["conf"]["2"]["url"], setup_vars["keys"]["key2"],
                                    "CostContract", {"State": 0}, tokenRunner)
        hash = res["hash"]
        result = actions.tx_status(setup_vars["conf"]["2"]["url"], setup_vars["wait"], hash, tokenRunner)
        time.sleep(10)
        balanceContractOwnerA = db.get_balance_from_db(setup_vars["conf"]["1"]["db"], walletId)
        balanceNodeOwnerA = db.get_balance_from_db(setup_vars["conf"]["1"]["db"], setup_vars["conf"]["2"]["keyID"])
        balanceCommisionA = db.get_balance_from_db(setup_vars["conf"]["1"]["db"], commisionWallet)
        balanceRunnerA = db.get_balance_from_db_by_pub(setup_vars["conf"]["1"]["db"], pubRunner)
        dictValid = dict(balanceContractOwner=balanceContractOwnerA,
                         balanceNodeOwner=balanceNodeOwnerA,
                         balanceCommision=balanceCommisionA,
                         balanceRunner=balanceRunnerA)
        dictExpect = dict(balanceContractOwner=balanceContractOwnerB,
                          balanceNodeOwner=balanceNodeOwnerB,
                          balanceCommision=balanceCommisionB,
                          balanceRunner=balanceRunnerB)
        msg = "balanceContractOwnerA:" + str(balanceContractOwnerA) + "\n" + \
              "balanceContractOwnerE:" + str(balanceContractOwnerB) + "\n" + \
              "balanceNodeOwnerA:" + str(balanceNodeOwnerA) + "\n" + \
              "balanceNodeOwnerE:" + str(balanceNodeOwnerB) + "\n" + \
              "balanceCommisionA:" + str(balanceCommisionA) + "\n" + \
              "balanceCommisionE:" + str(balanceCommisionB) + "\n" + \
              "balanceRunnerA:" + str(balanceRunnerA) + "\n" + \
              "balanceRunnerE:" + str(balanceRunnerB) + "\n"
        self.u.assertDictEqual(dictValid, dictExpect, msg)

    def test_deactive_contract_with_err(self, setup_vars):
        if actions.is_contract_activated(setup_vars["conf"]["2"]["url"], "CostContract", self.token) == True:
            self.deactivateContract(setup_vars())
        walletId = actions.get_activated_wallet(setup_vars["conf"]["2"]["url"], "CostContract", self.token)
        balanceContractOwnerB = db.get_balance_from_db(setup_vars["conf"]["1"]["db"], walletId)
        balanceNodeOwnerB = db.get_balance_from_db(setup_vars["conf"]["1"]["db"], setup_vars["conf"]["2"]["keyID"])
        commisionWallet = db.get_commission_wallet(setup_vars["conf"]["1"]["db"], 1)
        balanceCommisionB = db.get_balance_from_db(setup_vars["conf"]["1"]["db"], commisionWallet)
        commission = db.get_system_parameter(setup_vars["conf"]["1"]["db"], "commission_size")
        tokenRunner, uid = actions.get_uid(setup_vars["conf"]["2"]["url"])
        signature = sign(setup_vars["keys"]["key2"], uid)
        pubRunner = get_public_key(setup_vars["keys"]["key2"])
        balanceRunnerB = db.get_balance_from_db_by_pub(setup_vars["conf"]["1"]["db"], pubRunner)
        dataRunner = actions.login(setup_vars["conf"]["2"]["url"], setup_vars["keys"]["key2"], 0)
        tokenRunner = dataRunner["jwtToken"]
        res = actions.call_contract(setup_vars["conf"]["2"]["url"], setup_vars["keys"]["key2"],
                                    "CostContract", {"State": 0}, tokenRunner)
        time.sleep(10)
        hash = res["hash"]
        result = actions.tx_status(setup_vars["conf"]["2"]["url"], setup_vars["wait"], hash, tokenRunner)
        balanceContractOwnerA = db.get_balance_from_db(setup_vars["conf"]["1"]["db"], walletId)
        balanceNodeOwnerA = db.get_balance_from_db(setup_vars["conf"]["1"]["db"], setup_vars["conf"]["2"]["keyID"])
        balanceCommisionA = db.get_balance_from_db(setup_vars["conf"]["1"]["db"], commisionWallet)
        balanceRunnerA = db.get_balance_from_db_by_pub(setup_vars["conf"]["1"]["db"], pubRunner)
        dictValid = dict(balanceContractOwner = balanceContractOwnerA,
                         balanceNodeOwner = balanceNodeOwnerA,
                         balanceCommision = balanceCommisionA,
                         balanceRunner = balanceRunnerA)
        dictExpect = dict(balanceContractOwner = balanceContractOwnerB,
                          balanceNodeOwner = balanceNodeOwnerB,
                          balanceCommision = balanceCommisionB,
                          balanceRunner = balanceRunnerB)
        msg = "balanceContractOwnerA:" + str(balanceContractOwnerA) + "\n" +\
        "balanceContractOwnerE:" + str(balanceContractOwnerB) + "\n" +\
        "balanceNodeOwnerA:" + str(balanceNodeOwnerA) + "\n" +\
        "balanceNodeOwnerE:" + str(balanceNodeOwnerB) + "\n" +\
        "balanceCommisionA:" + str(balanceCommisionA) + "\n" +\
        "balanceCommisionE:" + str(balanceCommisionB) + "\n" +\
        "balanceRunnerA:" + str(balanceRunnerA) + "\n" +\
        "balanceRunnerE:" + str(balanceRunnerB) + "\n"
        self.u.assertDictEqual(dictValid, dictExpect, msg)