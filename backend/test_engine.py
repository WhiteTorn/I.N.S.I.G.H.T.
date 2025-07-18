from insight_core.engines.mark_i_foundation_engine import MarkIFoundationEngine
from insight_core.config.config_manager import ConfigManager
import asyncio


async def test_engine():
    config_manager = ConfigManager()
    config_manager.load_config()

    MarkI = MarkIFoundationEngine(config_manager)
    result = await MarkI.get_daily_briefing('2025-07-17')
    print(result)

# Run the async function
asyncio.run(test_engine())