import webapp2
import jinja2
import requests
import os
import sys
import time
import logging
import urllib2
import json
import re
from operator import itemgetter
from datetime import datetime
from google.appengine.ext import db
from webapp2_extras import sessions
from google.appengine.api import mail


#UTC time of contest to be started in seconds
time_exam_started = 4*3600+1800
contest_duration = 2 #in hours

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)



def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)



#def get_mesage_html():
#	jinja2 = webapp_extras_jinja2.get_jinja2()
#	return jinja2.render_template('/templates/go-welcome.html')



class BaseHandler(webapp2.RequestHandler):
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)
 
        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

 
    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()

    def render(self, template, **kw):
        self.response.out.write(render_str(template, **kw))






USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return not email or EMAIL_RE.match(email)






class UserInfo(db.Model):
	fullname = db.StringProperty()
	username = db.StringProperty()
	email = db.StringProperty()
	password = db.StringProperty()
	A = db.StringProperty()
	B = db.StringProperty()
	C = db.StringProperty()
	D = db.StringProperty()
	E = db.StringProperty()
	F = db.StringProperty()
	ADD = db.StringProperty()
	EON = db.StringProperty()
	STR = db.StringProperty()
	DBY = db.StringProperty()
	RUPQ = db.StringProperty()
	ns_user = db.IntegerProperty()
	ac_time = db.IntegerProperty()
	tagline = db.StringProperty()
	aboutme = db.StringProperty()
	portfolio = db.StringProperty()
	is_confirmed = db.BooleanProperty()
	dp_link = db.StringProperty()
	cp_link = db.StringProperty()


class PaidEmails(db.Model):
	emailid = db.StringProperty()




class About(BaseHandler):
	def get(self):
		self.render('about.html')









class Main(BaseHandler):
	def get(self):
		username_s = self.session.get('username')
		if username_s:
			self.redirect('/user/'+str(username_s))
			return
		self.render('index-front.html')


class Signup(BaseHandler):
    def get(self):
    	username_s = self.session.get('username')
    	username_session = str(username_s)
    	if username_s:
    		self.redirect('https://dubhacking.appspot.com/user/'+username_session)
        self.render('index.html')

    def post(self):
    	have_error = False
    	fullname = self.request.get('fullname')
    	username = self.request.get('username')
    	email = self.request.get('email')
    	password = self.request.get('password')
    	cpassword = self.request.get('cpassword')
    	params = dict(username = username,email = email,fullname = fullname,password = password)

    	q = db.GqlQuery("SELECT * FROM UserInfo WHERE username= :u",u=str(username)).fetch(limit=2)
    	qe = db.GqlQuery("SELECT * FROM UserInfo WHERE email= :e",e=str(email)).fetch(limit=2)
    	if len(qe)>0:
    		params['email_already_taken'] = "The email id has already been registered!"
    		have_error=True
    	if len(q)>0:
    		params['username_already_present'] = "This username has already been taken. Choose another!"
    		have_error=True


    	sde = db.GqlQuery("SELECT * FROM PaidEmails WHERE emailid= :e",e=str(email)).fetch(limit=2)
    	if len(sde)==0:
    		params['not_paid'] = "I guess you didn't register yourself for the contest."
    		have_error=True

    	if not valid_username(username):
    		params['error_username'] = "That's not a valid username."
    		have_error = True
    	if not valid_password(password):
    		params['error_password'] = "That wasn't a valid password."
    		have_error = True

    	elif password != cpassword:
    		params['error_verify'] = "Your passwords didn't match."
    		have_error = True
    	
    	if not valid_email(email):
    		params['error_email'] = "That's not a valid email."
    		have_error = True

    	confirming_link = 'https://dubhacking.appspot.com/confirming/'+str(username)+'/'+'CONFIRM_BIG_INTEGER'
    	cparam = dict(confirming_link=confirming_link)

    	if have_error:
    		self.render('index.html', **params)
    	else:
    		user_instance = UserInfo(key_name=username,fullname=fullname,username=username,cp_link='https://img1.etsystatic.com/031/1/7380103/il_340x270.647655413_bh43.jpg',dp_link='http://oi61.tinypic.com/2cfw86c.jpg',email=email,password=password,is_confirmed=False,A='NA',B='NA',C='NA',D='NA',E='NA',F='NA',ADD='NA',STR='NA',EON='NA',DBY='NA',RUPQ='NA',ns_user=0,ac_time=0,tagline='The Algorithmist',aboutme="I'm an undergraduate Computer Science student who loves to code. I like solving algorithmic challenges and making apps that impacts the society",portfolio='')
    		user_instance.put()
    		message = mail.EmailMessage(sender="Wasim Thabraze <waseem.tabraze@gmail.com>",
    			                        subject="Your account has been approved!")
    		#message.to = "Waim Thabraze <waseem.tabraze@gmail.com.com>"
    		message.to = str(fullname)+" "+'<'+str(email)+'>'
    		message.body = """
    		Dear User,
    		Thank you for creating an account on Dubhacking!
    		"""
    		message.html = render_str('emailtemplate.html',**cparam)
    		message.send()

    		self.redirect('/confirm_email')



class Confirm_email(BaseHandler):
	def get(self):
		username_s = self.session.get('username')
		if username_s:
			self.redirect('/user/'+str(username_s))
		else:
			#self.response.out.write("Thank you for signing up! Now all you need to do is to confirm your email. A confirmation email with an Activation link has been sent to you!!")
			self.render('confirm_email.html')

class Confirming(BaseHandler):
	def get(self):
		current_url = self.request.url
		p = current_url.split('/')
		un = p[4]
		qq = db.GqlQuery("SELECT * FROM UserInfo WHERE username= :u",u=str(un)).fetch(limit=2)
		if qq>0:
			q  = db.GqlQuery("SELECT * FROM UserInfo WHERE username= :u",u=str(un)).get()
			if q.is_confirmed == False:
				setattr(q,'is_confirmed',True)
				q.put()
				self.redirect('/login')
			else:
				self.redirect('/user/'+str(un))
		else:
			self.redirect('/signup')









class Login(BaseHandler):
    def get(self):
    	is_usersession_present = self.session.get('username')
    	if is_usersession_present:
    		self.redirect('/user/'+str(is_usersession_present))
    		return
    	username_s = self.session.get('username')
    	username_session = str(username_s)
    	if username_s:
    		self.redirect('https://dubhacking.appspot.com/user/'+username_session)
        #template_values={}
        #template = jinja_env.get_template('login.html')
        #self.response.out.write(template.render(template_values))
        self.render('login.html')

    def post(self):
    	is_usersession_present = self.session.get('username')
    	if is_usersession_present:
    		self.redirect('/user/'+str(is_usersession_present))
    		return
    	have_error=False
    	params = {}
    	login_username = self.request.get('login_username')
    	login_password = self.request.get('login_password')
    	if str(login_username)=="" or str(login_password)=="":
    		params['login_empty_error'] = "Enter credentials"
    		have_error = True

    	if login_username and login_password:
    		q = db.GqlQuery("SELECT * FROM UserInfo WHERE username= :u",u=str(login_username)).fetch(limit=2)
    		if len(q)==0:
    			params['username_not_present'] = "This username is not available on our database."
    			have_error = True
    		else:
    			userdata = db.GqlQuery("SELECT * FROM UserInfo WHERE username= :u",u=str(login_username)).get()
    			if str(login_password)==str(userdata.password) and userdata.is_confirmed==True:
    				self.session['username'] = str(login_username)
    				self.redirect('/user/'+str(login_username))
    			elif userdata.is_confirmed==False:
    				params['not_confirmed'] = "Confirm your email id before you login!"
    				have_error=True
    			else:
    				params['error_verify'] = "Incorrect password"
    				have_error = True
    	if have_error:
    		self.render('login.html',**params)




def vfg(v):
	if v=='AC':
		return 99
	elif v=='WA':
		return 33
	elif v=='TLE':
		return 66
	else:
		return 0



			



class Userprofile(BaseHandler):
	def get(self):
		username_s = self.session.get('username')
		if not username_s:
			self.redirect('/')
			return
		username_session = str(username_s)
		current_url = self.request.url
		un = current_url.split('/')[4]
		username = str(un)
		param = {}
		q = db.GqlQuery("SELECT * FROM UserInfo WHERE username= :u",u=username).fetch(limit=2)
		if len(q)==0:
			self.response.out.write("The person with the username "+ username +" is not available in our database. If he/she is taking part, contact Wasim soon!")
			return
        
		#if username_session != username:
		#	self.redirect('/user/'+username_session)
		#	return #May be a chance of an error!
		fd = db.GqlQuery("SELECT * FROM UserInfo WHERE username= :u",u=username_session).get()
		fn = db.GqlQuery("SELECT * FROM UserInfo WHERE username= :u",u=username).get()

		fullname_nav = str(fd.fullname)
		fullname = str(fn.fullname)
		tagline = str(fn.tagline)
		aboutme = str(fn.aboutme)
		dp_link=str(fn.dp_link)
		cp_link = str(fn.cp_link)
		nsu = int(fn.ns_user)
		mu = db.GqlQuery("SELECT * FROM UserInfo WHERE ns_user= :n",n=nsu).fetch(limit=5)
		vA = vfg(str(fn.A))
		vB = vfg(str(fn.B))
		vC = vfg(str(fn.C))
		vD = vfg(str(fn.D))
		vE = vfg(str(fn.E))
		vF = vfg(str(fn.F))
		vADD = vfg(str(fn.ADD))
		vSTR = vfg(str(fn.STR))
		vEON = vfg(str(fn.EON))
		vDBY = vfg(str(fn.DBY))
		vRUPQ = vfg(str(fn.RUPQ))
		if len(mu)==1:
			no_one_matches = "None of them match with your skills. You are unique!"
			self.render('profilepage.html',username=username,no_one_matches=no_one_matches,fullname_nav=fullname_nav,cp_link=cp_link,dp_link=dp_link,username_session=username_session,fullname=fullname,tagline=tagline,aboutme=aboutme,vA=vA,vB=vB,vC=vC,vD=vD,vE=vE,vF=vF,vADD=vADD,vSTR=vSTR,vEON=vEON,vDBY=vDBY,vRUPQ=vRUPQ)
		else:
			self.render('profilepage.html',mu=mu,username=username,username_session=username_session,cp_link=cp_link,dp_link=dp_link,fullname_nav=fullname_nav,fullname=fullname,tagline=tagline,aboutme=aboutme,vA=vA,vB=vB,vC=vC,vD=vD,vE=vE,vF=vF,vADD=vADD,vSTR=vSTR,vEON=vEON,vDBY=vDBY,vRUPQ=vRUPQ)






















class Scoreboard(BaseHandler):
	def get(self):
		privacy='user'
		username_s = self.session.get('username')
		username_session = str(username_s)
		if not username_s:
			privacy='public'
		else:
			fn = db.GqlQuery("SELECT * FROM UserInfo WHERE username= :u",u=username_session).get()
			fullname = fn.fullname
		sb = []
		c = db.GqlQuery("SELECT * FROM UserInfo")
		for entity in c:
			sb.append({'username':str(entity.username),'nops':int(entity.ns_user),'act':int(entity.ac_time)})
		newlist = sorted(sb, key=lambda k: (-k['nops'], k['act']))
		for i in newlist:
			un = str(i['username'])
			ud = db.GqlQuery("SELECT * FROM UserInfo WHERE username= :u",u=un).get()
			i['A']=ud.A
			i['B']=ud.B
			i['C']=ud.C
			i['D']=ud.D
			i['E']=ud.E
			i['F']=ud.F
			i['ADD'] = ud.ADD
			i['STR'] = ud.STR
			i['EON'] = ud.EON
			i['DBY'] = ud.DBY
			i['RUPQ'] = ud.RUPQ
		if not username_s:
			self.render('scoreboard_public.html',newlist=newlist,privacy=privacy)
		else:
			self.render('scoreboard.html',newlist=newlist,privacy=privacy,username_session=username_session,fullname=fullname)
			del sb[:]





class ProblemPage(BaseHandler):
	def get(self):
		username_s = self.session.get('username')
		if not username_s:
			self.redirect('/')
			return
		username_session = str(username_s)
		cts = datetime.utcnow().hour*3600+datetime.utcnow().minute*60+datetime.utcnow().second
		qq = db.GqlQuery("SELECT * FROM UserInfo WHERE username= :u",u=username_session).get()
		if(cts<time_exam_started):
			time_left = time_exam_started-cts
			self.render('contest_to_be_started.html',fullname=str(qq.fullname),time_left=time_left,username_session=username_session)
		elif cts>time_exam_started+contest_duration*3600:
			self.render('contest_ended.html',fullname=str(qq.fullname),username_session=username_session)
		else:
			contest_ends_in = time_exam_started + contest_duration * 3600 - cts
			self.render('problempage.html',username_session=username_session,contest_ends_in=contest_ends_in,fullname=qq.fullname,vA=qq.A,vB=qq.B,vC=qq.C,vD=qq.D,vE=qq.E,vF=qq.F,vADD=qq.ADD,vEON=qq.EON,vSTR=qq.STR,vDBY=qq.DBY,vRUPQ=qq.RUPQ)






class Problem(BaseHandler):
	def get(self):
		username_s = self.session.get('username')
		if not username_s:
			self.redirect('/')
			return
		username_session = str(username_s)
		fname = db.GqlQuery("SELECT * FROM UserInfo WHERE username= :u",u=username_session).get()
		fullname = str(fname.fullname)
		current_url = self.request.url
		p = current_url.split('/')
		prob = p[4]
		if prob=='A':
			#template_values={'username_session':username_session}
			#template = jinja_env.get_template('problemA.html')
			self.response.out.write("Questions will be posted on the day of the contest! Wait!!")
			#self.render('problemA.html',username_session=username_session)
		elif prob=='B':
			#template_values={'username_session':username_session}
			#template = jinja_env.get_template('problemB.html')
			self.response.out.write("Questions will be posted on the day of the contest! Wait!!")
			#self.response.out.write(template.render(template_values))
			#self.render('problemB.html',username_session=username_session)
		elif prob=='C':
			#template_values={'username_session':username_session}
			#template = jinja_env.get_template('problemC.html')
			#self.response.out.write(template.render(template_values))
			self.response.out.write("Questions will be posted on the day of the contest! Wait!!")
			#self.render('problemC.html',username_session=username_session)
		elif prob=='D':
			#template_values={'username_session':username_session}
			#template = jinja_env.get_template('problemD.html')
			#self.response.out.write(template.render(template_values))
			self.response.out.write("Questions will be posted on the day of the contest! Wait!!")
			#self.render('problemD.html',username_session=username_session)
		elif prob=='E':
			#template_values={'username_session':username_session}
			#template = jinja_env.get_template('problemE.html')
			#self.response.out.write(template.render(template_values))
			self.response.out.write("Questions will be posted on the day of the contest! Wait!!")
			#self.render('problemE.html',username_session=username_session)
		elif prob=='F':
			#template_values={'username_session':username_session}
			#template = jinja_env.get_template('problemF.html')
			#self.response.out.write(template.render(template_values))
			self.response.out.write("Questions will be posted on the day of the contest! Wait!!")
			#self.render('problemF.html',username_session=username_session)
		elif prob=='ADD':
			self.render('ADD.html',username_session=username_session,fullname=fullname)
		elif prob=='STR':
			self.render('STR.html',username_session=username_session,fullname=fullname)
		elif prob=='EON':
			self.render('EON.html',username_session=username_session,fullname=fullname)
		elif prob=='DBY':
			self.render('DBY.html',username_session=username_session,fullname=fullname)
		elif prob=='RUPQ':
			self.render('RUPQ.html',username_session=username_session,fullname=fullname)
		else:
			self.response.out.write("There is no such problem code currently on dubhacking!")




#class Submit(BaseHandler):
#	def get(self):
#		username_s = self.session.get('username')
#		username_session = str(username_s)
#		#template_values={'username_session':username_session}
#		#template = jinja_env.get_template('submit.html')
#		#self.response.out.write(template.render(template_values))
#		self.render('submit.html',username_session=username_session)
		




class Idea(BaseHandler):
	def get(self):
		username_s = self.session.get('username')
		username_session = str(username_s)
		#template_values={'username_session':username_session}
		#template = jinja_env.get_template('ideabox.html')
		#self.response.out.write(template.render(template_values))
		self.render('ideabox.html',username_session=username_session)




#class PostIdea(BaseHandler):
#	def get(self):
#		self.response.out.write("You are not authorised to access this URL. Only Dubhacking can access it. :)")
#
#	def post(self):
#		username_s = self.session.get('username')
#		username_session = str(username_s)
#		idea = str(self.request.get('submitted_idea'))
		#Send the idea to the database






class Settings(BaseHandler):
	def get(self):
		username_s = self.session.get('username')
		if not username_s:
			self.redirect('/')
			return
		username_session = str(username_s)
		fn = db.GqlQuery("SELECT * FROM UserInfo WHERE username= :u",u=username_session).get()
		fullname = str(fn.fullname)
		dp_link = str(fn.dp_link)
		cp_link = str(fn.cp_link)
		#template_values={'username_session':username_session,'fullname':fullname}
		#template = jinja_env.get_template('settings.html')
		#self.response.out.write(template.render(template_values))
		self.render('settings.html',username_session=username_session,fullname=fullname,tagline=str(fn.tagline),cp_link=cp_link,aboutme=str(fn.aboutme),portfolio=str(fn.portfolio),dp_link=str(dp_link))

	def post(self):
		have_error = False
		username_s = self.session.get('username')
		username_session = str(username_s)
		#p = dict(username_session=username_session)
		fn = self.request.get('fullname')
		fullname = str(fn)
		pwd = self.request.get('password')
		password = str(pwd)
		tl = self.request.get('tagline')
		tagline = str(tl)
		ame  = self.request.get('aboutme')
		aboutme = str(ame)
		pf = self.request.get('portfolio')
		portfolio = str(pf)
		dp_li = self.request.get('dp_link')
		dp_link = str(dp_li)
		cp_li = self.request.get('cp_link')
		cp_link = str(cp_li)
		params = dict(username_session=username_session,fullname=fullname,portfolio=portfolio,tagline=tagline,aboutme=aboutme,cp_link=cp_link,dp_link=dp_link)
		if portfolio!="" and portfolio[0:4]!='http':
			have_error = True
			params['tagline_error'] = "Professional profile is known as portfolio. Leave it empty if you don't have one!"
		update = db.GqlQuery("SELECT * FROM UserInfo WHERE username= :u",u=username_session).get()
		if password== str(update.password):
			setattr(update,'fullname',fullname)
			setattr(update,'portfolio',portfolio)
			setattr(update,'tagline',tagline)
			setattr(update,'aboutme',aboutme)
			setattr(update,'dp_link',dp_link)
			setattr(update,'cp_link',cp_link)
			update.put()
			self.redirect('/user/'+username_session)
		else:
			have_error = True
			params['error_verify'] = 'Incorrect Password'
			#self.render('settings.html',**params)
		if have_error:
			self.render('settings.html',**params)



#class Info(BaseHandler):
#	def post(self):
#		username_s = self.session.get('username')
#		username_session = str(username_s)
#		fn = self.request.get('fullname')
#		fullname = str(fn)
#		pwd = self.request.get('password')
#		password = str(pwd)
#		pf = self.request.get('portfolio')
#		portfolio = str(pf)
#		tl = self.request.get('tagline')
#		tagline = str(tl)
#		ame  = self.request.get('aboutme')
#		aboutme = str(ame)
#		update = db.GqlQuery("SELECT * FROM UserInfo WHERE username= :u",u=username_session).get()
#		if password== str(update.password):
#			setattr(update,'fullname',fullname)
#			setattr(update,'portfolio',portfolio)
#			setattr(update,'tagline',tagline)
#			setattr(update,'aboutme',aboutme)
#			update.put()
#			self.redirect('/user/'+username_session)
#		else:
#			self.redirect('/settings')


class EditArea(BaseHandler):
	def get(self):
		self.render('edit_submit.html')






class Logout(BaseHandler):
	def get(self):
		if self.session.get('username'):
			del self.session['username']
		self.redirect('/')






class Submit(BaseHandler):
	def get(self):
		username_s = self.session.get('username')
		if not username_s:
			self.redirect('/')
			return
		username_session = str(username_s)
		fn = db.GqlQuery("SELECT * FROM UserInfo WHERE username= :u",u=username_session).get()
		fullname = str(fn.fullname)
		cts = datetime.utcnow().hour*3600+datetime.utcnow().minute*60+datetime.utcnow().second
		if(cts<time_exam_started):
			time_left=time_exam_started-cts
			self.render('contest_to_be_started.html',time_left=time_left,fullname=fullname,username_session=username_session)
		elif(cts>time_exam_started+contest_duration*3600):
			self.render('contest_ended.html',fullname=fullname,username_session=username_session)
		else:
			self.render('submit.html',username_session=username_session,fullname=fullname)
	#def get(self):
		#self.response.out.write("Only Dubhacking server is authorised to access this page. If you reloaded the page to check compilation errors, go BACK then submit your code again.")

	def post(self):
		have_error = False
		api_key = 'KEY' #Taken down for security.
		run_url = 'RUN_URL' #Taken down for security.

		username_s = self.session.get('username')
		username_session = str(username_s)
		submitted_code = self.request.get('submitted_code')
		submitted_lang = self.request.get('submitted_lang')
		submitted_prob = self.request.get('submitted_prob')
		
		submitted_code_str = str(submitted_code)
		submitted_prob_str = str(submitted_prob)
		submitted_lang_str = str(submitted_lang)
		fn = db.GqlQuery("SELECT * FROM UserInfo WHERE username= :u",u=username_session).get()
		fullname = str(fn.fullname)
		params = dict(username_session=username_session,fullname=fullname)
		if submitted_code_str=="":
			params['empty_submit_error'] = "Laaal! :D Where is the code "+fullname+" ??"
			have_error = True


		if have_error:
			self.render('submit.html',**params)
			return



		if(submitted_lang_str == 'C++'):
			lang = 2

		if submitted_code_str == '':
			self.redirect('/submit')
			return

		if submitted_prob_str == 'ADD': #Change 1 
			data = {'api_key':api_key,
			        'source' :submitted_code_str,
			        'lang' : lang,
			        'testcases' : json.dumps(["1 2",
			        	                      "3 5",
			        	                      "2 5"])
			        }
			try:
				r = requests.post(run_url,data=data)
			except requests.ConnectionError:
				self.response.out.write("Currently server is on fire with huge submission rate. No problem! Submit again :D")
				return
			except:
				self.response.out.write("Currently server is on fire with huge submission rate. No problem! Submit it again :)")
				return
			result = r.json()
			if result['result']['compilemessage'] == "":
				stdout0 = result['result']['stdout'][0]
				stdout1 = result['result']['stdout'][1]
				stdout2 = result['result']['stdout'][2]
				time0 = float(result['result']['time'][0])
				time1 = float(result['result']['time'][1])
				time2 = float(result['result']['time'][2])
				update_verdict = db.GqlQuery("SELECT * FROM UserInfo WHERE username= :u",u=username_session).get()
				pv = update_verdict.ADD #Change
				nsu = update_verdict.ns_user
				pact = update_verdict.ac_time
				if stdout0 == '3\n' and stdout1=='8\n' and stdout2=='7\n' and time0<=0.05 and time1<=0.05 and time2<=0.05:
					setattr(update_verdict,'ADD','AC') #change
					cts = datetime.utcnow().hour*3600+datetime.utcnow().minute*60+datetime.utcnow().second
					#act =int(pact) + cts - time_exam_started*3600
					#setattr(update_verdict,'ac_time',act)
					if str(pv)=='NA' or str(pv)=='WA':
						nsu = int(nsu)+1
						act =int(pact) + cts - time_exam_started
						setattr(update_verdict,'ns_user',nsu)
						setattr(update_verdict,'ac_time',act)
				else:
					setattr(update_verdict,'ADD','WA')
					if str(pv)=='AC':
						nsu = int(nsu)-1;
						setattr(update_verdict,'ns_user',nsu)
				update_verdict.put()
				self.redirect('/user/'+username_session)
			else:
				have_error = True
				params['compilation_error'] = str(result['result']['compilemessage'])
				self.render('submit.html',**params)

		elif submitted_prob_str =='STR': #change
			data = {'api_key':api_key,
			        'source': submitted_code_str,
			        'lang': lang,
			        'testcases': json.dumps(["hello","abracadabra","really","wasim","dubhacking"])
			        }
			try:
				r = requests.post(run_url,data=data)
			except requests.ConnectionError:
				self.response.out.write("Currently server is on fire with huge submission rate. No problem! Submit again :D")
				return
			except:
				self.response.out.write("Currently server is on fire with huge submission rate. No problem! Submit again :D")
				return
			result = r.json()
			if result['result']['compilemessage']=="":
				stdout0 = result['result']['stdout'][0]
				stdout1 = result['result']['stdout'][1]
				stdout2 = result['result']['stdout'][2]
				stdout3 = result['result']['stdout'][3]
				stdout4 = result['result']['stdout'][4]
				time0 = float(result['result']['time'][0])
				time1 = float(result['result']['time'][1])
				time2 = float(result['result']['time'][2])
				time3 = float(result['result']['time'][3])
				time4 = float(result['result']['time'][4])
				update_verdict = db.GqlQuery("SELECT * FROM UserInfo WHERE username= :u",u=username_session).get()
				pv = update_verdict.STR #change
				nsu = update_verdict.ns_user
				pact = update_verdict.ac_time
				if stdout0=='5\n' and stdout1=='11\n' and stdout2=='6\n' and stdout3=='5\n' and stdout4=='10\n' and time0<=0.03 and time1<=0.03 and time2<=0.03 and time3<=0.03 and time4<=0.03:
					setattr(update_verdict,'STR','AC') #change
 					cts = datetime.utcnow().hour*3600+datetime.utcnow().minute*60+datetime.utcnow().second
					if str(pv)=='NA' or str(pv)=='WA':
						nsu = int(nsu)+1
						act =int(pact) + cts - time_exam_started
						setattr(update_verdict,'ns_user',nsu)
						setattr(update_verdict,'ac_time',act)
				else:
					setattr(update_verdict,'STR','WA')
					if str(pv)=='AC':
						nsu = int(nsu)-1
						setattr(update_verdict,'ns_user',nsu)
				update_verdict.put()
				self.redirect('/user/'+username_session)
			else:
				have_error = True
				params['compilation_error'] = str(result['result']['compilemessage'])
				self.render('submit.html',**params)

		elif submitted_prob_str == 'EON':
			data = {'api_key':api_key,
			        'source': submitted_code_str,
			        'lang':lang,
			        'testcases': json.dumps(["2","7"])
			        }
			try:
				r = requests.post(run_url,data=data)
			except requests.ConnectionError:
				self.response.out.write("Currently server is on fire with huge submission rate. No problem! Submit again :D")
				return
			except:
				self.response.out.write("Currently server is on fire with huge submission rate. No problem! Submit again :D")
				return
			result = r.json()
			if result['result']['compilemessage']=="":
				stdout0 = result['result']['stdout'][0]
				stdout1 = result['result']['stdout'][1]
				time0 = float(result['result']['time'][0])
				time1 = float(result['result']['time'][1])
				update_verdict = db.GqlQuery("SELECT * FROM UserInfo WHERE username= :u",u=username_session).get()
				pv = update_verdict.EON
				nsu = update_verdict.ns_user
				pact = update_verdict.ac_time
				if stdout0=='YES\n' and stdout1=='NO\n' and time0<0.1 and time1<0.1:
					setattr(update_verdict,'EON','AC')
					cts = datetime.utcnow().hour*3600+datetime.utcnow().minute*60+datetime.utcnow().second
					if str(pv)=='NA' or str(pv)=='WA' or str(pv)=='TLE':
						nsu = int(nsu)+1
						act =int(pact) + cts - time_exam_started
						setattr(update_verdict,'ns_user',nsu)
						setattr(update_verdict,'ac_time',act)
				elif time0>0.1 or time1>0.1:
					setattr(update_verdict,'EON','TLE')
					if str(pv)=='AC':
						nsu = int(nsu)-1
						setattr(update_verdict,'ns_user',nsu)
				else:
					setattr(update_verdict,'EON','WA')
					if str(pv)=='AC':
						nsu = int(nsu)-1
						setattr(update_verdict,'ns_user',nsu)
				update_verdict.put()
				self.redirect('/user/'+username_session)
			else:
				have_error = True
				params['compilation_error'] = str(result['result']['compilemessage'])
				self.render('submit.html',**params)


		elif submitted_prob_str == 'DBY':
			data = {'api_key':api_key,
			        'source' :submitted_code_str,
			        'lang' :lang,
			        'testcases' : json.dumps(["5 1","5 5","5 2","1 1"])
			        }
			try:
				r = requests.post(run_url,data=data)
			except requests.ConnectionError:
				self.response.out.write("Currently server is on fire with huge submission rate. No problem! Submit again :D")
				return
			except:
				self.response.out.write("Currently server is on fire with huge submission rate. No problem! Submit again :D")
				return
			result = r.json()
			if result['result']['compilemessage']=="":
				stdout0 = result['result']['stdout'][0]
				stdout1 = result['result']['stdout'][1]
				stdout2 = result['result']['stdout'][2]
				stdout3 = result['result']['stdout'][3]
				time0 = float(result['result']['time'][0])
				time1 = float(result['result']['time'][1])
				time2 = float(result['result']['time'][2])
				time3 = float(result['result']['time'][3])
				update_verdict = db.GqlQuery("SELECT * FROM UserInfo WHERE username= :u",u=username_session).get()
				pv = update_verdict.DBY
				nus = update_verdict.ns_user
				pact = update_verdict.ac_time
				if stdout0=='5\n' and stdout1=='1\n' and stdout2=='2\n' and stdout3=='1\n' and time0<0.3 and time1<0.3 and time2<0.3 and time3<0.3:
					setattr(update_verdict,'DBY','AC')
					cts = datetime.utcnow().hour*3600+datetime.utcnow().minute*60+datetime.utcnow().second
					if str(pv)=='NA' or str(pv)=='WA':
						nus = int(nus)+1
						act =int(pact) + cts - time_exam_started
						setattr(update_verdict,'ns_user',nus)
						setattr(update_verdict,'ac_time',act)
				else:
					setattr(update_verdict,'DBY','WA')
					if str(pv)=='AC':
						nus = int(nus)-1
						setattr(update_verdict,'ns_user',nus)
				update_verdict.put()
				self.redirect('/user/'+username_session)
			else:
				have_error = True
				params['compilation_error'] = str(result['result']['compilemessage'])
				self.render('submit.html',**params)


		elif submitted_prob_str =='RUPQ':
			data = {'api_key':api_key,
			        'source' :submitted_code_str,
			        'lang':lang,
			        'testcases' : json.dumps(["10 3 5\n1 3\n2 4\n6 8","20 4 12\n1 8\n8 12\n13 18\n17 18"])
			        }
			try:
				r = requests.post(run_url,data=data)
			except requests.ConnectionError:
				self.response.out.write("Currently server is on fire with huge submission rate. No problem! Submit again :D")
				return
			except:
				self.response.out.write("Currently server is on fire with huge submission rate. No problem! Submit again :D")
				return
			result = r.json()
			if result['result']['compilemessage']=="":
				stdout0 = result['result']['stdout'][0]
				stdout1 = result['result']['stdout'][1]
				#stdout2 = result['result']['stdout'][2]
				#stdout3 = result['result']['stdout'][3]
				#stdout4 = result['result']['stdout'][4]
				time0 = float(result['result']['time'][0])
				time1 = float(result['result']['time'][1])
				#time2 = float(result['result']['time'][2])
				#time3 = float(result['result']['time'][3])
				#time4 = float(result['result']['time'][4])
				update_verdict = db.GqlQuery("SELECT * FROM UserInfo WHERE username= :u",u=username_session).get()
				pv = update_verdict.F
				nus = update_verdict.ns_user
				pact = update_verdict.ac_time
				if stdout0=="12\n" and stdout1=="26\n" and time0<0.04 and time1<0.04:
					setattr(update_verdict,'RUPQ','AC')
					cts = datetime.utcnow().hour*3600+datetime.utcnow().minute*60+datetime.utcnow().second
					if str(pv)=='NA' or str(pv)=='WA':
						nus = int(nus)+1
						act =int(pact) + cts - time_exam_started
						setattr(update_verdict,'ns_user',nus)
						setattr(update_verdict,'ac_time',act)
				else:
					setattr(update_verdict,'RUPQ','WA')
					if str(pv)=='AC':
						nus = int(nus)-1
						setattr(update_verdict,'ns_user',nus)
				update_verdict.put()
				self.redirect('/user/'+username_session)
			else:
				have_error = True
				params['compilation_error'] = str(result['result']['compilemessage'])
				self.render('submit.html',**params)

		elif submitted_prob_str=='D':
			data = {'api_key':api_key,
			        'source' : submitted_code_str,
			        'lang':lang,
			        'testcases': json.dumps(["science\n 4 n s c e"])
			        }
			try:
				r = requests.post(run_url,data=data)
			except requests.ConnectionError:
				self.response.out.write("Currently server is on fire with huge submission rate. No problem! Submit again :D")
				return
			except:
				self.response.out.write("Currently server is on fire with huge submission rate. No problem! Submit again :D")
				return
			result = r.json()
			if result['result']['compilemessage']=="":
				stdout0 = result['result']['stdout'][0]
				time0 = float(result['result']['time'][0])
				update_verdict = db.GqlQuery("SELECT * FROM UserInfo WHERE username= :u",u=username_session).get()
				pv = update_verdict.D
				nus = update_verdict.ns_user
				pact = update_verdict.ac_time
				if stdout0=="n 1\ns 1\nc 2\ne 2\n" and time0<0.02:
					setattr(update_verdict,'D','AC')
					cts = datetime.utcnow().hour*3600+datetime.utcnow().minute*60+datetime.utcnow().second
					if str(pv)=='NA' or str(pv)=='WA':
						nus = int(nus)+1
						act =int(pact) + cts - time_exam_started
						setattr(update_verdict,'ns_user',nus)
						setattr(update_verdict,'ac_time',act)
				else:
					setattr(update_verdict,'D','WA')
					if str(pv)=='AC':
						nus = int(nus)-1
						setattr(update_verdict,'ns_user',nus)
				update_verdict.put()
				self.redirect('/user/'+username_session)
			else:
				have_error = True
				params['compilation_error'] = str(result['result']['compilemessage'])
				self.render('submit.html',**params)

		#elif submitted_prob_str=='ADD':
		#	data = {'api_key':api_key,
		#	        'source':submitted_code_str,
		#	        'lang':lang,
		#	        'testcases':json.dumps(["2 4","1 0","2 10","10 10"])

		#	       }
		#	r = requests.post(run_url,data=data)
		#	result = r.json()
		#	if result['result']['compilemessage']=="":
		#		stdout0 = result['result']['stdout'][0]
		#		stdout1 = result['result']['stdout'][1]
		#		stdout2 = result['result']['stdout'][2]
		#		stdout3 = result['result']['stdout'][3]
		#		time0 = result['result']['time'][0]
		#		time1 = result['result']['time'][1]
		#		time2 = result['result']['time'][2]
		#		time3 = result['result']['time'][3]
		#		update_verdict = db.GqlQuery("SELECT * FROM UserInfo WHERE username= :u",u=username_session).get()
		#		pv = update_verdict.ADD
		#		nus = update_verdict.ns_user
		#		pact = update_verdict.ac_time
		#		if stdout0=="6\n" and stdout1=="1\n" and stdout2=="12\n" and stdou3=="20\n" and time0<0.04 and time1<0.04 and time2<0.04 and time3<0.04:
		#			setattr(update_verdict,'ADD','AC')
		#			cts = datetime.utcnow().hour*360+datetime.utcnow().minute*60+datetime.utcnow().second
		#			if str(pv)=='NA' or str(pv)=='WA':
		#				nus = int(nus)+1
		#				act = int(pact) + cts - time_exam_started*3600
		#				setattr(update_verdict,'ns_user',nus)
		#				setattr(update_verdict,'ac_time',act)
		#			else:
		#				setattr(update_verdict,'ADD','WA')
		#				if str(pv)=='AC':
		#					nus = int(nus)-1
		#					setattr(update_verdict,'ns_user',nus)
		#				update_verdict.put()
		#				self.redirect('/user/'+username_session)
		#		else:
		#			have_error=True
		#			params['compilation_error'] = str(result['result']['compilemessage'])
		#			self.render('submit.html',**params)

		else:
			self.response.out.write("There's no such problem code")









		
config = {}
config['webapp2_extras.sessions'] = {'secret_key': ' ','cookie_args':{'max_age':86400}}
#config['webapp2_extras.jinja2'] = {'template_path':'C:\Users\TOSHIBA pc\Documents\apps\dubhacking\templates'}


app = webapp2.WSGIApplication([
	('/',Main),
	('/about',About),
    ('/signup',Signup),
    ('/user/.*',Userprofile),
    ('/edit',EditArea),
    ('/problem/.*',Problem),
    ('/problems',ProblemPage),
    ('/submit',Submit),
    ('/idea',Idea),
    ('/settings',Settings),
    ('/confirm_email',Confirm_email),
    ('/confirming/.*',Confirming),
    ('/login',Login),
    ('/logout',Logout),
    ('/scoreboard',Scoreboard)

],config=config, debug=True)
