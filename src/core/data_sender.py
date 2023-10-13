import asyncio

from eth_account import Account
from hexbytes import HexBytes
from loguru import logger
from web3 import Web3
from web3.types import TxParams


class Web3Wrapper:
    def __init__(
        self,
        web3: Web3,
        private_key: str,
    ) -> None:
        self.web3 = web3
        self.__account: Account = Account.from_key(private_key)

        self.account_address = self.__account.address

    async def estimate_and_send_transaction(
        self,
        tx_params: TxParams,
        gas_multiplier: int | float = 1.05,
    ) -> HexBytes:
        """
        Estimates gas and sends transaction with gas multiplyer
        
        :param tx_params: TxParams transaction parameters
        :param gas_multiplier: int | float gas multiplier

        :return: HexBytes transaction hash
        """
        if not self.web3.is_checksum_address(tx_params["to"]):
            tx_params["to"] = self.web3.to_checksum_address(tx_params["to"])

        if not tx_params.get("nonce"):
            tx_params["nonce"] = await self.web3.eth.get_transaction_count(
                self.account_address, "pending"
            )

        if not tx_params.get("from"):
            tx_params["from"] = self.account_address

        if not tx_params.get("chainId"):
            tx_params["chainId"] = await self.web3.eth.chain_id

        gas = await self.web3.eth.estimate_gas(tx_params)

        tx_params["gas"] = int(gas * gas_multiplier)
        signed_tx = self.__account.sign_transaction(tx_params)

        return await self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)

    @property
    async def eip1559_gas_price(self) -> dict[str, int]:
        """
        Returns a dict with maxPriorityFeePerGas and maxFeePerGas
        
        :return: dict[str, Wei]
        """
        base_fee = await self.web3.eth.gas_price

        max_priority_fee = await self.web3.eth.max_priority_fee

        return {
            "maxPriorityFeePerGas": max_priority_fee,
            "maxFeePerGas": (base_fee + max_priority_fee) * 2,
        }


async def gas_locker(
    locker: asyncio.Lock,
    web3: Web3,
    gas_target: float | int
) -> None:
    """
    Function to wait for gas price to drop below target
    Lock is used to prevent multiple calls to this function
    from different coroutines

    :param locker: asyncio.Lock instance
    :param web3: Web3 instance
    :param gas_target: float | int target gas price in gwei

    :return: None
    """

    # gas target from float to wei
    gas_target = gas_target * 1e9

    logger.info(f"Gas locker set to {gas_target / 1e9} gwei")

    await locker.acquire()

    while True:
        if (current_gas := await web3.eth.gas_price) > gas_target:
            if not locker.locked():
                await locker.acquire()

            logger.info(
                f"Current gas price: {current_gas / 1e9} gwei, "
                f"waiting for {gas_target / 1e9} gwei"
            )
            await asyncio.sleep(1)
        else:
            if locker.locked():
                locker.release()
                logger.info(f"Current gas price: {current_gas / 1e9} gwei. Proceeding.")
