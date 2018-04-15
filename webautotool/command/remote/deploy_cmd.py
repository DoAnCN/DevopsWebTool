# -*- conding: utf-8 -*-
import logging

def deploy_cmd(server, url):
    first_deploy = True
    proj_name = url.split("/")[1].replace(".git","")
    logging.info("%s"%proj_name)
    proj_dir = 'web-%s' % proj_name
    logging.info("%s" % proj_dir)
    dest_dir =  '/opt/web/%s' % proj_dir
    logging.info("%s" % dest_dir)
    if server.check_remote_file(dest_dir):
        logging.info("Check dest dir exists .git")
        git_dir = "%s/%s/%s" % (dest_dir, proj_dir, '.git')
        if server.check_remote_file(git_dir):
            print("Check git dir exists")
            logging.info("Check dest dir exists git dir")
            first_deploy = False
    print(first_deploy)
    if first_deploy:
        logging.info("Clone project")
        server.git_clone(url, dest_dir)
        server.create_db(dest_dir + "/lib/db.php")