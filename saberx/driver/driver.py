from saberx.executers.threaddriver import ThreadExecuter
from saberx.actionparser.actionextractor import ActionExtractor
from configparser import SafeConfigParser
import time
import optparse
import os

CONFIG_FILE = "/etc/saberx/saberx.conf"
LOCK_FILE = "saberx.lock"

def drive():
    global CONFIG_FILE

    # parse args
    parser = optparse.OptionParser()
    parser.add_option('-f', action="store", dest="config", help="Config file.")
    options, args = parser.parse_args()

    if options.config:
        CONFIG_FILE = options.config

    config = __load_config()

    if not __sanitize_config(config):
        '''
            Config is not proper. Issue has been logged. Exiting SaberX
        '''

        exit(2)

    actionExtractor = ActionExtractor(configpath=config.get("action_plan"))
    if not actionExtractor.action_plan_loaded:

        '''
            Failed to load action plan. Issue has been loggeg. Exitting SaberX
        '''
        exit(2)

    if not __clear_existing_lock(config.get("lock_dir")):

        '''
            Issue has already been logged. Existting Saberx
        '''
        exit (2)

    action_groups = actionExtractor.get_action_groups()

    threadExecuter = ThreadExecuter(groups=action_groups)

    while True:
        if __can_aquire_lock(config.get("lock_dir")):
            worker_and_run_success = threadExecuter.spawn_workers(os.path.join(config.get("lock_dir"), LOCK_FILE))
            if not worker_and_run_success:

                '''
                    Either lock could not be aquired or release failed. Issue has been logged.
                    Exit SaberX
                '''
                exit(2)
        time.sleep(300)


def __clear_existing_lock(lock_dir):
    lock_file = os.path.join(lock_dir, LOCK_FILE)

    try:
        if os.path.exists(lock_file):
            os.unlink(lock_file)
        return True
    except Exception as e:

        '''
            Unable to clear stale lock. Log issue. Send false. Stale locks muct be removed
            or else runs wont take place
        '''
        return False

def __can_aquire_lock(lock_dir):
    lock_file = os.path.join(lock_dir, LOCK_FILE)

    if os.path.exists(lock_file):
        return False

    return True

def __load_config():
    parser = SafeConfigParser()
    parser.read(CONFIG_FILE)

    section = "DEFAULT"
    config = {}

    for param, value in parser.items(section):
        config[param] = value

    return config

def __sanitize_config(config):

    '''
        sanitize the config and log issues
    '''
    
    return True

if __name__ == "__main__":
    drive()
