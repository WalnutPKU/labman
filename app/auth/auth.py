import hashlib

from app.db import get_db
from app.utils import rand_str


class Auth(object):

    @classmethod
    def encrypt_password(cls, password, src='plain_text', salt_len=8):
        if src == 'plain_text':
            hash1 = hashlib.md5(password.encode()).hexdigest()
        elif src == 'md5':
            hash1 = password
        else:
            raise ValueError('password src must be either plain_text or md5')
        salt = rand_str(salt_len)
        return salt + hashlib.md5((salt + hash1).encode()).hexdigest()

    @classmethod
    def check_password(cls, password, db_password, salt_len=8):
        salt = db_password[:salt_len]
        if salt + hashlib.md5((salt + password).encode()).hexdigest() == db_password:
            return True
        else:
            return False

    @classmethod
    def change_password(cls, uid, old_password, new_password, salt_len=8):
        db = get_db()
        user = db.auth.find_one({'uid': uid})
        if not cls.check_password(old_password, user['password']):
            return {'success': False, 'msg': 'Old password is not corrent!'}
        else:
            encrypted = cls.encrypt_password(new_password, 'md5')
            db.auth.update_one({'uid': uid}, {'$set': {'password': encrypted}})
            return {'success': True, 'msg': ''}

    @classmethod
    def verify_user(cls, username, password):
        db = get_db()
        user = db.auth.find_one({'username': username})
        if not user:
            return {'success': False, 'msg': 'The username does not exist!'}
        elif not cls.check_password(password, user['password']):
            return {'success': False, 'msg': 'Wrong password!'}
        else:
            return {'success': True, 'msg': ''}

    @classmethod
    def get_user_info(cls, username):
        db = get_db()
        user = db.auth.find_one({'username': username})
        return user

    @classmethod
    def add_new_user(cls, uid, username, password=None):
        if not password:
            password = username
        db = get_db()
        db.auth.insert_one({
            'uid': uid,
            'username': username,
            'password': cls.encrypt_password(username),
            'auth_level': 'member'
        })
