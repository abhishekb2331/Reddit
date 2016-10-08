# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simple replace the two lines below with:
    return auth.wiki()
    """
    name=0
    name_id=0
    name_group=0
    if(auth.is_logged_in()):
	    name=auth.user.username
	    name_id=auth.user.id
	    name_group=db(db.auth_membership.user_id==auth.user.id).select(db.auth_membership.group_id).first()
    redirect(URL('home_page'))
    response.flash=T('Welcome to reddit.com')
    k=db(db.auth_membership.user_id==auth.user.id).select(db.auth_membership.group_id)
    if(k[0].group_id!=2):
	    redirect(URL('user_home'))
    else:
	    redirect(URL('admin_home'))
    return dict(message=T('Hello World'))

def user_home():
	return dict(message='Welcome User')

def admin_home():
	return dict(messafe='Welcome admin')

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    auth.settings.register_onaccept=__add_user_membership
    return dict(form=auth())

def __add_user_membership(form):
	group=db(db.auth_group.role=="user").select().first()
	user_id=form.vars.id
	auth.add_membership(1,user_id)

def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())


def register():
	name=0
	name_id=0
	name_group=0
	if(auth.is_logged_in()):
		name=auth.user.username
		name_id=auth.user.id
		name_group=db(db.auth_membership.user_id==auth.user.id).select(db.auth_membership.group_id).first()
	form=SQLFORM(db.auth_user)
	if(form.accepts(request,session)):
		form.process()
		auth.add_membership(1,form.vars.id)
		redirect(URL('register'))
	elif(form.errors):
		response.flash="Please Fill Form again"
		redirect(URL('register'))
	else:
		response.flash="Please register"
	return dict(form=form,name=name,name_id=name_id,name_group=name_group)


@auth.requires_login()
@auth.requires_membership('admin')
def change_membership():
	name=0
	name_id=0
	name_group=0
	if(auth.is_logged_in()):
		name=auth.user.username
		name_id=auth.user.id
		name_group=db(db.auth_membership.user_id==auth.user.id).select(db.auth_membership.group_id).first()
	
	list_user=db((db.auth_membership.group_id!=2)&(db.auth_user.id==db.auth_membership.user_id)).select(db.auth_user.username)
	list_user1=[]
	for i in list_user:
		list_user1.append(i.username)
	list_user1=set(list_user1)
	form=SQLFORM.factory(
			Field('name',db.auth_user,requires=IS_IN_SET(list_user1),label='Name')
			)
	if(form.accepts(request,session)):
		form.process()
		l=db(db.auth_user.username==form.vars.name).select(db.auth_user.id).first()
		db(db.auth_membership.user_id==l.id).update(group_id=2)
		response.flash='Membership Updated'
		redirect(URL('change_membership'))
#	user_id=request.args(0)
#	db(db.auth_membership.user_id==user_id).update(group_id=2)
	return dict(name=name,name_id=name_id,name_group=name_group,form=form)

@auth.requires_login()
@auth.requires_membership('admin')
def remove_category():
	name=0
	name_id=0
	name_group=0
	if(auth.is_logged_in()):
		name=auth.user.username
		name_id=auth.user.id
		name_group=db(db.auth_membership.user_id==auth.user.id).select(db.auth_membership.group_id).first()
	form=SQLFORM.factory(
			Field('category',db.category_table,requires=IS_IN_DB(db,'category_table.id','category_table.category'),label="Category")
			)
	if(form.accepts(request,session)):
		form.process()
		db(db.category_table.id==form.vars.category).delete()
		redirect(URL('remove_category'))
	elif(form.errors):
		response.flash='Please Fill the Form again'
	else:
		response.flash='Fill Form'
	return dict(form=form,name=name,name_id=name_id,name_group=name_group)

@auth.requires_login()
@auth.requires_membership('admin')
def add_category():
	name=0
	name_id=0
	name_group=0
	if(auth.is_logged_in()):
		name=auth.user.username
		name_id=auth.user.id
		name_group=db(db.auth_membership.user_id==auth.user.id).select(db.auth_membership.group_id).first()
	form=SQLFORM(db.category_table)
	if(form.accepts(request,session)):
		form.process()
		redirect(URL('add_category'))
	elif(form.errors):
		response.flash='Please Fill the Form again'
	else:
		response.flash='Fill Form'
	return dict(form=form,name=name,name_id=name_id,name_group=name_group)
import datetime
@auth.requires_login()
def post_news():
	name=0
	name_id=0
	name_group=0
	if(auth.is_logged_in()):
		name=auth.user.username
		name_id=auth.user.id
		name_group=db(db.auth_membership.user_id==auth.user.id).select(db.auth_membership.group_id).first()
	f=db.post_item.post_date
	f.writable=False
	f.default=datetime.date.today().strftime("%B %d, %Y")
	f.readable=False
	g=db.post_item.post_time
	g.writable=False
	g.default=datetime.datetime.now().strftime("%I:%M%p")
	g.readable=False
	h=db.post_item.user_id
	h.writable=False
	h.default=auth.user.id
	h.readable=False
	i=db.post_item.likes
	i.writable=False
	i.default=100
	i.readable=False
	form=SQLFORM(db.post_item)
	if(form.accepts(request,session)):
		#db.like_post.insert(post_item_id=form.vars.id,likes=100,user_id=auth.user.id)
		form.process()
		redirect(URL('post_news'))
	elif(form.errors):
		response.flash="Cannot perform the action"
		redirect(URL('post_news'))
	return dict(form=form,name=name,name_id=name_id,name_group=name_group)


@auth.requires_login()
def edit_post():
	name=0
	name_id=0
	name_group=0
	if(auth.is_logged_in()):
		name=auth.user.username
		name_id=auth.user.id
		name_group=db(db.auth_membership.user_id==auth.user.id).select(db.auth_membership.group_id).first()
	edit_id=request.args(0)
	k=[]
	k=db(db.auth_membership.user_id==auth.user.id).select(db.auth_membership.group_id).first()
	array=[]
	array=db(db.post_item.id==edit_id).select(db.post_item.category,db.post_item.heading,db.post_item.url,db.post_item.user_id,db.post_item.url2).first()
	print array
	if(auth.user.id != array.user_id and k.group_id!=2):
		return dict(message="You Do not have the permission",name=name,name_id=name_id,name_group=name_group)
	else:
		form=SQLFORM.factory(
				Field('category',db.category_table,requires=IS_IN_DB(db,'category_table.id','category_table.category'),label='Category',default=array.category),
				Field('heading','string',label='Heading',default=array.heading),
				Field('url','string',requires=IS_URL(),label='URL',default=array.url),
				Field('url2','string',requires=IS_URL(),label="Youtube Link",default=array.url2))
		if(form.accepts(request,session)):
			db(db.post_item.id==edit_id).update(category=form.vars.category,heading=form.vars.heading,url=form.vars.url,url2=form.vars.url2)
			form.process()
			redirect(URL('edit_post',args=(edit_id)))
		elif(form.errors):
			response.flash='Error with Form'
		return dict(form=form,message='',name=name,name_id=name_id,name_group=name_group)

@auth.requires_login()
def delete_post():
	name=0
	name_id=0
	name_group=0
	if(auth.is_logged_in()):
		name=auth.user.username
		name_id=auth.user.id
		name_group=db(db.auth_membership.user_id==auth.user.id).select(db.auth_membership.group_id).first()
	edit_id=request.args(0)
	k=[]
	k=db(db.auth_membership.user_id==auth.user.id).select(db.auth_membership.group_id).first()
	array=[]
	array=db(db.post_item.id==edit_id).select(db.post_item.category,db.post_item.heading,db.post_item.url,db.post_item.user_id).first()
	if(auth.user.id != array.user_id and k.group_id!=2):
		return dict(message="You Do not have the permission",name=name,name_id=name_id,name_group=name_group)
	else:
		db(db.post_item.id==edit_id).delete()
	return dict(message='Post Deleted',name=name,name_id=name_id,name_group=name_group)

@auth.requires_login()
def comment_post():
	name=0
	name_id=0
	name_group=0
	if(auth.is_logged_in()):
		name=auth.user.username
		name_id=auth.user.id
		name_group=db(db.auth_membership.user_id==auth.user.id).select(db.auth_membership.group_id).first()
	post_id=request.args(0)
	f=db.comments.post_item_id
	f.writable=False
	f.default=post_id
	f.readable=False
	g=db.comments.user_id
	g.writable=False
	g.default=auth.user.id
	g.readable=False
	h=db.comments.comments_date
	h.writable=False
	h.default=datetime.date.today().strftime("%B %d, %Y")
	h.readable=False
	i=db.comments.comments_time
	i.writable=False
	i.default=datetime.datetime.now().strftime("%I:%M%p")
	i.readable=False
	j=db.comments.likes
	j.writable=False
	j.default=100
	j.readable=False
	form=SQLFORM(db.comments)
	if(form.accepts(request,session)):
		form.process()
		redirect(URL('comment_post'))
	elif(form.errors):
		response.flash='Cannot be posted'
	return dict(form=form,name=name,name_id=name_id,name_group=name_group)

@auth.requires_login()
def edit_comments():
	name=0
	name_id=0
	name_group=0
	if(auth.is_logged_in()):
		name=auth.user.username
		name_id=auth.user.id
		name_group=db(db.auth_membership.user_id==auth.user.id).select(db.auth_membership.group_id).first()
	edit_id=request.args(0)
	k=[]
	k=db(db.auth_membership.user_id==auth.user.id).select(db.auth_membership.group_id).first()
	array=[]
	array=db(db.comments.post_item_id==edit_id).select(db.comments.comments,db.comments.user_id).first()
	if(auth.user.id !=array.user_id and k.group_id!=2):
		return dict(message='You donot have Permission',name=name,name_id=name_id,name_group=name_group)
	else:
		form=SQLFORM.factory(
				Field('comments','text',default=array.comments)
				)
		if(form.accepts(request,session)):
			db(db.comments.post_item_id==edit_id).update(comments=form.vars.comments)
			form.process()
			redirect(URL(link))
		elif(form.errors):
			response.flash='Error with Form'
		return dict(form=form,message='',name=name,name_id=name_id,name_group=name_group)

@auth.requires_login()
def delete_comments():
	name=0
	name_id=0
	name_group=0
	if(auth.is_logged_in()):
		name=auth.user.username
		name_id=auth.user.id
		name_group=db(db.auth_membership.user_id==auth.user.id).select(db.auth_membership.group_id).first()
	edit_id=request.args(0)
	link=request.args(1)
	k=[]
	k=db(db.auth_membership.user_id==auth.user.id).select(db.auth_membership.group_id).first()
	array=[]
	array=db(db.comments.post_item_id==edit_id).select(db.comments.user_id).first()
	if(auth.user.id !=array.user_id and k.group_id!=2):
		return dict(message="You Do not have the permission",name=name,name_id=name_id,name_group=name_group)
	else:
		db(db.comments.post_item_id==edit_id).delete()
	return dict(message='Comment Deleted',name=name,name_id=name_id,name_group=name_group)

@auth.requires_login()
def like_post():
	name=0
	name_id=0
	name_group=0
	if(auth.is_logged_in()):
		name=auth.user.username
		name_id=auth.user.id
		name_group=db(db.auth_membership.user_id==auth.user.id).select(db.auth_membership.group_id).first()
	like_id=request.args(0)
	print like_id
	array=[]
	array=db((db.like_post.post_item_id==like_id)&(db.like_post.user_id==auth.user.id)).select(db.like_post.likes).first()
	print array,'1'
	if(array==None):
		db.like_post.insert(user_id=auth.user.id,post_item_id=like_id,likes=5)
		k=[]
		k=db(db.post_item.id==like_id).select(db.post_item.likes).first()
		k.likes=k.likes or 100
		k.likes+=5
		db(db.post_item.id==like_id).update(likes=k.likes)
	elif(array.likes==-3):
		#db((db.like_post.post_item_id==like_id)&(db.like_post.user_id==auth.user.id)).delete()
		db((db.like_post.post_item_id==like_id)&(db.like_post.user_id==auth.user.id)).update(likes=5)
		k=[]
		k=db(db.post_item.id==like_id).select(db.post_item.likes).first()
		k.likes=k.likes or 100
		k.likes+=8
		db(db.post_item.id==like_id).update(likes=k.likes)
	elif(array.likes==5):
		db((db.like_post.post_item_id==like_id)&(db.like_post.user_id==auth.user.id)).delete()
		k=[]
		k=db(db.post_item.id==like_id).select(db.post_item.likes).first()
		k.likes=k.likes or 100
		k.likes-=5
		db(db.post_item.id==like_id).update(likes=k.likes)
	return dict(message='liked',name=name,name_id=name_id,name_group=name_group)



@auth.requires_login()
def dislike_post():
	name=0
	name_id=0
	name_group=0
	if(auth.is_logged_in()):
		name=auth.user.username
		name_id=auth.user.id
		name_group=db(db.auth_membership.user_id==auth.user.id).select(db.auth_membership.group_id).first()
	dislike_id=request.args(0)
	array=[]
	array=db((db.like_post.post_item_id==dislike_id)&(db.like_post.user_id==auth.user.id)).select(db.like_post.likes).first()
	print array,'2'
	if(array==None):
		db.like_post.insert(user_id=auth.user.id,post_item_id=dislike_id,likes=-3)
		k=[]
		k=db(db.post_item.id==dislike_id).select(db.post_item.likes).first()
		k.likes-=3
		db(db.post_item.id==dislike_id).update(likes=k.likes)
	elif(array.likes==5):
		#db((db.like_post.post_item_id==dislike_id)&(db.like_post.user_id==auth.user.id)).delete()
		k=[]
		k=db(db.post_item.id==dislike_id).select(db.post_item.likes).first()
		k.likes=k.likes or 100
		k.likes-=8
		db(db.post_item.id==dislike_id).update(likes=k.likes)
		db((db.like_post.post_item_id==dislike_id)&(db.like_post.user_id==auth.user.id)).update(likes=-3)
	elif(array.likes==-3):
		db((db.like_post.post_item_id==dislike_id)&(db.like_post.user_id==auth.user.id)).delete()
		k=[]
		k=db(db.post_item.id==dislike_id).select(db.post_item.likes).first()
		k.likes=k.likes or 100
		k.likes+=3
		db(db.post_item.id==dislike_id).update(likes=k.likes)

	return dict(message='disliked',name=name,name_id=name_id,name_group=name_group)

@auth.requires_login()
def like_comments():
	name=0
	name_id=0
	name_group=0
	if(auth.is_logged_in()):
		name=auth.user.username
		name_id=auth.user.id
		name_group=db(db.auth_membership.user_id==auth.user.id).select(db.auth_membership.group_id).first()
	like_id=request.args(0)
	array=[]
	array=db((db.like_comment.comments_id==like_id)&(db.like_comment.user_id==auth.user.id)).select(db.like_comment.likes).first()
	if(array==None):
		db.like_comment.insert(user_id=auth.user.id,comments_id=like_id,likes=5)
		k=[]
		k=db(db.comments.id==like_id).select(db.comments.likes).first()
		k.likes=k.likes or 100
		k.likes+=5
		db(db.comments.id==like_id).update(likes=k.likes)
	elif(array.likes==-3):
		#db((db.like_comment.comments_id==like_id)&(db.like_comment.user_id==auth.user.id)).delete()
		k=[]
		k=db(db.comments.id==like_id).select(db.comments.likes).first()
		k.likes=k.likes or 100
		k.likes+=8
		db(db.comments.id==like_id).update(likes=k.likes)
		db((db.like_comment.comments_id==like_id)&(db.like_comment.user_id==auth.user.id)).update(likes=5)
	elif(array.likes==5):
		db((db.like_comment.comments_id==like_id)&(db.like_comment.user_id==auth.user.id)).delete()
		k=[]
		k=db(db.comments.id==like_id).select(db.comments.likes).first()
		k.likes=k.likes or 100
		k.likes-=5
		db(db.comments.id==like_id).update(likes=k.likes)

	return dict(message='liked',name=name,name_id=name_id,name_group=name_group)


@auth.requires_login()
def dislike_comments():
	name=0
	name_id=0
	name_group=0
	if(auth.is_logged_in()):
		name=auth.user.username
		name_id=auth.user.id
		name_group=db(db.auth_membership.user_id==auth.user.id).select(db.auth_membership.group_id).first()
	dislike_id=request.args(0)
	array=[]
	array=db((db.like_comment.comments_id==dislike_id)&(db.like_comment.user_id==auth.user.id)).select(db.like_comment.likes).first()
	if(array==None):
		db.like_comment.insert(user_id=auth.user.id,comments_id=dislike_id,likes=-3)
		k=[]
		k=db(db.comments.id==dislike_id).select(db.comments.likes).first()
		k.likes=k.likes or none
		k.likes-=3
		db(db.comments.id==dislike_id).update(likes=k.likes)
	elif(array.likes==5):
		#db((db.like_comment.comments_id==dislike_id)&(db.like_comment.user_id==auth.user.id)).delete()
		k=[]
		k=db(db.comments.id==dislike_id).select(db.comments.likes).first()
		k.likes=k.likes or 100
		k.likes-=8
		db(db.comments.id==dislike_id).update(likes=k.likes)
		db((db.like_comment.comments_id==dislike_id)&(db.like_comment.user_id==auth.user.id)).update(likes=-3)
	elif(array.likes==-3):
		db((db.like_comment.comments_id==dislike_id)&(db.like_comment.user_id==auth.user.id)).delete()
		k=[]
		k=db(db.comments.id==dislike_id).select(db.comments.likes).first()
		k.likes=k.likes or 100
		k.likes+=3
		db(db.comments.id==dislike_id).update(likes=k.likes)
	return dict(message='liked',name=name,name_id=name_id,name_group=name_group)



@auth.requires_login()
@auth.requires_membership('admin')
def remove_user():
	name=0
	name_id=0
	name_group=0
	if(auth.is_logged_in()):
		name=auth.user.username
		name_id=auth.user.id
		name_group=db(db.auth_membership.user_id==auth.user.id).select(db.auth_membership.group_id).first()
	list_user=db((db.auth_membership.group_id!=2)&(db.auth_user.id==db.auth_membership.user_id)).select(db.auth_user.username)
	list_user1=[]
	for i in list_user:
		list_user1.append(i.username)
	list_user1=set(list_user1)
	print list_user
	#userid=request.args(0)
	form=SQLFORM.factory(
			Field('name',db.auth_user,requires=IS_IN_SET(list_user1),label='Name')
			)
	if(form.accepts(request,session)):
		form.process()
		l=db(db.auth_user.username==form.vars.name).select(db.auth_user.id).first()
		db(db.auth_user.id==l.id).delete()
		response.flash='User Removed'
		redirect(URL('remove_user'))
	return dict(message='User Deleted',name=name,name_id=name_id,name_group=name_group,form=form)

def home_page():
	array=[]
	array=db((db.post_item.id>0)&(db.post_item.user_id==db.auth_user.id)&(db.post_item.category==db.category_table.id)&(db.auth_user.id==db.post_item.user_id)).select(db.auth_user.username,db.auth_user.image,db.category_table.category,db.post_item.ALL,orderby=~(db.post_item.likes))
	comment_full={}
	for i in range(0,len(array),1) :
		comment_full[array[i]['post_item'].id]=(db((db.comments.post_item_id==array[i]['post_item'].id)&(db.comments.user_id==db.auth_user.id)).select(db.auth_user.username,db.auth_user.image,db.comments.ALL,orderby=~(db.comments.likes)))
	categories=[]
	categories=db(db.category_table.id>0).select(db.category_table.ALL)
	likes_list=[]
	for i in range(0,len(array),1):
		likes_list.append(db(db.like_post.post_item_id==array[i]['post_item'].id).select(db.like_post.likes,orderby=~(db.like_post.likes)))
	liking=[]
	for i in range(0,len(array),1):
		index=len(likes_list[i])
		j=0
		for j in range(0,index,1):
			if(likes_list[i][j].likes==-3):
				break
		#if -3 in likes_list[i].list:
			#index=likes_list[i].index(-3)
		if(j==0 and index!=0 and likes_list[i][0].likes==5):
			j=1
		j=j or 0
		liking.append(j)
	len_array=len(array)
	name=0
	name_id=0
	name_group=0
	if(auth.is_logged_in()):
		name=auth.user.username
		name_id=auth.user.id
		name_group=db(db.auth_membership.user_id==auth.user.id).select(db.auth_membership.group_id).first()
	#for(i in )
	return dict(array=array,categories=categories,comment_full=comment_full,name=name,name_id=name_id,name_group=name_group,liking=liking)

def show_categories():
	name=0
	name_id=0
	name_group=0
	if(auth.is_logged_in()):
		name=auth.user.username
		name_id=auth.user.id
		name_group=db(db.auth_membership.user_id==auth.user.id).select(db.auth_membership.group_id).first()
	category_id=request.args(0)
	page=int(request.args(1))
	array=[]
	array=db((db.post_item.category==category_id)&(db.category_table.id==category_id)&(db.auth_user.id==db.post_item.user_id)).select(db.auth_user.username,db.auth_user.image,db.category_table.ALL,db.post_item.ALL,orderby=~(db.post_item.likes))
	comment_full={}
	for i in range(0,len(array),1) :
		comment_full[array[i]['post_item'].id]=(db((db.comments.post_item_id==array[i]['post_item'].id)&(db.comments.user_id==db.auth_user.id)).select(db.auth_user.username,db.auth_user.image,db.comments.ALL))
	arg1=category_id
	arg2=page
	likes_list=[]
	for i in range(0,len(array),1):
		likes_list.append(db(db.like_post.post_item_id==array[i]['post_item'].id).select(db.like_post.likes,orderby=~(db.like_post.likes)))
	liking=[]
	for i in range(0,len(array),1):
		index=len(likes_list[i])
		j=0
		for j in range(0,index,1):
			if(likes_list[i][j].likes==-3):
				break
		#if -3 in likes_list[i].list:
			#index=likes_list[i].index(-3)
		if(j==0 and index!=0 and likes_list[i][0].likes==5):
			j=1
		j=j or 0
		liking.append(j)
	return dict(array=array,page=page,category_id=category_id,comment_full=comment_full,name=name,name_id=name_id,name_group=name_group,liking=liking)


def show_comment():
	name=0
	name_id=0
	name_group=0
	if(auth.is_logged_in()):
		name=auth.user.username
		name_id=auth.user.id
		name_group=db(db.auth_membership.user_id==auth.user.id).select(db.auth_membership.group_id).first()
	post_id=request.args(0)
	array=[]
	array=db((db.post_item.id==post_id)&(db.post_item.user_id==db.auth_user.id)&(db.post_item.category==db.category_table.id)).select(db.post_item.ALL,db.auth_user.ALL,db.category_table.ALL).first()
	comment_full=[]
	comment_full=db((db.comments.post_item_id==post_id)&(db.comments.user_id==db.auth_user.id)).select(db.auth_user.ALL,db.comments.ALL,orderby=~(db.comments.likes))
	likes_list=[]
	for i in range(0,1,1):
		likes_list.append(db(db.like_post.post_item_id==array['post_item'].id).select(db.like_post.likes,orderby=~(db.like_post.likes)))
	liking=[]
	for i in range(0,1,1):
		index=len(likes_list[i])
		j=0
		for j in range(0,index,1):
			if(likes_list[i][j].likes==-3):
				break
		#if -3 in likes_list[i].list:
			#index=likes_list[i].index(-3)
		if(j==0 and index!=0 and likes_list[i][0].likes==5):
			j=1
		j=j or 0
		liking.append(j)
	return dict(comment_full=comment_full,array=array,name=name,name_id=name_id,name_group=name_group,liking=liking)

def search_post():
	name=0
	name_id=0
	name_group=0
	if(auth.is_logged_in()):
		name=auth.user.username
		name_id=auth.user.id
		name_group=db(db.auth_membership.user_id==auth.user.id).select(db.auth_membership.group_id).first()
	form=SQLFORM.factory(
			Field('typeof',requires=IS_IN_SET(['user','category','url','heading'])),
			Field('search','string')
			)
	if(form.accepts(request,session)):
		form.process()
		print form.vars.search,form.vars.typeof
		redirect(URL('list_post',args=(form.vars.search,form.vars.typeof)))
	elif(form.errors):
		response.flash=T('Form has Errors')
	return dict(form=form,name=name,name_id=name_id,name_group=name_group)

def list_post():
	name=0
	name_id=0
	name_group=0
	if(auth.is_logged_in()):
		name=auth.user.username
		name_id=auth.user.id
		name_group=db(db.auth_membership.user_id==auth.user.id).select(db.auth_membership.group_id).first()
	search=request.args(0)
	typeof=request.args(1)
	array=[]
	if(typeof=='user'):
		array=db((db.auth_user.username==search)&(db.post_item.user_id==db.auth_user.id)&(db.post_item.category==db.category_table.id)).select(db.auth_user.ALL,db.post_item.ALL,db.category_table.ALL,orderby=~(db.post_item.likes))
	elif(typeof=='category'):
		array=db((db.category_table.category==search)&(db.category_table.id==db.post_item.category)&(db.post_item.user_id==db.auth_user.id)).select(db.auth_user.ALL,db.post_item.ALL,db.category_table.ALL,orderby=~(db.post_item.likes))
	elif(typeof=='url'):
		array=db((db.post_item.url==search)&(db.post_item.category_table==db.category.id)&(db.post_item.user_id==db.auth_user.id)).select(db.auth_user.ALL,db.post_item.ALL,db.category_table.ALL,orderby=~(db.post_item.likes))
	elif(typeof=='heading'):
		array=db((db.post_item.heading==search)&(db.post_item.category_table==db.category.id)&(db.post_item.user_id==db.auth_user.id)).select(db.auth_user.ALL,db.post_item.ALL,db.category_table.id,orderby=~(db.post_item.likes))
	comment_full={}
	for i in range(0,len(array),1) :
		comment_full[array[i]['post_item'].id]=(db((db.comments.post_item_id==array[i]['post_item'].id)&(db.comments.user_id==db.auth_user.id)).select(db.auth_user.username,db.auth_user.image,db.comments.ALL,orderby=~(db.comments.likes)))
	return dict(array=array,comment_full=comment_full,name=name,name_id=name_id,name_group=name_group)

@auth.requires_login()
def user_profile():
	name=0
	name_id=0
	name_group=0
	if(auth.is_logged_in()):
		name=auth.user.username
		name_id=auth.user.id
		name_group=db(db.auth_membership.user_id==auth.user.id).select(db.auth_membership.group_id).first()
	array=[]
	array=db((db.post_item.user_id==auth.user.id)&(db.post_item.category==db.category_table.id)&(db.post_item.user_id==db.auth_user.id)).select(db.post_item.ALL,db.auth_user.ALL,db.category_table.ALL,orderby=~(db.post_item.likes))
	comment_full={}
	for i in range(0,len(array),1) :
		comment_full[array[i]['post_item'].id]=(db((db.comments.post_item_id==array[i]['post_item'].id)&(db.comments.user_id==db.auth_user.id)).select(db.auth_user.username,db.auth_user.image,db.comments.ALL,orderby=~(db.comments.likes)))
	categories=[]
	categories=db(db.category_table.id>0).select(db.category_table.ALL)
	likes_list=[]
	for i in range(0,len(array),1):
		likes_list.append(db(db.like_post.post_item_id==array[i]['post_item'].id).select(db.like_post.likes,orderby=~(db.like_post.likes)))
	liking=[]
	for i in range(0,len(array),1):
		index=len(likes_list[i])
		j=0
		for j in range(0,index,1):
			if(likes_list[i][j].likes==-3):
				break
		#if -3 in likes_list[i].list:
			#index=likes_list[i].index(-3)
		if(j==0 and index!=0 and likes_list[i][0].likes==5):
			j=1
		j=j or 0
		liking.append(j)
	return dict(array=array,comment_full=comment_full,categories=categories,name=name,name_id=name_id,name_group=name_group,liking=liking)

def show_likes():
	name=0
	name_id=0
	name_group=0
	if(auth.is_logged_in()):
		name=auth.user.username
		name_id=auth.user.id
		name_group=db(db.auth_membership.user_id==auth.user.id).select(db.auth_membership.group_id).first()
	like_id=request.args(0)
	array=[]
	array=db((db.post_item.id==like_id)&(db.post_item.user_id==db.auth_user.id)&(db.post_item.category==db.category_table.id)).select(db.post_item.ALL,db.auth_user.ALL,db.category_table.ALL).first()
	comment_full=[]
	comment_full=db((db.like_post.post_item_id==like_id)&(db.like_post.user_id==db.auth_user.id)).select(db.auth_user.image,db.auth_user.username,db.like_post.ALL,orderby=(db.like_post.likes))
	likes_list=[]
	for i in range(0,1,1):
		likes_list.append(db(db.like_post.post_item_id==int(array['post_item'].id)).select(db.like_post.likes,orderby=~(db.like_post.likes)))
	liking=[]
	for i in range(0,1,1):
		index=len(likes_list[i])
		j=0
		print index,likes_list[i]
		for j in range(0,index,1):
			if(likes_list[i][j].likes==-3):
				break
		#if -3 in likes_list[i].list:
			#index=likes_list[i].index(-3)
		if(j==0 and index!=0 and likes_list[i][0].likes==5):
			j=1
		j=j or 0
		liking.append(j)
	print liking
	return dict(array=array,comment_full=comment_full,name=name,name_id=name_id,name_group=name_group,liking=liking)

@auth.requires_login()
@auth.requires_membership('admin')
def admin_profile():
	name=0
	name_id=0
	name_group=0
	if(auth.is_logged_in()):
		name=auth.user.username
		name_id=auth.user.id
		name_group=db(db.auth_membership.user_id==auth.user.id).select(db.auth_membership.group_id).first()
	array=[]
	array=db((db.post_item.id>0)&(db.post_item.user_id==db.auth_user.id)&(db.post_item.category==db.category_table.id)&(db.auth_user.id==db.post_item.user_id)).select(db.auth_user.username,db.auth_user.image,db.category_table.category,db.post_item.ALL,orderby=(db.post_item.post_date|db.post_item.post_time))
	comment_full={}
	for i in range(0,len(array),1) :
		comment_full[array[i]['post_item'].id]=(db((db.comments.post_item_id==array[i]['post_item'].id)&(db.comments.user_id==db.auth_user.id)).select(db.auth_user.username,db.auth_user.image,db.comments.ALL,orderby=(db.comments.comments_date|db.comments.comments_time)))
	categories=[]
	categories=db(db.category_table.id>0).select(db.category_table.ALL)
	likes_list=[]
	for i in range(0,len(array),1):
		likes_list.append(db(db.like_post.post_item_id==array[i]['post_item'].id).select(db.like_post.likes,orderby=~(db.like_post.likes)))
	liking=[]
	for i in range(0,len(array),1):
		index=len(likes_list[i])
		j=0
		for j in range(0,index,1):
			if(likes_list[i][j].likes==-3):
				break
		#if -3 in likes_list[i].list:
		if(j==0 and index!=0 and likes_list[i][0].likes==5):
			j=1
			#index=likes_list[i].index(-3)
		j=j or 0
		liking.append(j)
	len_array=len(array)
	#for(i in )
	return dict(array=array,categories=categories,comment_full=comment_full,name=name,name_id=name_id,name_group=name_group,liking=liking)

def login():
	name=0
	name_id=0
	name_group=0
	if(auth.is_logged_in()):
		name=auth.user.username
		name_id=auth.user.id
		name_group=db(db.auth_membership.user_id==auth.user.id).select(db.auth_membership.group_id).first()
	auth.settings.formstyle = 'bootstrap'
	form = auth.login()
	return dict(form=form,name=name,name_id=name_id,name_group=name_group)

def show_categories_user():
	name=0
	name_id=0
	name_group=0
	if(auth.is_logged_in()):
		name=auth.user.username
		name_id=auth.user.id
		name_group=db(db.auth_membership.user_id==auth.user.id).select(db.auth_membership.group_id).first()
	category_id=request.args(0)
	page=int(request.args(1))
	user_id=request.args(2)
	array=[]
	array=db((db.post_item.category==category_id)&(db.category_table.id==category_id)&(db.auth_user.id==user_id)&(db.post_item.user_id==user_id)).select(db.auth_user.username,db.auth_user.image,db.category_table.ALL,db.post_item.ALL,orderby=~(db.post_item.likes))
	print array
	comment_full={}
	for i in range(0,len(array),1) :
		comment_full[array[i]['post_item'].id]=(db((db.comments.post_item_id==array[i]['post_item'].id)&(db.comments.user_id==db.auth_user.id)).select(db.auth_user.username,db.auth_user.image,db.comments.ALL))
	return dict(array=array,page=page,category_id=category_id,comment_full=comment_full,user_id=user_id,name=name,name_id=name_id,name_group=name_group)

def play_video():
	name=0
	name_id=0
	name_group=0
	if(auth.is_logged_in()):
		name=auth.user.username
		name_id=auth.user.id
		name_group=db(db.auth_membership.user_id==auth.user.id).select(db.auth_membership.group_id).first()
	post_id=request.args(0)
	array=[]
	array=db((db.post_item.id==post_id)&(db.post_item.user_id==db.auth_user.id)&(db.post_item.category==db.category_table.id)).select(db.post_item.ALL,db.auth_user.ALL,db.category_table.ALL).first()
	likes_list=[]
	for i in range(0,1,1):
		likes_list.append(db(db.like_post.post_item_id==array['post_item'].id).select(db.like_post.likes,orderby=~(db.like_post.likes)))
	liking=[]
	for i in range(0,1,1):
		index=len(likes_list[i])
		j=0
		for j in range(0,index,1):
			if(likes_list[i][j].likes==-3):
				break
		#if -3 in likes_list[i].list:
			#index=likes_list[i].index(-3)
		if(j==0 and index!=0 and likes_list[i][0].likes==5):
			j=1
		j=j or 0
		liking.append(j)
	return dict(array=array,name=name,name_id=name_id,name_group=name_group,liking=liking)
