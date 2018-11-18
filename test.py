from api_wrapper import RocketChat
from pprint import pprint

rocket = RocketChat('roncool', 'password', server_url='http://simpleserver.ga:3000')
pprint(rocket.me().json())
pprint(rocket.channels_list().json())
pprint(rocket.chat_post_message('good news everyone!', channel='GENERAL', alias='Farnsworth').json())
pprint(rocket.channels_history('GENERAL', count=5).json())

