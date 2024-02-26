from Crypto.Cipher import AES
import crypto
import base64
import requests
import re
import crypto
import lab2


def cut_cookie(cookie_string):
	print(cookie_string)
	match = re.search(r'auth_token=([0-9a-f]+)', cookie_string)
	if match:
		hex_encoded_cookie = match.group(1)
		print(hex_encoded_cookie)
		return hex_encoded_cookie
	else:
		print("No hex encoded cookie found.")


def cbc_cookie_attack():
	s = requests.Session()
	# username long enough so block ends with role=, to append another block to
	first_data = {
		"user": 'adminaaaaaaaaaa',
		"password": '123',
		"Register": ''
	}
	# register user
	s.post("http://localhost:8080/register", data=first_data)
	first_data = {
		"user": 'adminaaaaaaaaaa',
		"password": '123',
		"Login": ''
	}
	# login as user
	s.post("http://localhost:8080", data=first_data)
	# get cookie
	cookie = str(s.cookies)
	# extract cookie from whole  cookie string
	cookie = cut_cookie(cookie)
	print(cookie)


def main():
	cbc_cookie_attack()


if __name__ == "__main__":
	main()