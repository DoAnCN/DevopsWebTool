# -*- conding: utf-8 -*-

from webautotool.config.log import logger

def deploy_cmd(server, instance, clone=False):
    log = logger('deploy')
    log.info("Deploying...")

    first_deploy = False
    if instance:
        inst_name = instance['name']
        url_remote = instance['project']['url']
        db_name = instance['db_name']
        version = instance['project_ver']['version']
        inst_type = instance['type']

        dest_dir =  '/opt/web/{}'.format(inst_name)

        if not server.check_remote_file(dest_dir):
            first_deploy = True
        if first_deploy:
            log.info("Clone project")
            server.git_clone(url_remote, dest_dir, version)
            if not clone:
                server.create_db(dest_dir, db_name, inst_name, inst_type)
        else:
            server.git_pull(version, dest_dir )
