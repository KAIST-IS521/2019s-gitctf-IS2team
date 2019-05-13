import glob

from django.core.files.storage import default_storage
from django.shortcuts import render
from django.http import HttpResponse
from is521_ca.models import *
from is521_ca.utils import *
import json
import subprocess, time, os
from django.conf import settings

def index(request):
    uid = request.session.get('UID')

    if uid:
        user = User.objects.filter(uid=uid)[0]
        return HttpResponse("Hello {}\r\n".format(user))
    else:
        return HttpResponse("Not Logged in\r\n")

def auth(request):
    id = request.POST.get('id')
    pw = request.POST.get('pw')

    if id is None or pw is None:
        return HttpResponse("Login Failure - id,pw missing\r\n")

    users = User.objects.filter(uid=id)
    if users.count() != 1:
        return HttpResponse("Login Failure - id,pw incorrect\r\n")

    else:
        passwd_hash = sha1digest(pw.encode('utf-8'))

        if users[0].passwd == passwd_hash:
            request.session['UID'] = users[0].uid
            return HttpResponse("Authenticated with : {}\r\n".format(users[0]))
        return HttpResponse("Login Failure - id,pw incorrect\r\n")

def upload(request):
    uid = request.session.get('UID')

    if uid is None:
        return HttpResponse(False)
    if 'signkey' not in request.FILES:
        return HttpResponse(False)

    file = request.FILES['signkey']
    try:
        dearmored_filename = temp_filename(uid)
        orig_filename = dearmored_filename + ".orig"
        if os.path.exists(orig_filename) or os.path.exists(dearmored_filename):
            return HttpResponse("temp file exists, wait a seconds...\r\n")

        default_storage.save(orig_filename, file)

        retcode = subprocess.call(["gpg", orig_filename])

        if retcode != 0:
            return HttpResponse("gpg file is not valid format\r\n")

        retcode = subprocess.call(["gpg", "-o", dearmored_filename, "--dearmor", orig_filename])

        if retcode != 0:
            return HttpResponse("Error while dearmoring...\r\n")

        file_content = default_storage.open(temp_filename(uid)).read()

        user = User.objects.filter(uid=uid)[0]
        cert = Certificate(uid=user)
        cert.key = file_content
        cert.save()

        return HttpResponse(True)
    finally:
        # Always clean up temp directory
        try:
            for f in glob.glob(os.path.join(settings.BASE_DIR, "Keys/Temp/*")):
                os.remove(f)
        except:
            pass

def change(request):
    uid = request.session.get('UID')

    if uid is None:
        return HttpResponse("false\n")
    user = User.objects.get(uid=uid)

    def sanitize(s):
        # Todo: is this enough????
        banlist = ["..", "`", "$", "<", ">", "(", ")", "{", "}", ';', '|', '&', '*', '=', '?', '[', ']', '~', '#', '!', '%', '\\', '+', '\'']
        for ban in banlist:
            s = s.replace(ban, "")
        return s

    is_changed = False
    for info_key in ['lastname', 'firstname', 'email']:
        info_val = request.POST.get(info_key)
        if info_val is not None and info_val != '':
            is_changed = True
            setattr(user, info_key, sanitize(info_val))

    passwd = request.POST.get('passwd')
    if passwd is not None and passwd != '':
        is_changed = True
        user.passwd = sha1digest(passwd.encode('utf-8'))

    if is_changed:
        user.save()
        return HttpResponse("true\r\n")
    else:
        return HttpResponse("false\r\n")

def revoke_list(request):
    revoked_lists = Certificate.objects.filter(revoked=True).only("uid", "serial")
    revoked_lists = list(map(lambda x: (x.uid.uid, x.serial), revoked_lists))
    json_revoked_list_str = json.dumps(revoked_lists)

    return HttpResponse(json_revoked_list_str + "\r\n")

def revoke(request):
    uid = request.session.get('UID')

    if uid is None:
        return HttpResponse("false\n")

    user_cert_lists = Certificate.objects.filter(uid=uid, revoked=False).order_by("-serial")

    for user_cert in user_cert_lists:
        user_cert.revoked = True
        user_cert.save()

    return HttpResponse("true\n")


def download(request):
    uid = request.session.get('UID')

    if not uid:
        return HttpResponse(False)

    # default download target is uid
    download_target = request.POST.get('targetuid')
    if download_target is None:
        download_target = uid

    users = User.objects.filter(uid=download_target)
    if users.count() == 0:
        return HttpResponse(False)
    target_user = users[0]

    user_cert_lists = Certificate.objects.filter(uid=download_target, revoked=False).order_by("-serial")
    if user_cert_lists.count() == 0:
        return HttpResponse(False)

    cert = user_cert_lists[0]

    json_obj = {}
    json_obj['serial'] = cert.serial
    json_obj['uid'] = target_user.uid
    json_obj['first_name'] = target_user.firstname
    json_obj['last_name'] = target_user.lastname
    json_obj['email'] = target_user.email
    json_obj['key'] = cert.key.encode().hex()

    cert_str = json.dumps(json_obj)

    message, s = cert_sign(cert_str)

    signature = "{}".format(s.hex())
    file_form = dict()
    file_form['data'] = cert_str
    file_form['signature'] = signature

    response = HttpResponse(json.dumps(file_form), content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename=cert.json'
    return response

def verify(request):
    if 'verifykey' not in request.FILES:
        return HttpResponse(False)

    file = request.FILES['verifykey']
    try:
        file_content = file.read().decode('utf-8')
        cert = json.loads(file_content)

        # Validate cert format
        cert_data_str = cert['data']
        cert_sig = cert['signature']

        # Validate cert_str is utf-8 encoded
        d = cert_data_str.encode('utf-8')

        cert_data = json.loads(cert_data_str)

        # Validate cert metadata
        serial = int(cert_data['serial'])
        uid = cert_data['uid']
        first_name = cert_data['first_name']
        last_name = cert_data['last_name']
        email = cert_data['email']
        key = cert_data['key']

        # Validate cert signature
        sig_s = bytes.fromhex(cert_sig)

        # Validate if serial number exists
        # cert_obj = Certificate.objects.filter(serial=serial)[0]
    except:
        # Bad request format
        return HttpResponse(False)

    revoked_list = Certificate.objects.filter(revoked=True)
    revoked_list = map(lambda x: x.serial, revoked_list)

    if serial in revoked_list:
        return HttpResponse(False)

    if cert_verify(cert_data_str, sig_s):
        return HttpResponse(True)
    else:
        return HttpResponse(False)
