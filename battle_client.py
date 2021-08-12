import asyncio
import websockets
import requests
import json


class BattleClient:
    """
    Battle Client Object, binds to a battle, either a simulated one using a
    subprocess, or a real battle on a Showdown Server. Provides a public API,
    update_battle, to update the state of the battle given a battle action.

    Attributes
    ----------
    real {Bool}: Indicates if the battle is against a real person

    Methods
    -------
    update_battle(battle_action {String})-->List(String): updates battle
    """

    def __init__(self, team, username, showdown_uri=None, password=None):
        if showdown_uri and password:
            self.real = True
            self.websocket = None
            self.loop = asyncio.get_event_loop()
            self.loop.run_until_complete(
                self.__init_real_battle(showdown_uri, username, password, team)
                )
        elif not showdown_uri and not password:
            self.real = False
            self.battle = self.__init_sim_battle(username, team)
        else:
            raise ValueError('both showdown_url and password must be provided'
                             'or left as None')

    def update_battle(self, battle_action):
        """
        Updates the battle the client is bound to by having the active Pokemon
        perform :param battle_action:. Returns the updated battle state as a
        list of messages. For types of actions an active Pokemon could take
        see: https:

        :param battle_action {String}: command active Pokemon should execute

        ---> messages {List(String)}, a list of battle messages reflecting the
                                      current battle state
        """

        raise NotImplementedError

    async def __send_messages(self, room, messages):
        """
        Async task used send messages to the Pokemon Showdown server over a
        websocket.

        :param room {String}: room name of the chat room to send the messages
                              to
        :param messages {List(String)}: list of messages to pass to the
                                        specified room on the server

        ---> None
        """

        message = '{}|{}'.format(room, '|'.join(messages))
        await self.websocket.send(message)

    async def __login(self, username, password, challstr):
        """
        Async login task.
        """

        payload = {
            'act': 'login',
            'name': username,
            'pass': password,
            'challstr': challstr
            }
        r = requests.post('https://play.pokemonshowdown.com/action.php',
                data=payload
                )
        # asserting correct response
        assert r.text[0] == ']'

        data = json.loads(r.text[1:])
        # assert login went successfully
        assert data['curuser']['loggedin'] and data['assertion'][0:2] != ';;'

        assertion = data['assertion']
        await self.__send_messages('', messages)


    async def __init_real_battle(self, showdown_uri, username, password, team):
        """
        Creates a random battle on Pokemon Showdown server :param showdown_url:
        with user :param username: and Pokemon team :param team:.

        :param showdown_url {String}: URL of Pokemon Showdown server
        :param username {String}: username of user on server to login as
        :param password {String}: password of user
        :param team {String}: Pokemon team to use in format (...)

        ---> battle {websockets.WebSocketClientProtocol}, battle object for
                                                          real battles
        """

        self.websocket = await websockets.connect(showdown_uri)
        async for message in self.websocket:
            # if message is challstr ==> login given user
            if '|challstr|' == message[0:10]:
                await self.__login(username, password, message[10:])

    def __init_sim_battle(self, username, team):
        """
        Creates a Pokemon battle subprocess using the Pokemon Showdown battle
        simulator tool.
        """
        pass
