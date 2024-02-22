import web
from Crypto.Cipher import AES
from web import form
import crypto, hashlib, os, lab2
import threading
import requests

STR_COOKIE_NAME = "auth_token"

master_key = os.urandom(16)

# Database of users. Key is username, value is [SHA1(password), userid, role]
user_db = {"admin": ["119ba0f0a97158cd4c92f9ee6cf2f29e75f5e05a", 0, "admin"]}
user_ids = int(1)

render = web.template.render('templates/')
urls = ('/', 'index',
        '/register', 'register',
        '/logout', 'logout',
        '/home', 'home')


class index:
	login_form = form.Form(
		form.Textbox("user",
		             form.notnull,
		             description="Username",
		             id='usernameBox'),
		form.Password("password",
		              form.notnull,
		              description="Password",
		              id='passwordBox'),
		form.Button("Login",
		            id='loginButton'))

	nullform = form.Form()

	def GET(self):
		user, uid, role = verify_cookie()
		if user != "":
			return render.login(self.nullform, user, "Already logged in.")

		return render.login(self.login_form(), "", "")

	def POST(self):
		form = self.login_form()

		if not form.validates():
			return render.login(form, "", "Invalid form data.")

		user = form.d.user
		pw = hashlib.sha1(form.d.password.encode("UTF-8")).hexdigest()

		if user in user_db and user_db[user][0] == pw:
			create_cookie(user, user_db[user][1], user_db[user][2])
			raise web.seeother('/home')

		return render.login(form, "", "Username/Password Incorrect")


class register:
	myform = form.Form(
		form.Textbox("user",
		             form.notnull,
		             description="Username"),
		form.Password("password",
		              form.notnull,
		              description="Password"),
		form.Button("Register",
		            description="Register"))

	nullform = form.Form()

	def GET(self):
		user, uid, role = verify_cookie()
		if user != "":
			return render.generic(self.nullform, user, "", "Already logged in.")

		return render.generic(self.myform(), "", "Enter a username and password.", "")

	def POST(self):
		global user_ids
		form = self.myform()
		msg = ""
		err = ""

		if not form.validates():
			err = "Invalid fields."
		# Prevent those h4x0rs from trying to create user names
		# that might elevate their privellages.
		elif "=" in form.d.user or "&" in form.d.user or ";" in form.d.user:
			err = "Invalid characters in username."
		else:
			if form.d.user in user_db:
				err = "User already registered."
			else:
				# Set the password and role: only non-admin "users" can be created
				# through the web interface
				user_db[form.d.user] = [hashlib.sha1(form.d.password.encode("UTF-8")).hexdigest(), user_ids, "user"]
				user_ids += 1
				msg = "User registered."
		return render.generic(self.nullform(), "", msg, err)


class logout:
	def GET(self):
		destroy_cookie()
		raise web.seeother('/')


class home:

	def GET(self):
		user, uid, role = verify_cookie()

		if user == "":
			return render.home("", "", "", "Please log in.")
		elif role == "admin":
			msg = "Welcome, Admin!"
		else:
			msg = "Welcome, " + user

		return render.home(user, role, msg, "")


def destroy_cookie():
	web.setcookie(STR_COOKIE_NAME, "", expires=-1)


def create_cookie(user, uid, role):
	cookie = crypto.create_crypto_cookie(user, uid, role, master_key)
	web.setcookie(STR_COOKIE_NAME, cookie.hex())


def verify_cookie():
	cookie = web.cookies().get(STR_COOKIE_NAME)
	if cookie == None:
		return "", "", ""
	try:
		return crypto.verify_crypto_cookie(bytes.fromhex(cookie), master_key)
	except:
		return "", "", ""


# function to create a userwith specific username
def create_user(user, password):
	url = "http://localhost:8080/register"
	payload = {'Register': "", 'user': user, 'password': password}
	response = requests.post(url, data=payload)
	return response.text


# function to get cookie from specific user
# def retrieve_cookie(user, password):
# 	url = "http://localhost:8080/"
# 	payload = {'user': user, 'password': password}
# 	response = requests.post(url, data=payload)
# 	cookie = response.cookies.get('auth_token')
# 	return cookie


def attack():
	first_user = 'adminaaaaaaaaaa'  # username long enough so block ends with role=, to append another block to
	second_user = '56789ABCDEF' + crypto.ansix923_pad('admin', 16)  # second user to get the middle block to be 'admin' with correct padding
	create_user(first_user, '123')  # create user
	first_block = web.cookies().get(STR_COOKIE_NAME)  # get the cookie
	print(first_block)
	first_block = bytes.fromhex(first_block)  # decode from hex
	first_block = lab2.ecb_decrypt(master_key, first_block, "ansix923")# decrypt
	print("first cookie decrypted: ", first_block)
	first_block = first_block[:-16]# cut off last block, so now it ends with role=
	print("first block: ", first_block)
	create_user(second_user, '123')  # create second user
	second_block = web.cookies().get(STR_COOKIE_NAME)  # get second cookie
	second_block = bytes.fromhex(second_block)  # decode from hex
	second_block = lab2.ecb_decrypt(master_key, second_block, "ansix923")# decrypt
	print("cookie decrypted: ", second_block)
	second_block = last_block[16:32]  # isolate second block
	print("last block: ", second_block)
	manip_cookie = first_block + second_block  # put them together
	print("plaintext manipulated cookie: ", manip_cookie)



if __name__ == "__main__":
	# app = web.application(urls, globals())
	# app.run()
	# attack()
	web_app_thread = threading.Thread(target=web.application(urls, globals()).run)
	web_app_thread.start()
	attack()
