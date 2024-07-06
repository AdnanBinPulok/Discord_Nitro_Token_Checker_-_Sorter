# Discord Token Checker

This script checks Discord tokens for their validity, Nitro subscription status, and Nitro Boost slots. It also identifies tokens that are eligible for Nitro redemption.

## Prerequisites

- Python 3.6+
- `pip` for installing dependencies

## Installation

1. Clone the repository:

```bash
git clone https://github.com/AdnanBinPulok/Discord_Nitro_Token_Checker_-_Sorter
cd Discord_Nitro_Token_Checker_-_Sorter
```

2. Install the required packages:

```bash
pip install -r requirements.txt
```

## Usage

1. Create a `tokens.txt` file in the root directory of the project and add your tokens, one per line.
2. Create a `proxies.txt` file in the root directory of the project and add your proxies, one per line (optional).

3. Run the script:

```bash
python main.py
```

## proxy.txt
```
username:password@ip:port
username:password@ip:port
username:password@ip:port
``` 

## Output

The script will generate the following output files in the `outputs` directory:

- `valid.txt`: List of valid tokens with their details.
- `invalid.txt`: List of invalid tokens.
- `nitro_unavailable.txt`: List of tokens without Nitro subscription.
- `nitro_redeeemable.txt`: List of tokens eligible for Nitro redemption.

## Notes

- The script uses asynchronous requests to speed up the token checking process.
- If proxies are provided, they will be used randomly for each token.

## License

This project is licensed under the MIT License.
