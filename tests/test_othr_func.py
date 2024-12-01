import sys

from unittest.mock import MagicMock, patch
sys.path.append("./src")
from config import MOD_ID  # noqa: E402
import unittest  # noqa: E402
from othr_func import get_dollar_cost  # noqa: E402
from othr_func import moder  # noqa: E402
from othr_func import API_r  # noqa: E402
from othr_func import flip  # noqa: E402
from othr_func import moder_for_user  # noqa: E402


class othr_func_test(unittest.IsolatedAsyncioTestCase):
    async def test_flip(self):
        self.assertEqual(type(await flip()), str)

    async def test_dollar_cost(self):
        self.assertEqual(type(await get_dollar_cost()), str)

    async def test_moder_true(self):
        ctx = MagicMock()
        ctx.author.roles = [MagicMock(id=MOD_ID)]
        result = await moder(ctx)
        self.assertTrue(result)

    async def test_moder_false(self):
        ctx = MagicMock()
        ctx.author.roles = [MagicMock(id="126097107914970")]
        result = await moder(ctx)
        self.assertFalse(result)

    async def test_moder_multiple(self):
        ctx = MagicMock()
        ctx.author.roles = [MagicMock(id="017237610923921"), MagicMock(id="0391253721342375512"), MagicMock(id=MOD_ID)]
        result = await moder(ctx)
        self.assertTrue(result)

    async def test_moder_bad_value(self):
        ctx = MagicMock()
        ctx.author.roles = False
        with self.assertRaises(TypeError):
            await moder(ctx)

    async def test_moder_for_user_true(self):
        user = MagicMock()
        user.roles = [MagicMock(id=MOD_ID)]

        result = await moder_for_user(user)
        self.assertTrue(result)

    async def test_moder_for_user_false(self):
        user = MagicMock()
        user.roles = [MagicMock(id="1239124077142")]

        result = await moder_for_user(user)
        self.assertFalse(result)

    async def test_moder_for_user_false_multiple(self):
        user = MagicMock()
        user.roles = [MagicMock(id="1239124077142"), MagicMock(id="657567564341234"), MagicMock(id="11234125152")]

        result = await moder_for_user(user)
        self.assertFalse(result)

    async def test_moder_for_user_bad_value(self):
        user = MagicMock()
        user.roles = False
        with self.assertRaises(TypeError):
            await moder_for_user(user)

    @patch('httpx.AsyncClient')
    async def test_get_request_json_raw(self, mock_client):
        url = 'https://example.com/api/data'
        mock_response = MagicMock()
        mock_response.json.return_value = {'data': 'example'}
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

        api = API_r()
        result = await api.get_request_json_raw(url)
        self.assertEqual(result, {'data': 'example'})

    @patch('httpx.AsyncClient')
    async def test_get_request_json_raw_error(self, mock_client):
        url = 'https://example.com/api/data'
        mock_response = MagicMock()
        mock_response.json.side_effect = Exception('Ошибка')
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

        api = API_r()
        self.assertEqual(await api.get_request_json_raw(url), 'Ошибка! Подробнее: Ошибка')

    @patch('httpx.AsyncClient')
    async def test_get_request_json(self, mock_client):
        url = 'https://example.com/api/data'
        mock_response = MagicMock()
        mock_response.json.return_value = {'data': 'example'}
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        api = API_r()
        result = await api.get_request_json('data', url)
        self.assertEqual(result, 'example')

    @patch('httpx.AsyncClient')
    async def test_get_request_json_error(self, mock_client):
        url = 'https://example.com/api/data'
        mock_response = MagicMock()
        mock_response.json.side_effect = Exception("Error 404: not found!")
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        api = API_r()
        self.assertEqual(await api.get_request_json('data', url), 'Ошибка! Подробнее: Error 404: not found!')

    # @patch('othr_func.API_r')
    # async def test_get_iss_loc(self, mock_API_r):
    #     async def mock_get_request_json_raw(url):
    #         return {
    #         'iss_position': {'latitude': '12.3456', 'longitude': '78.9012'}
    #         }
    #     mock_API_r.return_value.get_request_json_raw = mock_get_request_json_raw
    #     result = await get_iss_loc()
    #     self.assertEqual(result, {'latitude': '12.3456', 'longitude': '78.9012'})


if __name__ == "__main__":
    unittest.main()
