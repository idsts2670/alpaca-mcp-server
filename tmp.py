import asyncio
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import sys
import os
import argparse

# Import the actual MCP server functions
try:
    sys.path.insert(0, '/Users/satoshi.ido/Documents/alpaca-mcp-server')
    from alpaca_mcp_server import (
        get_stock_quote,
        get_option_contracts, 
        place_option_market_order
    )
    print("✅ Successfully imported Alpaca MCP server functions")
except ImportError as e:
    print(f"❌ Could not import MCP server functions: {e}")
    print("Make sure you're in the alpaca-mcp-server directory")
    sys.exit(1)

class AlpacaMCPClient:
    """
    Alpaca MCP client for paper trading.
    Connects to the Alpaca MCP server which uses paper trading by default.
    """
    
    def __init__(self):
        print("🔗 Connected to Alpaca MCP server (paper trading mode)")
    
    async def get_stock_quote(self, symbol: str) -> str:
        """Get real stock quote from Alpaca MCP server."""
        return await get_stock_quote(symbol)
    
    async def get_option_contracts(self, underlying_symbol: str, expiration_date=None, 
                                 strike_price_gte=None, strike_price_lte=None,
                                 type=None, status=None, **kwargs) -> str:
        """Get real option contracts from Alpaca MCP server."""
        # Convert string type to enum if needed
        from alpaca.trading.enums import ContractType, AssetStatus
        
        contract_type = None
        if type == "CALL":
            contract_type = ContractType.CALL
        elif type == "PUT":
            contract_type = ContractType.PUT
        
        asset_status = None
        if status == "ACTIVE":
            asset_status = AssetStatus.ACTIVE
        
        return await get_option_contracts(
            underlying_symbol=underlying_symbol,
            expiration_date=expiration_date,
            strike_price_gte=strike_price_gte,
            strike_price_lte=strike_price_lte,
            type=contract_type,
            status=asset_status
        )
    
    async def place_option_market_order(self, legs: List[Dict], order_class: str, 
                                      quantity: int, time_in_force: str = "DAY", **kwargs) -> str:
        """Place real option order via Alpaca MCP server (paper trading)."""
        print(f"   📤 Submitting order to Alpaca MCP server...")
        print(f"     Legs: {legs}")
        print(f"     Order class: {order_class}")
        print(f"     Quantity: {quantity}")
        
        # Convert time_in_force string to enum
        from alpaca.trading.enums import TimeInForce
        
        tif = TimeInForce.DAY
        if time_in_force.upper() == "GTC":
            tif = TimeInForce.GTC
        
        result = await place_option_market_order(
            legs=legs,
            order_class=order_class,
            quantity=quantity,
            time_in_force=tif
        )
        
        print(f"   📥 Response from MCP server:")
        print(f"     {result}")
        
        return result

class BullCallSpreadAlgorithm:
    """
    Algorithm to automatically place bull call spreads with options.
    
    Strategy (Debit Spread):
    - Buy call option with strike X% below current price (lower strike, long position)
    - Sell call option with strike Y% above current price (higher strike, short position)
    - Target expiration: approximately N weeks from now
    - Execute as single multi-leg order for atomic execution
    
    This creates a debit spread where you pay a net premium upfront.
    """
    
    def __init__(self, symbol="SPY", buy_percentage=3, sell_percentage=5, weeks_ahead=2):
        """
        Initialize the bull call spread algorithm.
        
        Args:
            symbol: Underlying symbol to trade (default: SPY)
            buy_percentage: Percentage below current price for long call (default: 3)
            sell_percentage: Percentage above current price for short call (default: 5)
            weeks_ahead: Weeks until expiration (default: 2)
        """
        self.mcp_client = AlpacaMCPClient()
        self.symbol = symbol
        self.buy_percentage = buy_percentage
        self.sell_percentage = sell_percentage
        self.weeks_ahead = weeks_ahead
        
    def parse_price_from_quote(self, quote_response: str) -> Optional[float]:
        """Parse stock price from the quote response string."""
        try:
            lines = quote_response.split('\n')
            bid_price = None
            ask_price = None
            
            for line in lines:
                line = line.strip()
                if 'Bid Price:' in line:
                    bid_price = float(line.split('$')[1].split()[0])
                elif 'Ask Price:' in line:
                    ask_price = float(line.split('$')[1].split()[0])
            
            if bid_price and ask_price:
                return (bid_price + ask_price) / 2  # Return midpoint
            
            return None
            
        except Exception as e:
            print(f"Error parsing quote: {e}")
            return None
    
    async def get_current_price(self) -> Optional[float]:
        """Get the current stock price from the latest quote."""
        try:
            quote_result = await self.mcp_client.get_stock_quote(self.symbol)
            return self.parse_price_from_quote(quote_result)
        except Exception as e:
            print(f"Error fetching {self.symbol} price: {e}")
            return None
    
    def calculate_strike_prices(self, current_price: float) -> tuple[float, float]:
        """Calculate target strike prices for the bull call spread."""
        # Calculate target strikes
        buy_strike_target = current_price * (1 - self.buy_percentage / 100)
        sell_strike_target = current_price * (1 + self.sell_percentage / 100)
        
        # Round to nearest $0.50 (common for options)
        buy_strike = round(buy_strike_target * 2) / 2
        sell_strike = round(sell_strike_target * 2) / 2
        
        return buy_strike, sell_strike
    
    def get_target_expiration_date(self) -> datetime:
        """Calculate target expiration date approximately weeks_ahead from now."""
        target_date = datetime.now() + timedelta(weeks=self.weeks_ahead)
        
        # Find the nearest Friday (typical option expiration)
        days_until_friday = (4 - target_date.weekday()) % 7
        if days_until_friday == 0 and target_date.weekday() != 4:
            days_until_friday = 7
            
        expiration_date = target_date + timedelta(days=days_until_friday)
        return expiration_date
    
    def parse_option_contracts(self, contracts_response: str, 
                             target_buy_strike: float, target_sell_strike: float) -> tuple[Optional[str], Optional[str]]:
        """Parse option contracts response to find the best matches."""
        try:
            contracts = []
            lines = contracts_response.split('\n')
            current_contract = {}
            
            for line in lines:
                line = line.strip()
                if line.startswith('Symbol:'):
                    if current_contract:
                        contracts.append(current_contract)
                    current_contract = {'symbol': line.split('Symbol:')[1].strip()}
                elif line.startswith('Strike Price:'):
                    strike_str = line.split('$')[1].split()[0]
                    current_contract['strike'] = float(strike_str)
                elif line.startswith('Type:'):
                    type_str = line.split('Type:')[1].strip()
                    if 'CALL' in type_str:
                        current_contract['type'] = 'CALL'
                    elif 'PUT' in type_str:
                        current_contract['type'] = 'PUT'
            
            if current_contract:
                contracts.append(current_contract)
            
            print(f"   Parsed {len(contracts)} contracts")
            
            # Find best matches
            buy_contract = None
            sell_contract = None
            min_buy_diff = float('inf')
            min_sell_diff = float('inf')
            
            for contract in contracts:
                if contract.get('type') == 'CALL' and contract.get('strike') and contract.get('symbol'):
                    strike = contract.get('strike')
                    symbol = contract.get('symbol')
                    
                    # Find closest to buy strike
                    buy_diff = abs(strike - target_buy_strike)
                    if buy_diff < min_buy_diff:
                        min_buy_diff = buy_diff
                        buy_contract = symbol
                    
                    # Find closest to sell strike
                    sell_diff = abs(strike - target_sell_strike)
                    if sell_diff < min_sell_diff:
                        min_sell_diff = sell_diff
                        sell_contract = symbol
            
            print(f"   Selected contracts:")
            print(f"     Buy: {buy_contract} (target: ${target_buy_strike:.2f})")
            print(f"     Sell: {sell_contract} (target: ${target_sell_strike:.2f})")
            
            return buy_contract, sell_contract
            
        except Exception as e:
            print(f"Error parsing contracts: {e}")
            return None, None
    
    async def find_option_contracts(self, buy_strike: float, sell_strike: float, 
                                  expiration_date: datetime) -> tuple[Optional[str], Optional[str]]:
        """Find option contracts matching the target strikes and expiration."""
        try:
            print(f"   Searching for contracts with strikes between ${min(buy_strike, sell_strike) - 2:.2f} and ${max(buy_strike, sell_strike) + 2:.2f}")
            print(f"   Target expiration: {expiration_date.date()}")
            
            contracts_result = await self.mcp_client.get_option_contracts(
                underlying_symbol=self.symbol,
                expiration_date=expiration_date.date(),
                strike_price_gte=str(min(buy_strike, sell_strike) - 2),
                strike_price_lte=str(max(buy_strike, sell_strike) + 2),
                type="CALL",
                status="ACTIVE"
            )
            
            buy_contract, sell_contract = self.parse_option_contracts(contracts_result, buy_strike, sell_strike)
            
            if buy_contract and sell_contract:
                print(f"   ✅ Found contracts:")
                print(f"     Buy: {buy_contract}")
                print(f"     Sell: {sell_contract}")
                return buy_contract, sell_contract
            else:
                print(f"   ❌ Could not find suitable contracts")
                return None, None
            
        except Exception as e:
            print(f"Error finding option contracts: {e}")
            return None, None
    
    async def place_bull_call_spread(self, buy_contract: str, sell_contract: str, 
                                   quantity: int = 1) -> str:
        """Place the bull call spread as a multi-leg order."""
        try:
            legs = [
                {"symbol": buy_contract, "side": "buy", "ratio_qty": 1},
                {"symbol": sell_contract, "side": "sell", "ratio_qty": 1}
            ]
            
            return await self.mcp_client.place_option_market_order(
                legs=legs,
                order_class="mleg",
                quantity=quantity,
                time_in_force="DAY"
            )
            
        except Exception as e:
            return f"Error placing bull call spread: {e}"
    
    async def execute_strategy(self, quantity: int = 1) -> str:
        """Execute the complete bull call spread strategy."""
        try:
            print(f"🚀 Starting Bull Call Spread Algorithm for {self.symbol}...")
            print(f"   Strategy: Buy {self.buy_percentage}% below, Sell {self.sell_percentage}% above, {self.weeks_ahead} weeks out")
            print(f"   Quantity: {quantity} spread(s)")
            
            # Step 1: Get current stock price
            print(f"\n1. Fetching current {self.symbol} price...")
            current_price = await self.get_current_price()
            
            if current_price is None:
                return f"❌ Failed to fetch current {self.symbol} price"
            
            print(f"   Current {self.symbol} price: ${current_price:.2f}")
            
            # Step 2: Calculate target strikes
            print("\n2. Calculating target strike prices...")
            buy_strike, sell_strike = self.calculate_strike_prices(current_price)
            print(f"   Buy strike ({self.buy_percentage}% below): ${buy_strike:.2f}")
            print(f"   Sell strike ({self.sell_percentage}% above): ${sell_strike:.2f}")
            
            # Step 3: Determine expiration date
            print("\n3. Determining expiration date...")
            expiration_date = self.get_target_expiration_date()
            print(f"   Target expiration: {expiration_date.strftime('%Y-%m-%d')}")
            
            # Step 4: Find option contracts
            print("\n4. Finding option contracts...")
            buy_contract, sell_contract = await self.find_option_contracts(
                buy_strike, sell_strike, expiration_date
            )
            
            if not buy_contract or not sell_contract:
                return "❌ Failed to find suitable option contracts"
            
            # Step 5: Place the order
            print("\n5. Placing bull call spread order...")
            order_result = await self.place_bull_call_spread(
                buy_contract, sell_contract, quantity
            )
            
            print("\n6. ✅ Strategy execution complete!")
            return order_result
            
        except Exception as e:
            return f"❌ Strategy execution failed: {e}"

def parse_arguments():
    """Parse command line arguments for strategy customization."""
    parser = argparse.ArgumentParser(
        description='Bull Call Spread Trading Algorithm',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tmp.py                           # Default: SPY, 3%/5%, 2 weeks, 1 spread
  python tmp.py --symbol AAPL             # Trade AAPL instead of SPY
  python tmp.py --buy-pct 2 --sell-pct 5   # 2% below, 5% above  
  python tmp.py --weeks 3 --quantity 2    # 3 weeks out, 2 spreads
  python tmp.py --symbol SPY --buy-pct 4 --sell-pct 8 --weeks 1 --quantity 3
        """
    )
    
    parser.add_argument(
        '--symbol', '-s',
        type=str,
        default='SPY',
        help='Underlying symbol to trade (default: SPY)'
    )
    
    parser.add_argument(
        '--buy-pct', '--buy-percentage',
        type=float,
        default=3.0,
        help='Percentage below current price for long call (default: 3.0)'
    )
    
    parser.add_argument(
        '--sell-pct', '--sell-percentage',
        type=float,
        default=5.0,
        help='Percentage above current price for short call (default: 5.0)'
    )
    
    parser.add_argument(
        '--weeks', '-w',
        type=int,
        default=2,
        help='Weeks until expiration (default: 2)'
    )
    
    parser.add_argument(
        '--quantity', '-q',
        type=int,
        default=1,
        help='Number of spreads to trade (default: 1)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show strategy parameters without executing (default: False)'
    )
    
    return parser.parse_args()

def print_strategy_summary(args):
    """Print a summary of the strategy parameters."""
    print("=" * 70)
    print("📊 BULL CALL SPREAD STRATEGY SUMMARY")
    print("=" * 70)
    print(f"Symbol:           {args.symbol}")
    print(f"Buy Strike:       {args.buy_pct}% below current price")
    print(f"Sell Strike:      {args.sell_pct}% above current price")
    print(f"Expiration:       ~{args.weeks} weeks from now")
    print(f"Quantity:         {args.quantity} spread(s)")
    print(f"Mode:             {'Dry Run (no execution)' if args.dry_run else 'Live Paper Trading'}")
    print("=" * 70)

async def main():
    """Main function to execute the bull call spread algorithm."""
    args = parse_arguments()
    
    # Print strategy summary
    print_strategy_summary(args)
    
    # Dry run mode - just show parameters
    if args.dry_run:
        print("\n🔍 DRY RUN MODE - No trades will be executed")
        print("Remove --dry-run flag to execute the strategy")
        return
    
    try:
        # Validate parameters
        if args.buy_pct <= 0 or args.sell_pct <= 0:
            print("❌ Error: Buy and sell percentages must be positive")
            return
        
        if args.weeks <= 0:
            print("❌ Error: Weeks must be positive")
            return
        
        if args.quantity <= 0:
            print("❌ Error: Quantity must be positive")
            return
        
        # Create and execute the algorithm
        algorithm = BullCallSpreadAlgorithm(
            symbol=args.symbol.upper(),
            buy_percentage=args.buy_pct,
            sell_percentage=args.sell_pct,
            weeks_ahead=args.weeks
        )
        
        result = await algorithm.execute_strategy(quantity=args.quantity)
        
        print("\n" + "=" * 70)
        print("📋 FINAL RESULT:")
        print("=" * 70)
        print(result)
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure you're in the alpaca-mcp-server directory")
        print("2. Set up your Alpaca API credentials:")
        print("   export ALPACA_API_KEY='your_paper_key'")
        print("   export ALPACA_SECRET_KEY='your_paper_secret'")
        print("   export ALPACA_PAPER_TRADE='True'")

if __name__ == "__main__":
    asyncio.run(main()) 