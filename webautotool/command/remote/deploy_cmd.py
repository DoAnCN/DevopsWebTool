# -*- conding: utf-8 -*-

from webautotool.config.log import logger

def deploy_cmd(server, instance, ver):
    log = logger('deploy')
    log.info("Deploying...")

    first_deploy = False

    inst_name = instance['data']['inst_name']
    url_remote = instance['data']['url_remote']
    db_name = instance['data']['db_name']
    version = instance['data']['version']

    dest_dir =  '/opt/web/{}'.format(instance['data']['inst_name'])

    if not server.check_remote_file(dest_dir):
        first_deploy = True
    if first_deploy:
        log.info("Clone project")
        server.git_clone(url_remote, dest_dir, version)
        server.create_db(dest_dir, db_name, inst_name)
    else:
        server.git_pull(ver, dest_dir )


