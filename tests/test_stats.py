import sys
sys.path.append("./src")
import unittest
from unittest.mock import patch, AsyncMock
import asyncio
import stats.stats
from stats.stats import get_count_hist_for_mouth, get_channels_statistic, get_author_stat
from io import BytesIO
from PIL import Image

class TestGetCountHistForMouth(unittest.IsolatedAsyncioTestCase):

    @patch('stats.stats.db_connect', new_callable=AsyncMock)
    def test_get_count_hist_for_mouth(self, mock_db_connect):
        mock_cursor = AsyncMock()
        mock_db = AsyncMock()
        mock_db.cursor.return_value = mock_cursor
        mock_db_connect.return_value = mock_db

        mock_cursor.fetchall.return_value = [
            ('2024-11-01', 5),
            ('2024-11-02', 10),
            ('2024-11-03', 15)
        ]

        async def run_test():
            loop = asyncio.get_event_loop()
            result = await get_count_hist_for_mouth(11, 2024, loop)
            self.assertIsInstance(result, BytesIO)

        asyncio.run(run_test())
        
    
    @patch('stats.stats.db_connect', new_callable=AsyncMock)
    def test_get_count_hist_for_mouth_error(self, mock_db_connect):
        mock_cursor = AsyncMock()
        mock_db = AsyncMock()
        mock_db.cursor.return_value = mock_cursor
        mock_db_connect.return_value = mock_db

        mock_cursor.fetchall.return_value = None

        async def run_test():
            loop = asyncio.get_event_loop()
            with self.assertRaises(TypeError):
                await get_count_hist_for_mouth(11, 2024, loop)
        asyncio.run(run_test())


    @patch('stats.stats.db_connect', new_callable=AsyncMock)
    def test_get_channel_statistic(self, mock_db_connect):
        mock_cursor = AsyncMock()
        mock_db = AsyncMock()
        mock_db.cursor.return_value = mock_cursor
        mock_db_connect.return_value = mock_db

        mock_cursor.fetchall.return_value = [
            ('news', 22),
            ('voice1', 14),
            ('ping', 48),
            ("Galery", 5),
            ("mod_apels", 1),
            ("mod", 12)]

        async def run_test():
            loop = asyncio.get_event_loop()
            result = await get_channels_statistic(11, 2024, loop)
            # img = Image.open(result)
            # img.save('image.png', 'png')
            self.assertIsInstance(result, BytesIO)
        asyncio.run(run_test())


    @patch('stats.stats.db_connect', new_callable=AsyncMock)
    def test_get_channel_statistic_error(self, mock_db_connect):
        mock_cursor = AsyncMock()
        mock_db = AsyncMock()
        mock_db.cursor.return_value = mock_cursor
        mock_db_connect.return_value = mock_db

        mock_cursor.fetchall.return_value = None

        async def run_test():
            loop = asyncio.get_event_loop()
            with self.assertRaises(TypeError):
                await get_channels_statistic(2024, 11, loop)
        asyncio.run(run_test())


    @patch('stats.stats.db_connect', new_callable=AsyncMock)
    def test_get_author_statistic(self, mock_db_connect):
        mock_cursor = AsyncMock()
        mock_db = AsyncMock()
        mock_db.cursor.return_value = mock_cursor
        mock_db_connect.return_value = mock_db

        mock_cursor.fetchall.return_value = [
            ("User1", 450),
            ("User2", 348),
            ("User3", 457),
            ("User4", 123),
            ("User5", 312),
            ("User6", 52),
            ]

        async def run_test():
            loop = asyncio.get_event_loop()
            result = await get_author_stat(11, 2024, loop)
            # img = Image.open(result)
            # img.save('image.png', 'png')
            self.assertIsInstance(result, BytesIO)
        asyncio.run(run_test())


    @patch('stats.stats.db_connect', new_callable=AsyncMock)
    def test_get_author_statistic_error(self, mock_db_connect):
        mock_cursor = AsyncMock()
        mock_db = AsyncMock()
        mock_db.cursor.return_value = mock_cursor
        mock_db_connect.return_value = mock_db

        mock_cursor.fetchall.return_value = None

        async def run_test():
            loop = asyncio.get_event_loop()
            with self.assertRaises(TypeError):
                await get_author_stat(2024, 11, loop)
        asyncio.run(run_test()) 
    
    

if __name__ == '__main__':
    unittest.main()