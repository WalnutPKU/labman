from flask import Blueprint, flash, jsonify, redirect, render_template, request, session, url_for

from .member import Member
from app.auth import Auth


mod_member = Blueprint('mod_member', __name__, static_folder='../static')


@mod_member.route('/profile', strict_slashes=False, methods=['GET', 'POST'])
def profile():
    if 'uid' not in session:
        return redirect(url_for('mod_auth.signin'))
    member = Member.get_by_uid(session['uid'])
    if request.method == 'GET':
        supervisors = Member.list('Professor')
        return render_template('profile.html', member=member,
                               supervisors=supervisors)
    elif request.method == 'POST':
        if member.update(request.form):
            flash('Profile updated!', 'success')
        else:
            flash('Failed to update your profile!', 'error')
        return redirect(url_for('mod_overview.index'))


@mod_member.route('/profile/publications', methods=['POST', 'DELETE'])
def manage_self_publication():
    if 'uid' not in session:
        return redirect(url_for('mod_auth.signin'))
    member = Member.get_by_uid(session['uid'])
    if request.method == 'POST':
        member.add_publication(request.form)
        return redirect(url_for('mod_member.profile'))
    else:
        pass


@mod_member.route('/profile/avatar', methods=['POST'])
def avatar():
    if 'uid' not in session:
        return redirect(url_for('mod_auth.signin'))
    member = Member.get_by_uid(session['uid'])
    if 'file' in request.files:
        url = member.change_avatar(request.files['file'])
        return jsonify({'avatar_url': url})


@mod_member.route('/member/new', methods=['GET', 'POST'])
def add_member():
    if 'uid' not in session:
        return redirect(url_for('mod_auth.signin'))
    elif session['auth_level'] != 'admin':
        return render_template(
            'access_denied.html',
            info='You do not have the authority to add a member, '
                 'please contact the administrator.'
        )
    if request.method == 'GET':
        supervisors = Member.list('Professor')
        return render_template('new_member.html', member=Member(),
                               supervisors=supervisors)
    else:
        member = Member.new(request.form)
        if member:
            username = member.en_name.replace(' ', '').lower()
            username = Auth.add_new_user(member.uid, username)
            flash('Successfully added a new member, username is ' + username,
                  'success')
        else:
            flash('Failed to add a new member!', 'error')
        return redirect(url_for('mod_overview.index'))


@mod_member.route('/member/<int:uid>', methods=['GET', 'POST', 'DELETE'])
def view_member(uid):
    if 'uid' not in session:
        return redirect(url_for('mod_auth.signin'))
    if request.method == 'GET':
        member = Member.get_by_uid(uid)
        supervisors = Member.list('Professor')
        return render_template('member.html', member=member,
                               supervisors=supervisors)
    elif request.method == 'POST':
        member = Member.get_by_uid(uid)
        if member.update(request.form):
            flash('Member info updated!', 'success')
        else:
            flash('Failed to update the member info!', 'error')
        return redirect(url_for('mod_overview.index'))
    else:
        if Member.delete(uid):
            Auth.del_user(uid)
            flash('Successfully deleted a member!', 'success')
        else:
            flash('Failed to delete a member!', 'error')
        return ''


@mod_member.route('/member/<int:uid>/publications', methods=['POST', 'DELETE'])
def manage_publication(uid):
    if 'uid' not in session:
        return redirect(url_for('mod_auth.signin'))
    elif session['auth_level'] != 'admin':
        return render_template(
            'access_denied.html',
            info='You do not have the authority to add publications for '
                 'a member, please contact the administrator.'
        )
    member = Member.get_by_uid(uid)
    if request.method == 'POST':
        member.add_publication(request.form)
        return redirect(url_for('mod_member.view_member', uid=uid))
    else:
        pass
