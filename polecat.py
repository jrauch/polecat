from github import Github, Comparison, Commit, GithubObject
import os
import json
import sys
import time
import copy
import requests
import time
from ipdb import set_trace

reload(sys)
sys.setdefaultencoding("ISO-8859-1")

class ScanOrg():
	def __init__(self, user, passwd, acct=None, org=None, base_url="https://api.github.com"):
		self.github = Github(user, passwd, base_url=base_url)
		#self.repo_owner = repo_owner
		self.user_handle = None
		self.organization_handle = None
		if acct:
			self.user_handle = self.github.get_user(acct)
		if org:
			self.organization_handle = self.github.get_organization(org)

	def get_members(self):
		if self.organization_handle:
			return self.organization_handle.get_members()
		else:
			return self.user_handle.get_members()

class SearchAccount():
	def __init__(self, user, passwd, acct=None, org=None, base_url="https://api.github.com",search_query="/search/code?q=user:{}+{}"):
		self.user = user
		self.passwd = passwd
		self.acct=acct
		self.org=org
		self.base_url = "https://api.github.com"
		self.search_query=search_query

	def search(self, query):
		myquery = self.search_query.format(self.acct, query)
		sleeper=16
		while sleeper != 0:
			r = requests.get(self.base_url+myquery, auth=(self.user, self.passwd))
			rjson = r.json()
			if "message" in rjson and "API rate limit exceeded" in rjson["message"]:
				sleeper += sleeper
				print("(resting)")
				time.sleep(sleeper)
			else:
				sleeper = 0

		results = set()

		if "total_count" in rjson and rjson["total_count"] != 0:
			for items in rjson["items"]:
				results.add("Found '{}' in {}".format(query, items["html_url"])) 
		#for result in results:
		#	print(result)
		return results


if __name__ == "__main__":
	(user, passwd) = open(os.path.expanduser('~')+"/.gitcred").read().strip().split(":")
	org = ScanOrg(user, passwd, org=sys.argv[1])
	members = org.get_members()
	r=set()

	for member in members:
		print(member.login)
		s=SearchAccount(user, passwd, acct=str(member.login))
		r = r.union(s.search("AWS_ACCESS_KEY_ID"))
		r = r.union(s.search("AWS_SECRET_ACCESS_KEY"))

	for result in r:
		print(result)
