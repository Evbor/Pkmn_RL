import unittest
import json
import subprocess
from unittest.mock import patch, MagicMock, AsyncMock, Mock
from battle_client import BattleClient

class TestBattleClientReal(unittest.IsolatedAsyncioTestCase):
    """
    Test case for BattleClient object binding to a real battle
    """

    def setUp(self):
        # BattleClient configuration
        self.team = 'test_team'
        self.username = 'blahahahaXDRaR'
        self.showdown_uri = 'ws://localhost:8000/showdown/websocket'
        self.password = '1Parrot1!'
        # Starting local Pokemon Showdown server
        self.ps = subprocess.Popen(['./pokemon-showdown/pokemon-showdown'],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT
                )

    @patch.object(BattleClient, '_BattleClient__init_real_battle')
    def test_init_realness(self, mock_BattleClient):
        battle = BattleClient(self.team, self.username, self.showdown_uri,
                self.password
                )
        self.assertTrue(battle.real)

    @patch.object(BattleClient, '_BattleClient__init_real_battle')
    def test_init_send_message(self, mock_BattleClient):
        # Setup
        battle = BattleClient(self.team, self.username, self.showdown_uri,
                self.password
                )
        battle._BattleClient__websocket = AsyncMock()
        # Testing
        rooms = ['', 'testroomid']
        messages = ['/trn testuname,testavatar,testassert']
        for room in rooms:
            for message in messages:
                with self.subTest(message=message, room=room):
                    correct_message = '{}|{}'.format(room, message)
                    battle._BattleClient__loop.run_until_complete(battle._BattleClient__send_message(room,
                        message)
                        )
                    battle._BattleClient__websocket.send.assert_called_with(correct_message)

    @patch.object(BattleClient, '_BattleClient__init_real_battle')
    @patch('battle_client.requests.post')
    def test_init_login(self, mock_requests_post, mock_BattleClient):
        # Setup
        # - Defining MockResponse object
        class MockResponse:
            def __init__(self, text):
                self.text = text
        # - Instaniating BattleClient object and manually patching websocket attribute
        battle = BattleClient(self.team, self.username, self.showdown_uri,
                self.password
                )
        battle._BattleClient__websocket = AsyncMock()
        # Testing
        loggedin_tests = [True, False]
        assertion_tests = ['testassertionstring', ';;erroroccured']
        json_prefix_tests = [']', '', 'bad_prefix']

        for loggedin in loggedin_tests:
            for assertion_string in assertion_tests:
                for json_prefix in json_prefix_tests:
                    # Buidling mock data and response objects
                    mock_data = {
                            'curuser': {'loggedin': loggedin},
                            'assertion': assertion_string
                            }
                    mock_response_string = json_prefix + json.dumps(mock_data)
                    mock_response = MockResponse(mock_response_string)
                    with self.subTest(loggedin=loggedin,
                            assertion_string=assertion_string,
                            json_prefix=json_prefix):
                        # Patching posts calls to return constructed mock data
                        mock_requests_post.return_value = mock_response
                        # Testing function
                        if (loggedin and json_prefix == ']' and
                        assertion_string[0:2] != ';;'):
                            correct_message = ('|/trn '
                                '{},0,{}'.format(self.username, assertion_string))
                            battle._BattleClient__loop.run_until_complete(battle._BattleClient__login(self.username,
                                self.password, 'test_challstr')
                                )
                            battle._BattleClient__websocket.send.assert_called_with(correct_message)
                            # some tests about correct call
                        else:
                            with self.assertRaises(AssertionError):
                                battle._BattleClient__loop.run_until_complete(battle._BattleClient__login(self.username,
                                    self.password, 'test_challstr')
                                    )

    def tearDown(self):
        # Destroying BattleClient Config
        del self.team
        del self.username
        del self.showdown_uri
        del self.password
        # Killing local Pokemon Showdown server
        try:
            self.ps.terminate()
            self.ps.communicate(timeout=0.2)
        except subprocess.TimeoutExpired:
            print('Server did not terminate in time')
            self.ps.kill

        del self.ps

class TestBattleClientSim(unittest.TestCase):
    """
    Test case for BattleClient object binding to a simulated battle
    """

    def setUp(self):
        self.team = 'test_team'
        self.username = 'test_username'

    @patch.object(BattleClient, '_BattleClient__init_sim_battle')
    def test_init_realness(self, mock_BattleClient):
        battle = BattleClient(self.team, self.username)
        self.assertFalse(battle.real)

    def tearDown(self):
        del self.team
        del self.username

if __name__ == '__main__':
    unittest.main()
