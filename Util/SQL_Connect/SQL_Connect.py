import ConfigParser

def Get_Connect_ini():
    config = ConfigParser.ConfigParser()
    config.read('config.ini')
    SQL_Data = {
        'Host' :  config.get('SQL_Connect', 'Host'),
        'Account' :  config.get('SQL_Connect', 'Account'),
        'Password' :  config.get('SQL_Connect', 'Password'),
        'Database' :  config.get('SQL_Connect', 'Database')
    }

    return SQL_Data

