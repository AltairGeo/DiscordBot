import sys

from unittest.mock import patch, AsyncMock
import unittest
import asyncio
sys.path.append("./src")
import othr_func  # noqa: F401, E402
from cogs.misc import Miscellaneous  # noqa: E402


class TestCogMisc(unittest.IsolatedAsyncioTestCase):
    @patch('othr_func.flip', new_callable=AsyncMock)
    def test_flip_command(self, mock_flip):
        mock_flip.return_value = "Орёл"
        bot_mock = AsyncMock()
        cog = Miscellaneous(bot_mock)
        ctx_mock = AsyncMock()

        async def run_flip():
            await cog.flip(cog, ctx_mock)

        asyncio.run(run_flip())
        mock_flip.assert_awaited_once()
        ctx_mock.respond.assert_awaited_once_with("Орёл")

    def test_members_count_command(self, new_callable=AsyncMock):
        ctx_mock = AsyncMock()
        ctx_mock.guild = AsyncMock()
        ctx_mock.guild.member_count = 100
        bot_mock = AsyncMock()
        cog = Miscellaneous(bot_mock)

        async def run_test():
            await cog.members_count(cog, ctx_mock)
        asyncio.run(run_test())
        ctx_mock.respond.assert_awaited_once_with("На сервере 100 человек.")

    @patch('othr_func.API_r')
    async def test_fox_command(self, mock_API_r):
        mock_API_r.return_value.get_request_json = AsyncMock(return_value="https://randomfox.ca/images/86.jpg")
        bot_mock = AsyncMock()
        ctx_mock = AsyncMock()
        cog = Miscellaneous(bot_mock)
        await cog.fox(cog, ctx_mock)
        ctx_mock.respond.assert_awaited_once_with("https://randomfox.ca/images/86.jpg")


if __name__ == '__main__':
    unittest.main()
