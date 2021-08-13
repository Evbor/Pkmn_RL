import unittest
import subprocess
from unittest.mock import patch, MagicMock, AsyncMock
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

    async def patch__init_real_battle(self, showdown_uri, username, password, team):
        self._BattleClient__websocket = 'patched!'

    @patch.object(BattleClient, '_BattleClient__init_real_battle',
            new=patch__init_real_battle)
    def test_init_send_message(self):
        battle = BattleClient(self.team, self.username, self.showdown_uri,
                self.password
                )
        self.assertEqual(battle._BattleClient__websocket, 'patched!')

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
