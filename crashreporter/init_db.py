__author__ = 'calvin'

from hq.database import init_db

init_db()


from hq.tools import create_group, create_user



if __name__ == '__main__':

    grp = create_group('Sensoft')

    calvin = create_user('calvin@email.com', 'apple', name='Calvin', group=grp, admin=True, api_key='123456')
    print calvin.email, calvin.api_key
    adam = create_user('adam@email.com', 'banana', name='Adam', api_key='qwerty')
    print adam.email, adam.api_key

    asd=2


