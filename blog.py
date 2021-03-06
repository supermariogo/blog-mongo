
# -*- coding: utf-8 -*-
#
# Copyright (c) 2008 - 2013 10gen, Inc. <http://10gen.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#



import pymongo
import blogPostDAO
import sessionDAO
import userDAO
import messageDAO
import appointmentDAO
import instDAO
import bottle
import cgi
import re
from mail import *
import datetime
import pprint



__author__ = 'Ze Mao'


# General Discussion on structure. This program implements a blog. This file is the best place to start to get
# to know the code. In this file, which is the controller, we define a bunch of HTTP routes that are handled
# by functions. The basic way that this magic occurs is through the decorator design pattern. Decorators
# allow you to modify a function, adding code to be executed before and after the function. As a side effect
# the bottle.py decorators also put each callback into a route table.

# These are the routes that the blog must handle. They are decorated using bottle.py
@bottle.route('/static/<filepath:path>')
def server_static(filepath):
    return bottle.static_file(filepath, root='static')

# This route is the main page of the blog
@bottle.route('/')
def blog_index():

    cookie = bottle.request.get_cookie("session")

    username = sessions.get_username(cookie)

    # even if there is no logged in user, we can show the blog
    guest_list = posts.get_posts_by_role("guest", 7)
    host_list = posts.get_posts_by_role("host", 7)

    return bottle.template('blog_template', dict(guest_posts=guest_list,host_posts=host_list, username=username, today=datetime.date.today()))



@bottle.get('/user/profile/<profile_username>')
def user_profile(profile_username=""):

    cookie = bottle.request.get_cookie("session")

    username = sessions.get_username(cookie)

    #show self
    if profile_username=="":
        profile_username = username


    guest_list = posts.get_posts_for_profile(profile_username, "guest")
    host_list = posts.get_posts_for_profile(profile_username, "host")

    return bottle.template('userprofile_template', dict(guest_posts=guest_list, host_posts=host_list, profile_username=profile_username, username=username))

# This route is the main page of the blog
@bottle.route('/user/home')
def user_home():
    bottle.redirect("/user/home/profile")


@bottle.route('/user/home/profile')
def user_home_profile():

    cookie = bottle.request.get_cookie("session")
    username = sessions.get_username(cookie)  # see if user is logged in
    if username is None:
        return bottle.template("login", dict(email="", password="", errors="Log in requreid", verify=""))
    user = users.get_user_by_username(username)

    return bottle.template('userhome_profile', dict(profile_username=username, username=username, user=user))


@bottle.route('/user/home/account')
def user_home_account():

    cookie = bottle.request.get_cookie("session")
    username = sessions.get_username(cookie)  # see if user is logged in
    if username is None:
        return bottle.template("login", dict(email="", password="", errors="Log in requreid", verify=""))
    user = users.get_user_by_username(username)

    return bottle.template('userhome_account', dict(username=username, error="", result=""))

@bottle.route('/user/home/updatepassword')
def user_home_updatepassword():

    cookie = bottle.request.get_cookie("session")
    username = sessions.get_username(cookie)  # see if user is logged in
    email = sessions.get_email(cookie)  # see if user is logged in

    if username is None:
        return bottle.template("login", dict(email="", password="", errors="Log in requreid", verify=""))
    user = users.get_user_by_username(username)


    old_password = bottle.request.forms.get("old_password")
    new_password = bottle.request.forms.get("new_password")
    confirm_password = bottle.request.forms.get("confirm_password")

    result = ""
    if new_password != confirm_password:
        result = "New password and confirm password are different"

    if users.validate_login(email, old_password) is None:
        result = "Wrong pasword"
    #TODO: need to change password

    return bottle.template('userhome_account', dict(username=username, result=result))

@bottle.route('/user/home/emails')
def user_home_emails():

    cookie = bottle.request.get_cookie("session")
    username = sessions.get_username(cookie)  # see if user is logged in
    if username is None:
        return bottle.template("login", dict(email="", password="", errors="Log in requreid", verify=""))
    user = users.get_user_by_username(username)

    return bottle.template('userhome_emails', dict(username=username, user=user))

@bottle.route('/user/home/history')
def user_home_history():

    cookie = bottle.request.get_cookie("session")
    username = sessions.get_username(cookie)  # see if user is logged in
    if username is None:
        return bottle.template("login", dict(email="", password="", errors="Log in requreid", verify=""))
    user = users.get_user_by_username(username)

    guest_list = posts.get_posts_for_profile(username, "guest")
    host_list = posts.get_posts_for_profile(username, "host")

    return bottle.template('userhome_history', dict(guest_posts=guest_list, host_posts=host_list, username=username, user=user))

@bottle.route('/user/home/invite')
def user_home_invite():

    cookie = bottle.request.get_cookie("session")
    username = sessions.get_username(cookie)  # see if user is logged in
    if username is None:
        return bottle.template("login", dict(email="", password="", errors="Log in requreid", verify=""))
    user = users.get_user_by_username(username)

    return bottle.template('userhome_invite', dict(profile_username=username, username=username, result=""))

@bottle.post('/user/home/invite')
def user_home_invite_post():
    email = bottle.request.forms.get("invited_email")
    message = bottle.request.forms.get("invite_message")

    cookie = bottle.request.get_cookie("session")
    username = sessions.get_username(cookie)
    print "------------"
    print email
    print message
    print username
    error = send_email(email, "Invitation from "+username, message)
    print error
    print "-------------"
    if error=="" :
        return bottle.template('userhome_invite', dict(profile_username=username, username=username, result="Successfully Send. Thank you! :)"))
    else:
        return bottle.template('userhome_invite', dict(profile_username=username, username=username, result="发送有点bug。。sorry。。"))



# This route is the main page of the blog
@bottle.get('/user/verify')
def user_verify():
    verify_result = users.user_email_verify(bottle.request.query['email'],bottle.request.query['key'])

    if verify_result is False:
        return bottle.template('error_template', dict(error="Invalid Email Verification"))
    else:
        return bottle.template("login", dict(email=bottle.request.query['email'], password="", errors="", verify="Successfully Verified! Please Log in."))

# The main page of the blog, filtered by tag
@bottle.route('/tag/<tag>')
def posts_by_tag(tag="notfound"):

    cookie = bottle.request.get_cookie("session")
    tag = cgi.escape(tag)

    username = sessions.get_username(cookie)

    # even if there is no logged in user, we can show the blog
    l = posts.get_posts_by_tag(tag, 10)

    return bottle.template('blog_template', dict(myposts=l, username=username))

@bottle.get('/search')
def search():

    cookie = bottle.request.get_cookie("session")
    q = bottle.request.query['q']
    l = insts.search_insts_by_alias(q)
    return bottle.template('{{s}}', dict(s=l))

# Displays a particular blog post
@bottle.get("/post/<permalink>")
def show_post(permalink="notfound"):

    cookie = bottle.request.get_cookie("session")

    username = sessions.get_username(cookie)
    permalink = cgi.escape(permalink)

    print "about to query on permalink = ", permalink
    post = posts.get_post_by_permalink(permalink)
    #it's possible that new keys are added but old post don't have it: keyError.
    add_new_keys(post)

    if post is None:
        bottle.redirect("/post_not_found")

    # init comment form fields for additional comment
    comment = {'name': "", 'body': "", 'email': ""}

    return bottle.template("entry_template", dict(post=post, username=username, errors="", comment=comment))


# used to process a comment on a blog post
@bottle.post('/newcomment')
def post_new_comment():

    body = bottle.request.forms.get("body")
    permalink = bottle.request.forms.get("permalink")

    cookie = bottle.request.get_cookie("session")
    username = sessions.get_username(cookie)
    if username is None:
        bottle.redirect("/login")
    author = username

    # it all looks good, insert the comment into the blog post and redirect back to the post viewer
    posts.add_comment(permalink, author, body)

    bottle.redirect("/post/" + permalink)

# used to process a like on a blog post
@bottle.post('/like')
def post_comment_like():
    permalink = bottle.request.forms.get("permalink")
    permalink = cgi.escape(permalink)

    comment_ordinal_str = bottle.request.forms.get("comment_ordinal")

    comment_ordinal = int(comment_ordinal_str)

    post = posts.get_post_by_permalink(permalink)
    if post is None:
        bottle.redirect("/post_not_found")
        return

    # it all looks good. increment the ordinal
    posts.increment_likes(permalink, comment_ordinal)

    bottle.redirect("/post/" + permalink)



@bottle.get("/post_not_found")
def post_not_found():
    return "Sorry, post not found"


# Displays the form allowing a user to add a new post. Only works for logged in users
@bottle.get('/newpost')
def get_newpost():
    try:
        role_from_get = bottle.request.query['role']
    except:
        role_from_get = "guest"
    cookie = bottle.request.get_cookie("session")
    username = sessions.get_username(cookie)  # see if user is logged in
    if username is None:
        bottle.redirect("/login")

    return bottle.template("editpost_template", dict(post=None, username=username, errors="", type="newpost", role_from_get=role_from_get))

#
# Post handler for setting up a new post.
# Only works for logged in user.
@bottle.post('/newpost')
def post_newpost():

    post = bottle.request.forms
    valid_post = {}
    cookie = bottle.request.get_cookie("session")
    username = sessions.get_username(cookie)  # see if user is logged in
    if username is None:
        bottle.redirect("/login")

    errors=''
    try:
        if post["title"] == "":
            errors += 'Need a title !\n'
        if post["price"] == "":
            errors += "Price ???\n"
    except:
        errors += "Key Error!"

    try:
        valid_post["deliver_time"]=datetime.datetime.strptime(post["deliver_time"], '%m/%d/%Y %I:%M %p')
    except:
        errors += "吃饭时间格式不对！"

    if errors is not '':
        return bottle.template("editpost_template", dict(post=post, errors=errors, username=username, type="newpost"))


    # prepare for the post, only copy valid data in case of spam into DB

    valid_post["author"] = username
    valid_post["status"] = 0 # 0:pending 1:complete
    valid_keys_list = ["role", "price", "title", "body", "payment_method", "deliver_method", "requirements", "phone", "wechat", "category"]
    for key in valid_keys_list:
        valid_post[key] = post[key]

    permalink = posts.insert_entry(valid_post)
    posts.add_guest_or_host(permalink, valid_post['role'], username)
    # now bottle.redirect to the blog permalink
    bottle.redirect("/post/" + permalink)

# remove a particular blog post
@bottle.get("/removepost/<permalink>")
def remove_post(permalink="notfound"):

    cookie = bottle.request.get_cookie("session")

    username = sessions.get_username(cookie)
    permalink = cgi.escape(permalink)
    if username is None:
        bottle.redirect("/login")

    post = posts.remove_post_by_permalink(permalink)
    bottle.redirect("/")

# update a particular blog post
@bottle.get("/updatepost/<permalink>")
def get_updatepost(permalink="notfound"):

    cookie = bottle.request.get_cookie("session")

    username = sessions.get_username(cookie)
    permalink = cgi.escape(permalink)

    print "(update)about to query on permalink = ", permalink
    post = posts.get_post_by_permalink(permalink)

    if post is None:
        bottle.redirect("/post_not_found")

    return bottle.template("editpost_template", dict(post=post, errors="", username=username, type="updatepost"))

@bottle.post("/updatepost/<permalink>")
def post_updatepost(permalink="notfound"):
    post = bottle.request.forms
    valid_post = {}
    cookie = bottle.request.get_cookie("session")
    username = sessions.get_username(cookie)  # see if user is logged in
    permalink = cgi.escape(permalink)

    if username is None:
        bottle.redirect("/login")

    errors=''
    try:
        if post["title"] == "":
            errors += 'Need a title !\n'
        if post["price"] == "":
            errors += "Price ???\n"
    except:
        errors += "Key Error!"

    try:
        valid_post["deliver_time"]=datetime.datetime.strptime(post["deliver_time"], '%m/%d/%Y %I:%M %p')
    except:
        errors += "吃饭时间格式不对！"

    if errors is not '':
        return bottle.template("editpost_template", dict(post=post, errors=errors, username=username, tpye="updatepost"))

    # prepare for the post, only copy valid data in case of spam into DB

    valid_post["author"] = username
    valid_keys_list = ["role", "price", "title", "body", "payment_method", "deliver_method", "requirements", "phone", "wechat", "category"]
    for key in valid_keys_list:
        valid_post[key] = post[key]

    posts.update_entry(permalink, valid_post)
    if valid_post["role"] == "guest":
        posts.remove_guest_or_host(permalink, "host", username)
        posts.add_guest_or_host(permalink, "guest", username)
    elif valid_post["role"] == "host":
        posts.remove_guest_or_host(permalink, "guest", username)
        posts.add_guest_or_host(permalink, "host", username)
    # now bottle.redirect to the blog permalink
    bottle.redirect("/post/" + permalink)

# displays the initial blog signup form
@bottle.get('/signup')
def present_signup():
    return bottle.template("signup",
                           dict(email="", password="",
                                username="", errors=""))

# displays the initial blog login form
@bottle.get('/login')
def present_login():
    return bottle.template("login", dict(email="", password="", errors="", verify=""))

# handles a login request
@bottle.post('/login')
def process_login():

    email = bottle.request.forms.get("email")
    password = bottle.request.forms.get("password")

    print "user submitted ", email, "pass ", password

    user_record = users.validate_login(email, password)
    if user_record:
        # email is stored in the user collection in the _id key
        session_id = sessions.start_session(user_record['_id'], user_record['username'])

        if session_id is None:
            bottle.redirect("/internal_error")

        cookie = session_id

        # Warning, if you are running into a problem whereby the cookie being set here is
        # not getting set on the redirect, you are probably using the experimental version of bottle (.12).
        # revert to .11 to solve the problem.
        bottle.response.set_cookie("session", cookie)

        bottle.redirect("/user/home")

    else:
        return bottle.template("login",dict(email=email, password="",errors="Invalid Login", verify=""))


@bottle.get('/internal_error')
@bottle.view('error_template')
def present_internal_error():
    return {'error':"System has encountered a DB error"}


@bottle.get('/logout')
def process_logout():

    cookie = bottle.request.get_cookie("session")

    sessions.end_session(cookie)

    bottle.response.set_cookie("session", "")


    bottle.redirect("/login")


@bottle.post('/signup')
def process_signup():

    email = bottle.request.forms.get("email")
    username = bottle.request.forms.get("username")
    password = bottle.request.forms.get("password")
    verify = bottle.request.forms.get("verify")

    # set these up in case we have an error case
    errors=""

    errors = validate_signup(email, password, verify, username)
    if errors == "":

        if not users.add_user(email, password, username):
            # this was a duplicate
            errors= "email already in use. Please choose another"
            return bottle.template("signup", dict(username=username, email=email,
                                    errors=errors))

        session_id = sessions.start_session(email, username)
        print session_id
        bottle.response.set_cookie("session", session_id)
        bottle.redirect("/user/home")
    else:
        print "user did not validate in validate_signup()"
        return bottle.template("signup", dict(username=username, email=email,
                                    errors=errors))



@bottle.get("/welcome")
def present_welcome():
    # check for a cookie, if present, then extract value

    cookie = bottle.request.get_cookie("session")
    username = sessions.get_username(cookie)  # see if user is logged in
    if username is None:
        print "welcome: can't identify user...redirecting to signup"
        bottle.redirect("/signup")

    return bottle.template("welcome", {'username': username})


@bottle.route('/feedback')
def send_feedback():
    return bottle.template('feedback_template', dict(username="", result=""))
@bottle.post('/feedback')
def send_feedback_post():
    name = bottle.request.forms.get("name")
    email = bottle.request.forms.get("email")
    message = bottle.request.forms.get("message")
    error = send_email("maoze365@gmail.com", "来自"+name+"的反馈", email+"\n\n"+message)
    if error=="" :
        return bottle.template('feedback_template', dict(username="", result="Successfully Send. Thank you! :)"))
    else:
        return bottle.template('feedback_template', dict(username="", result="发送有点bug。。sorry。。"))

#######################message####################
@bottle.post('/message/new')
def message_new():

    post = bottle.request.forms

    cookie = bottle.request.get_cookie("session")
    username = sessions.get_username(cookie)  # see if user is logged in
    if username is None:
        bottle.redirect("/login")

    valid_message = {}
    valid_message["from"] = username
    valid_message["message_group_id"]=""
    valid_message["status"] = 0 #this is the initial message, following message is 1. They share same message_group_id
    valid_keys_list = ["to", "body"]
    for key in valid_keys_list:
        valid_message[key] = post[key]

    message_group_id = messages.new_message(message=valid_message)

    print "-----------message send---------------"+message_group_id
    bottle.redirect("/message")
# remove a particular blog post
@bottle.get("/message/remove/<message_group_id>")
def remove_message_group(message_group_id="notfound"):

    cookie = bottle.request.get_cookie("session")

    username = sessions.get_username(cookie)
    message_group_id = cgi.escape(message_group_id)
    if username is None:
        bottle.redirect("/login")

    print "going to remove group_id"+message_group_id
    messages.remove_message_group(message_group_id)
    bottle.redirect("/message")

@bottle.route('/message')
def message():

    cookie = bottle.request.get_cookie("session")
    username = sessions.get_username(cookie)  # see if user is logged in
    if username is None:
        return bottle.template("login", dict(email="", password="", errors="Log in requreid", verify=""))

    message_list = messages.get_messages_by_from_or_to(username)

    return bottle.template('message', dict(message_list=message_list, username=username))

@bottle.get("/message/<message_group_id>")
def message_one(message_group_id="notfound"):

    cookie = bottle.request.get_cookie("session")

    username = sessions.get_username(cookie)
    if username is None:
        return bottle.template("login", dict(email="", password="", errors="Log in requreid", verify=""))

    message_group_id = cgi.escape(message_group_id)

    message_list = messages.get_messages_by_message_group_id(message_group_id)
    if username==message_list[0]['from']:
        reply_to=message_list[0]['to']
    else:
        reply_to=message_list[0]['from']
    return bottle.template('message_one', dict(message_list=message_list, username=username, reply_to=reply_to))


@bottle.post("/message/<message_group_id>")
def message_one(message_group_id="notfound"):

    cookie = bottle.request.get_cookie("session")

    username = sessions.get_username(cookie)
    if username is None:
        return bottle.template("login", dict(email="", password="", errors="Log in requreid", verify=""))

    message_group_id = cgi.escape(message_group_id)

    #process message
    post = bottle.request.forms

    valid_message = {}
    valid_message["from"] = username
    valid_message["message_group_id"] = message_group_id
    valid_message["status"] = 1 #this is the initial message, following message is 1. They share same message_group_id
    valid_keys_list = ["to", "body"]
    for key in valid_keys_list:
        valid_message[key] = post[key]

    messages.new_message(message=valid_message)
    #

    message_list = messages.get_messages_by_message_group_id(message_group_id)
    print message_list
    if username==message_list[0]['from']:
        reply_to=message_list[0]['to']
    else:
        reply_to=message_list[0]['from']
    return bottle.template('message_one', dict(message_list=message_list, username=username, reply_to=reply_to))


#######################message####################
@bottle.post('/appointment/new')
def appointment_new():

    post = bottle.request.forms

    cookie = bottle.request.get_cookie("session")
    username = sessions.get_username(cookie)  # see if user is logged in
    if username is None:
        bottle.redirect("/login")

    valid_appointment = {}
    valid_appointment["from"] = username
    valid_appointment["status"] = 0 #this is the initial message, following message is 1. They share same message_group_id
    valid_keys_list = ["to", "msg", "post_id", "post_title"]
    for key in valid_keys_list:
        valid_appointment[key] = post[key]

    appointments.new_appointment(appointment=valid_appointment)

    print "-----------appointment send---------------"
    bottle.redirect("/")

@bottle.post('/appointment/confirm')
def appointment_confirm():

    post = bottle.request.forms

    cookie = bottle.request.get_cookie("session")
    username = sessions.get_username(cookie)  # see if user is logged in
    if username is None:
        bottle.redirect("/login")
    print post["_id"]
    appointments.confirm_appointment(appointment_id=post["_id"])

    bottle.redirect("/appointment")

@bottle.post('/appointment/cancel')
def appointment_cancel():

    post = bottle.request.forms

    cookie = bottle.request.get_cookie("session")
    username = sessions.get_username(cookie)  # see if user is logged in
    if username is None:
        bottle.redirect("/login")
    appointments.cancel_appointment(appointment_id=post["_id"])

    bottle.redirect("/appointment")

@bottle.route('/appointment')
def appointment():

    cookie = bottle.request.get_cookie("session")
    username = sessions.get_username(cookie)  # see if user is logged in
    if username is None:
        return bottle.template("login", dict(email="", password="", errors="Log in requreid", verify=""))
    user = users.get_user_by_username(username)

    appointment_list = appointments.get_appointments_by_from_or_to(username)

    return bottle.template('appointment', dict(appointment_list=appointment_list, username=username, user=user))


# Helper Functions

#extracts the tag from the tags form element. an experience python programmer could do this in  fewer lines, no doubt
def extract_tags(tags):

    whitespace = re.compile('\s')

    nowhite = whitespace.sub("",tags)
    tags_array = nowhite.split(',')

    # let's clean it up
    cleaned = []
    for tag in tags_array:
        if tag not in cleaned and tag != "":
            cleaned.append(tag)

    return cleaned


# validates that the user information is valid for new signup, return True of False
# and fills in the error string if there is an issue
def validate_signup(email, password, verify, username):

    EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
    errors=""
    if not 4<=len(username)<=20:
        errors += "User Name Length: 4-20 \n"
    if not 4<=len(password)<=20:
        errors  += "Password Length: 4-20 \n"
    if password != verify:
        errors += "<p>password must match</p>"
    if email != "":
        if not EMAIL_RE.match(email):
            errors += "invalid email address<br>"
    return errors
def add_new_keys(post):
    valid_keys_list = ["role", "price", "title", "body", "deliver_time", "payment_method", "deliver_method", "requirements", "phone", "wechat", "category"]
    for key in valid_keys_list:
        if key not in post.keys():
            post[key] = ""

connection_string = "mongodb://cengfan.us"
connection = pymongo.MongoClient(connection_string)
database = connection.blog

posts = blogPostDAO.BlogPostDAO(database)
users = userDAO.UserDAO(database)
sessions = sessionDAO.SessionDAO(database)
messages = messageDAO.MessageDAO(database)
appointments = appointmentDAO.AppointmentDAO(database)
insts = instDAO.InstDAO(database)

bottle.debug(True)
bottle.run(host='0.0.0.0', port=80, reloader=True, server='cherrypy')         # Start the webserver running and wait for requests

