import ray
from wallet_tracker_agent.main import WalletTrackingAgent

ray.init()
wallet_agent = WalletTrackingAgent.remote()

ray.get(wallet_agent.add_wallet.remote("0x742d35Cc6634C0532925a3b844Bc454e4438f44e"))  # Example ETH wallet

results = ray.get(wallet_agent.process_wallets.remote())
for alert in results:
    print(alert["message"])

ray.get(wallet_agent.remove_wallet.remote("0x742d35Cc6634C0532925a3b844Bc454e4438f44e"))
