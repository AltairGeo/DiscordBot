import unittest
import sys

from unittest.mock import MagicMock, patch, AsyncMock
sys.path.append("./src")
import asyncio
import dswarn


class TestAddWarn(unittest.IsolatedAsyncioTestCase):
    @patch('dswarn.db_connect')
    async def test_add_warn_success(self, mock_db_connect):
        mock_db_connect.return_value = AsyncMock()
        mock_cursor = AsyncMock()
        mock_db_connect.return_value.cursor.return_value = mock_cursor
        mock_cursor.execute.return_value = AsyncMock()

        user_id = 123
        user_name = 'test_user'
        reason = 'test_reason'
        loop = asyncio.get_event_loop()

        result = await dswarn.add_warn(user_id, user_name, reason, loop)
        self.assertEqual(result, f"Выдано предупреждение пользователю {user_name}")


    @patch('dswarn.db_connect')
    async def test_add_warn_failure(self, mock_db_connect):
        mock_db_connect.return_value = AsyncMock()
        mock_cursor = AsyncMock()
        mock_db_connect.return_value.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = AsyncMock(side_effect=Exception('test_error'))

        user_id = 123
        user_name = 'test_user'
        reason = 'test_reason'
        loop = asyncio.get_event_loop()

        result = await dswarn.add_warn(user_id, user_name, reason, loop)
        self.assertEqual(result, 'Ошибка: test_error')


    @patch('dswarn.db_connect')
    async def test_delete_warn_success(self, mock_db_connect):
        mock_db_connect.return_value = AsyncMock()
        mock_cursor = AsyncMock()
        mock_db_connect.return_value.cursor.return_value = mock_cursor
        mock_cursor.execute.return_value = None
        mock_cursor.close.return_value = None
        mock_db_connect.return_value.commit.return_value = None

        ids = 123
        loop = asyncio.get_event_loop()

        result = await dswarn.delete_warn(ids, loop)
        self.assertEqual(result, 'Удалено!')


    @patch('dswarn.db_connect')
    async def test_delete_warn_failure(self, mock_db_connect):
        mock_db_connect.return_value = AsyncMock()
        mock_cursor = AsyncMock()
        mock_db_connect.return_value.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception('test_error')

        ids = 123
        loop = asyncio.get_event_loop()

        result = await dswarn.delete_warn(ids, loop)
        self.assertEqual(result, 'Ошибка: test_error')

    
    @patch('dswarn.db_connect')
    async def test_all_user_warn_success(self, mock_db_connect):
        mock_db_connect.return_value = AsyncMock()
        mock_cursor = AsyncMock()
        mock_db_connect.return_value.cursor.return_value = mock_cursor
        mock_cursor.execute.return_value = None
        mock_cursor.fetchall.return_value = [(1, 'test_user', 'test_reason')]

        user_id = 123
        loop = asyncio.get_event_loop()

        result = await dswarn.all_user_warn(user_id, loop)
        self.assertEqual(result, [(1, 'test_user', 'test_reason')])


    @patch('dswarn.db_connect')
    async def test_all_user_warn_failure(self, mock_db_connect):
        mock_db_connect.return_value = AsyncMock()
        mock_cursor = AsyncMock()
        mock_db_connect.return_value.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception('test_error')

        user_id = 123
        loop = asyncio.get_event_loop()

        result = await dswarn.all_user_warn(user_id, loop)
        self.assertEqual(result, 'Ошибка: test_error')

    
    @patch('dswarn.db_connect')
    async def test_get_count_warn_success(self, mock_db_connect):
        mock_db_connect.return_value = AsyncMock()
        mock_cursor = AsyncMock()
        mock_db_connect.return_value.cursor.return_value = mock_cursor
        mock_cursor.execute.return_value = None
        mock_cursor.fetchall.return_value = [(123, 5), (456, 3)]

        loop = asyncio.get_event_loop()

        result = await dswarn.get_count_warn(loop)
        self.assertEqual(result, [(123, 5), (456, 3)])

    @patch('dswarn.db_connect')
    async def test_get_count_warn_failure(self, mock_db_connect):
        mock_db_connect.return_value = AsyncMock()
        mock_cursor = AsyncMock()
        mock_db_connect.return_value.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception('test_error')

        loop = asyncio.get_event_loop()

        result = await dswarn.get_count_warn(loop)
        self.assertEqual(result, 'Ошибка: test_error')

    async def test_counter_succes(self):
        with self.subTest("Counter"):
            for i in range(20):
                counter = dswarn.counter(i)
                if i <= 10:
                    self.assertEqual(counter, 100)
                    print(f"test_counter_succes.subtest: ok {counter}")
                elif i <= 15:
                    self.assertEqual(counter, 105)
                    print(f"test_counter_succes.subtest: ok {counter}")
                elif i > 15:
                    self.assertEqual(counter, 200)
                    print(f"test_counter_succes.subtest: ok {counter}")