# use AES primitive, high crypto dome ?
# create AES object, specify mode (ECB), but only ever encrypt one block at a time
# never pass it more than one block at a time
# how to get parts and then change and submit, w3c site, do encoding correctly ('utf-8')
from Crypto.Cipher import AES
import crypto
import base64
import requests
import re

STR_COOKIE_NAME = "auth_token"


def pad(msg, block_size):
	pad_len = block_size - (len(msg) % block_size)  # get how many padding bytes we'll need
	return msg + bytes([pad_len] * pad_len)  # add that value as padding to end of msg


def unpad(msg, block_size):
	if len(msg) % block_size != 0:
		raise ValueError('stream length invalid, must be multiple of block size')
	pad_len = msg[-1]  # for a valid padding, the last byte value will be equal to the number of padding bytes
	# that exist
	for i in range(1, pad_len + 1):  # go through the msg backwards pad length positions
		# print(f'Stream byte: {msg[-i]} at pos: {-i}')
		pos_pad = msg[-i]  # get possible pos pad
		if pos_pad != pad_len:  # check that the byte is equal to the pad length number
			raise ValueError('invalid padding')
	msg = msg[:-i]  # cut the pad byte off
	return msg


def ecb_encrypt(key, plaintext):
	block_size = AES.block_size
	cipher = AES.new(key, AES.MODE_ECB)
	padded = pad(plaintext, block_size)
	ciphertext = cipher.encrypt(padded)
	return ciphertext


def ecb_decrypt(key, ciphertext, pad_scheme):
	block_size = AES.block_size
	if len(ciphertext) % block_size != 0:  # not a multiple of the block size
		raise ValueError("Must be multiple of block size")
	cipher = AES.new(key, AES.MODE_ECB)
	decrypted = cipher.decrypt(ciphertext)
	print(decrypted)
	if pad_scheme == "pkcs7":
		plaintext = unpad(decrypted, block_size)
	else:
		plaintext = crypto.ansix923_strip(decrypted, block_size)
	return plaintext


def find_ecb(cipher):
	# detect ecb by looking at the repetition of blocks
	blocks = []
	for i in range(54, len(cipher), 16):
		blocks.append(cipher[i:i + 16])
	# find ratio of distinct blocks to total blocks
	return len(set(blocks)) / len(blocks)


def create_admin_plaintext():
	manipulated_plaintext = b"user=admin&uid=0&role=admin"
	block_size = AES.block_size
	# pad using ANSIx923
	padded = crypto.ansix923_pad(manipulated_plaintext, block_size)
	return padded


# function to create a userwith specific username
def create_user(user, password):
	url = "http://localhost:8080/register"
	payload = {'Register': "", 'user': user, 'password': password}
	response = requests.post(url, data=payload)
	return response.text


# function to get cookie from specific user
def retrieve_cookie(user, password):
	url = "http://localhost:8080/home"
	payload = {'user': user, 'password': password}
	response = requests.post(url, data=payload)
	cookie = response.cookies.get('auth_token')
	return cookie


def cut_cookie(cookie_string):
	print(cookie_string)
	match = re.search(r'auth_token=([0-9a-f]+)', cookie_string)
	if match:
		hex_encoded_cookie = match.group(1)
		print(hex_encoded_cookie)
		return hex_encoded_cookie
	else:
		print("No hex encoded cookie found.")


def attack():
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
	# decode from hex
	first_block = bytes.fromhex(cookie)
	first_block = first_block[0:32]  # cut off last block, so now it ends with role=
	# second user to get the middle block to be 'admin' with correct padding
	s2 = requests.Session()
	second_data = {
		"user": '56789ABCDEF' + crypto.ansix923_pad('admin', 16),
		"password": '123',
		"Register": ''
	}
	# register second user
	s2.post("http://localhost:8080/register", data=second_data)
	second_data = {
		"user": '56789ABCDEF' + crypto.ansix923_pad('admin', 16),
		"password": '123',
		"Login": ''
	}
	# login as second user
	s2.post("http://localhost:8080", data=second_data)
	# get cookie
	cookie2 = str(s2.cookies)
	# extract hex cookie from whole cookie string
	cookie2 = cut_cookie(cookie2)
	second_block = bytes.fromhex(cookie2)  # decode from hex
	second_block = second_block[16:32]  # isolate second block
	manip_cookie = b""
	manip_cookie += first_block + second_block  # put them together
	manip_cookie = manip_cookie.hex()  # hex encode the cookie
	print("plaintext manipulated cookie: ", manip_cookie, len(manip_cookie))
	final_cookie = {
		"auth_token": manip_cookie
	}
	# submit my manipulated cookie
	r = s2.get("http://localhost:8080/home", cookies=final_cookie)
	print(r.content)


def cbc_encrypt(plaintext, key, iv):
	plaintext = pad(plaintext, AES.block_size)  # pad msg to right size
	# encrypt
	aes_obj = AES.new(key, AES.MODE_ECB)
	

def cbc_decrypt(ciphertext, key, iv):
	if len(ciphertext) % AES.block_size != 0:  # not a multiple of the block size
		raise ValueError("Must be multiple of block size")
	# decrypt
	# unpad, throw error if unpadding doesn't work


def main():
	with open("Lab2.TaskII.A.txt", "r") as file:
		base64_ciphertext = file.read()

	ciphertext = base64.b64decode(base64_ciphertext)
	key = b'CALIFORNIA LOVE!'
	plaintext = ecb_decrypt(key, ciphertext, "pkcs7")
	plaintext_str = plaintext.decode('ascii')
	print("Task 2 A, Decrypted plaintext: ", plaintext_str)

	# detecting ECB
	# question: is the bitmap image padded w/ pkcs7? do we need what the key is to decrypt it with?
	with open("Lab2.TaskII.B.txt", "r") as file2:
		lines = file2.readlines()
		# decode from hex
		ciphertext_list = list(map(bytes.fromhex, lines))

	min_count = float("inf")  # to compare scores to, want the lowest
	best_cipher = 0
	for idx, ciphertext in enumerate(ciphertext_list):
		count = find_ecb(ciphertext)
		if count < min_count:  # find ciphertext w/ lowest score, meaning least unique blocks and most repetitive blocks
			min_count = count
			best_cipher = idx
	found = lines[best_cipher].rstrip("\n")  # strip off new line char
	found = bytes.fromhex(found)  # decode from hex
	with open("ecb_image.bmp", "wb") as file_out:
		file_out.write(found)


if __name__ == "__main__":
	main()
	attack()
