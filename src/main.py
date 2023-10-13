import asyncio
import sys
from loguru import logger

from web3 import Web3

from config import Config, load_config
from core.data_sender import Web3Wrapper, gas_locker
from core.utils import configure_logger
from web3.eth import AsyncEth
from random import uniform


async def worker(
    q: asyncio.Queue,
    web3: Web3,
    config: Config,
    locker: asyncio.Lock,
) -> None:
    while not q.empty():
        if locker.locked():
            await asyncio.sleep(1)
            continue

        private_key = await q.get()

        try:
            w3 = Web3Wrapper(
                web3=web3,
                private_key=private_key
            )
        except Exception as err:
            logger.error(f"Error while creating Web3 object: {err}") # noqa: E501
            continue

        sleep_time = round(uniform(*config.SLEEP_BETWEEN_ACCOUNT_WORK), 3)
        logger.info(f"[{w3.account_address}] Sleep for {sleep_time} seconds") # noqa: E501
        await asyncio.sleep(sleep_time)

        if (gas_price := await w3.web3.eth.gas_price) > config.GAS_TARGET * 1e9:
            logger.info(
                f"[{w3.account_address}] Gas price is too "
                f"high ({gas_price / 1e9} gwei), skipping"
            )
            q.put_nowait(private_key)
            continue

        try:
            tx_hash = await w3.estimate_and_send_transaction(
                tx_params={
                    "to": config.CONTRACT,
                    "data": config.INPUT_DATA,
                    "value": config.VALUE,
                    **(await w3.eip1559_gas_price),
                }
            )
        except Exception as err:
            logger.error(f"[{w3.account_address}] Error while sending transaction: {err}") # noqa: E501
            continue

        logger.success(f"[{w3.account_address}] Transaction sent: {tx_hash.hex()}") # noqa: E501


async def main() -> None:
    config = load_config()

    web3 = Web3(
        Web3.AsyncHTTPProvider(config.RPC),
        middlewares=[],
        modules={"eth": (AsyncEth,)}
    )

    locker = asyncio.Lock()
    q = asyncio.Queue()

    asyncio.create_task(gas_locker(locker, web3, config.GAS_TARGET))

    with open("./src/private_keys.txt") as f:
        private_keys = f.read().splitlines()

    if not private_keys:
        logger.error("No private keys provided, exiting")
        sys.exit(1)

    [q.put_nowait(pk) for pk in private_keys]

    workers = [
        asyncio.create_task(worker(q, web3, config, locker))
        for _ in range(config.WORKERS_COUNT)
    ]

    await asyncio.gather(*workers)


if __name__ == "__main__":
    configure_logger()

    # Windows fix for closed event loop
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        logger.debug("Windows detected, using WindowsSelectorEventLoopPolicy")

    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
