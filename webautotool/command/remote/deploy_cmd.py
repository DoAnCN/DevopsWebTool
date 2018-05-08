# -*- conding: utf-8 -*-

from DevopsWebTool.webautotool.config.log import logger

def deploy_cmd(server, url, ver):
    log = logger('deploy')
    log.info("Deploying...")
    first_deploy = False
    proj_name = url.split("/")[1].replace(".git","")
    proj_dir = 'web-%s' % proj_name
    dest_dir =  '/opt/web/%s' % proj_dir
    if not server.check_remote_file(dest_dir):
        first_deploy = True
    if first_deploy:
        log.info("Clone project")
        server.git_clone(url, dest_dir)
        server.create_db(dest_dir + "/lib/db.php")
    else:
        server.git_pull(ver, dest_dir )
