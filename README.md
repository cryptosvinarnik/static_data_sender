# Script for sending transactions with static data. Suitable for nft mints, claims and so on. Created for warming up accounts in different chains.

## Run script
To run the main.py script, follow these steps:

- Open a terminal or command prompt.
- <code>git clone https://github.com/cryptosvinarnik/static_data_sender</code>
- Navigate to the directory where project is located (<code> cd dir/to/project</code>).
- INSTALL **Python3** AND **Pip3** (<a href="https://google.gik-team.com/?q=how+to+install+python3+and+pip">link</a>)
- Install the required dependencies by running <code>pip install -r requirements.txt</code>.
- Edit the config.yaml file to your desired settings.
- Run the script by running <code>python ./src/main.py</code>
- **..MAGIC!..**
- Subscribe to my <a href="https://t.me/cryptosvinarnik">channel</a>

## Configure config.yaml file!

*CONTRACT*: The address of the contract to interact with.

*INPUT_DATA*: The input data for the transaction.

*VALUE*: The value to send with the transaction.

*GAS_TARGET*: The gas target for the transaction running.

*RPC*: The URL of the Ethereum RPC node to use.

*SLEEP_BETWEEN_ACCOUNT_WORK*: The range of time to sleep between account work in seconds.

*WORKERS_COUNT*: The number of threads to use.
