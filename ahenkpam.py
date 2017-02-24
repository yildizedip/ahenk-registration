import subprocess
import argparse
import sys
from configparser import SafeConfigParser

from util import Util

file_source_common_password='configuration/common-password'
file_dest_common_password='/etc/pam.d/common-password'

file_source_common_session='configuration/common-session'
file_dest_common_session='/etc/pam.d/common-session'

file_source_common_session_noninteractive='configuration/common-session-noninteractive'
file_dest_common_session_noninteractive='/etc/pam.d/common-session-noninteractive'

file_source_libnss_ldap='configuration/libnss-ldap.conf'
file_dest_libnss_ldap='/etc/libnss-ldap.conf'

file_source_mkhomedir='configuration/mkhomedir'
file_dest_mkhomedir='/usr/share/pam-configs/mkhomedir'

file_source_nsswitch='configuration/nsswitch.conf'
file_dest_nsswitch='/etc/nsswitch.conf'

file_source_pam_ldap_conf='configuration/pam_ldap.conf'
file_dest_pam_ldap_conf='/etc/pam_ldap.conf'


file_source_nslcd_conf='configuration/nslcd.conf'
file_dest_nslcd_conf='/etc/nslcd.conf'

file_source_ahenk_conf ='configuration/ahenk.conf'
file_dest_ahenk_conf ='/etc/ahenk/ahenk.conf'


def execute(command, stdin=None, env=None, cwd=None, shell=True, result=True):

   try:
       process = subprocess.Popen(command, stdin=stdin, env=env, cwd=cwd, stderr=subprocess.PIPE,
                                  stdout=subprocess.PIPE, shell=shell)
       if result is True:
           result_code = process.wait()
           p_out = process.stdout.read().decode("unicode_escape")
           p_err = process.stderr.read().decode("unicode_escape")
           return result_code, p_out, p_err
       else:
           return None, None, None
   except Exception as e:
       return 1, 'Could not execute command: {0}. Error Message: {1}'.format(command, str(e)), ''


def install_packages():
    cmd = 'apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -qq libpam-ldap libnss-ldap nslcd'
    results = execute(cmd)
    if (results[0] == 0):
        print(results[1])

def configureAhenkConf():

    try:
        parser = SafeConfigParser()
        parser.read('configuration/ahenk.conf')
        parser.set('CONNECTION', 'host', lider_server_ip)
        parser.set('CONNECTION', 'port', '5222')
        parser.set('CONNECTION', 'receiverjid', 'lider_sunucu')
        parser.set('CONNECTION', 'receiverresource', 'Smack')
        parser.set('CONNECTION', 'servicename', lider_service_name)

        with open(file_source_ahenk_conf, 'w') as configfile:
            parser.write(configfile)
            print("Ahenk Configuration Finished..")


    except Exception as e:
        print(e)


def copyPamFiles():

    try:
        Util.copy_file(file_source_common_password,file_dest_common_password);

        Util.copy_file(file_source_common_session,file_dest_common_session);

        Util.copy_file(file_source_common_session_noninteractive,file_dest_common_session_noninteractive);

        Util.copy_file(file_source_libnss_ldap,file_dest_libnss_ldap);

        Util.copy_file(file_source_mkhomedir,file_dest_mkhomedir);

        Util.copy_file(file_source_nsswitch,file_dest_nsswitch);

        Util.copy_file(file_source_pam_ldap_conf,file_dest_pam_ldap_conf);

        Util.copy_file(file_source_nslcd_conf, file_dest_nslcd_conf);

        Util.copy_file(file_source_ahenk_conf,file_dest_ahenk_conf);

    except Exception as e:
        print(e)


def convert_files():
    try:
        content_libnss_ldap="base "+str(ldap_base_dn)+\
                            "\nuri ldap://"+str(ldap_server_ip)+ \
                            "\nldap_version 3" \
                            "\npam_password exop"

        Util.write_file(file_source_libnss_ldap, content_libnss_ldap)
        print("convert file:"+ file_source_libnss_ldap)

        content_pam_ldap_conf="base "+str(ldap_base_dn)+\
                              "\nuri ldap://"+str(ldap_server_ip)+ \
                              "\nldap_version 3" \
                              "\nrootbinddn "+str(ldap_root_dn)+\
                              "\npam_password crypt"

        Util.write_file(file_source_pam_ldap_conf, content_pam_ldap_conf)
        print("convert file:" + file_source_libnss_ldap)


        coontent_nscld_conf= "uid nslcd"+\
                            "\ngid nslcd"+\
                            "\nuri ldap://"+str(ldap_server_ip)+ \
                            "\nbase "+str(ldap_base_dn)

        Util.write_file(file_source_nslcd_conf, coontent_nscld_conf)


    except Exception as e:
        print(e)


def restartServices():
    try:
        print("nslcd, nscd ahenk services restarting...")
        cmd = '/etc/init.d/nslcd restart /etc/init.d/nscd restart /etc/init.d/ahenk restart'
        results = execute(cmd)
        if (results[0] == 0):
            print(results[1])

        print("nslcd, nscd ahenk services restarted...")
    except Exception as e:
        print(e)




# # install requried pam modle packages
# # cmd="apt-get update"
# # results=execute(cmd)
# # if(results[0]==0):
# #     print(results[1])
#
#install requried pam modle packages

#

lider_server_ip=input("Lütfen Lider Sunucu Adresini giriniz : ")
print("Ldap Sunucu IP : " + lider_server_ip)

lider_service_name=input("Lütfen Lider Servis Adını giriniz (Örn: im.mys.pardus.org)")
print("Lider Servis Adı : " + lider_service_name)

ldap_server_ip=input("Lütfen LDAP Sunucu Adresini giriniz : ")
print("Ldap Sunucu IP : " + ldap_server_ip)

ldap_base_dn=input("Lütfen LDAP Düğümü (base dn) giriniz (Örn:dc=mys,dc=pardus,dc=org) :")
print("LDAP Base Dn :" + ldap_base_dn)

ldap_root_user=input("Lütfen LDAP Admin Kullanıcısını giriniz:")

ldap_root_dn="cn="+str(ldap_root_user)+","+ldap_base_dn

print("LDAP Root Dn :" + ldap_root_dn)

install_ok= input("Kuruluma başlamak istiyor musunuz?(E):")
if install_ok=='E' or install_ok=='e' or install_ok =="":
    # install_packages()
    configureAhenkConf()
    convert_files()
    # copyPamFiles()
    # restartServices()
else:
    exit()

# try:
#     parser = argparse.ArgumentParser()
#     parser.add_argument("square", help="display a square of a given number",
#                         type=int)
#     args = parser.parse_args()
#
#     # print the square of user input from cmd line.
#     print(args.square ** 2)
#
#     # print all the sys argument passed from cmd line including the program name.
#     print(sys.argv)
#
#     # print the second argument passed from cmd line; Note it starts from ZERO
#     print(sys.argv[1])
# except:
#     e = sys.exc_info()[0]
#     print(e)