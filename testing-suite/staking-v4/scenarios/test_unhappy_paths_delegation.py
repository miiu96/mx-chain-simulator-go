from chain_commander import *
from core.validatorKey import *
from delegation import create_new_delegation_contract, delegate
from core.wallet import Wallet
from network_provider.get_transaction_info import get_gasUsed_from_tx
from delegation import add_nodes, stake_nodes
from network_provider.get_delegation_info import get_delegation_contract_address_from_tx



# General:
# here will be tested most of the cases that should fail regarding interaction with staking providers

# Steps:
# 1) Create a new delegation contract with "createNewDelegationContract" function with less than 1250 egld.
#   1.1) Tx should fail
#   1.2) Check that wallet balance is the same like before sending the tx - gass fees
#   1.3) Check te error message after sending the tx
# 2) Create a new delegation contract with 1250 egld with 0% fees and 4900 egld delegation cap - tx should pass
# 3) Add a new key to the contract
# 4) Stake a key to the contract that is not added
#   4.1) Tx should fail
#   4.2) Check error of the tx
# 5) Stake the key from point 3)
#   5.1) Tx should fail
#   5.2) Check error of tx
# 6) Delegate with another user 1250 egld to the contract
# 7) Stake the key from point 3) - now tx should pass

def main():
    print("Happy testing")

def test_unhappy_paths_delegation():

    # add xEGLD to the test wallet
    AMOUNT_TO_MINT = "6500" + "000000000000000000"
    wallet_A = Wallet(Path("./wallets/walletKey_1.pem"))
    wallet_key_1 = ValidatorKey(Path("./validatorKeys/validatorKey_1.pem"))
    wallet_key_2 = ValidatorKey(Path("./validatorKeys/validatorKey_2.pem"))
    array_keys = [wallet_key_1, wallet_key_2]

    # check if minting is successful
    assert "success" in wallet_A.set_balance(AMOUNT_TO_MINT)

    # check if one block was added
    assert "success" in add_blocks(1)

    # check if wallet balance was added and is equal with AMOUNT_TO_MINT
    assert wallet_A.get_balance() == AMOUNT_TO_MINT

    # check if blocks are to move Epoch to 3. Transactions happens after Epoch 3
    assert "success" in add_blocks_until_epoch_reached(4)

    # check if Epoch was moved to 3.
    assert proxy_default.get_network_status().epoch_number == 4

    # === STEP 1 ==============================================================
    # create transaction
    tx_hash = create_new_delegation_contract(wallet_A, AMOUNT="1249000000000000000000",SERVICE_FEE="00",
                                             DELEGATION_CAP="00")

    # check if a new delegation contract with "createNewDelegationContract" function with less than 1250 egld is "fail"
    assert "fail" in add_blocks_until_tx_fully_executed(tx_hash)

    # add one block to finish the transaction
    assert "success" in add_blocks(1)

    # Check that wallet balance is the same like before sending the tx - gas fees
    assert int(AMOUNT_TO_MINT) == (int(wallet_A.get_balance()) + int(get_gasUsed_from_tx(tx_hash)))

    # === STEP 2 ==============================================================
    # Create a new delegation contract with 1250 egld with 0% fees and 4900 egld delegation cap

    # create transaction
    tx_hash = create_new_delegation_contract(wallet_A, AMOUNT="1250000000000000000000", SERVICE_FEE="00",
                                             DELEGATION_CAP="4900000000000000000000")

    # add blocks to finish the transaction
    assert "success" in add_blocks_until_tx_fully_executed(tx_hash)

    # === STEP 3 ==============================================================
    # Get Delegation contract address.
    SP_address_for_A = get_delegation_contract_address_from_tx(tx_hash)
    # Add a new key to the contract
    # add and stake_nodes
    tx_hash = add_nodes(wallet_A, SP_address_for_A, [array_keys[1]])
    assert "success" in add_blocks_until_tx_fully_executed(tx_hash)

    # === STEP 4 ==============================================================
    # Stake a key to the contract that is not added
    tx_hash = stake_nodes(wallet_A, SP_address_for_A, [array_keys[0]])
    assert "fail" in add_blocks_until_tx_fully_executed(tx_hash)

    # === STEP 5 ==============================================================
    # Stake the key from STEP 3
    tx_hash = stake_nodes(wallet_A, SP_address_for_A, [array_keys[1]])
    assert "fail" in add_blocks_until_tx_fully_executed(tx_hash)

    # === STEP 6 ==============================================================
    # Delegate with another user 1250 egld to the contract
    tx_hash = delegate(wallet_A, SP_address_for_A, 1250000000000000000000)
    assert "success" in add_blocks_until_tx_fully_executed(tx_hash)

    # === STEP 7 ==============================================================
    # Stake the key from point 3) - now tx should pass

    # Stake a key to the contract that was added
    tx_hash = stake_nodes(wallet_A, SP_address_for_A, [array_keys[1]])
    assert "success" in add_blocks_until_tx_fully_executed(tx_hash)

    # check if nodes are staked
    assert array_keys[1].get_status(SP_address_for_A) == "staked"


if __name__ == '__main__':
    main()
