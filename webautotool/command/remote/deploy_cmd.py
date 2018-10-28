# -*- conding: utf-8 -*-

from webautotool.config.log import logger

def deploy_cmd(server, instance, ver):
    log = logger('deploy')
    log.info("Deploying...")

    first_deploy = False

    inst_name = instance['name']
    url_remote = instance['project']['url']
    db_name = instance['db_name']
    version = instance['project_ver']['name']

    dest_dir =  '/opt/web/{}'.format(instance['name'])

    if not server.check_remote_file(dest_dir):
        first_deploy = True
    if first_deploy:
        log.info("Clone project")
        server.git_clone(url_remote, dest_dir, version)
        server.create_db(dest_dir, db_name, inst_name)
    else:
        server.git_pull(ver, dest_dir )


