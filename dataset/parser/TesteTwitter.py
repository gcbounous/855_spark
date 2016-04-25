#! /usr/bin/python2.7
# -*- coding:utf-8 -*

import OAuth
import json

def findUser(query):
	user = OAuth.api.search_users(query)
	printUserjason(user[0])

def printUserjason(user):
	print(json.dumps(user._json, sort_keys=True, indent=2, separators=(',', ': ')))
	print(user._json["id"])

def getTwitterUsersFriends(user_id):
	"""
	Recupera a lista de ids dos usuarios que o usuario segue
		-param user_id: id do usurario
		-return lista_amigos: lista de ids dos amigos do usuario
	"""
	lista_amigos = OAuth.api.friends_ids(user_id)
	print(lista_amigos)

def rate_limit():
	limit = OAuth.api.rate_limit_status()
	print(json.dumps(limit, sort_keys=True, indent=2, separators=(',', ': ')))


if __name__ == "__main__":
	findUser("depcarloslereia")