# -*- conding: utf-8 -*-

def deploy_cmd(server, url):
    first_deploy = True
    proj_name = url.split("/")[1].replace(".git","")
    proj_dir = 'web-%s' % proj_name
    dest_dir =  '/opt/web/%s' % proj_dir
    if not server.check_remote_file(dest_dir):
        # git_dir = "%s/%s/%s" % (dest_dir, proj_dir, '.git')
        # if not server.check_remote_file(git_dir):
        first_deploy = True

    if first_deploy:
        # server.git_clone(url, dest_dir)
        server.create_db(dest_dir + "/lib/db.php")