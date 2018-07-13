#!/usr/bin/env python

from github import Github, Comparison, Commit, GithubObject
import os
import json
import sys
import time
import copy
import requests
import time
import re
#from ipdb import set_trace
from jinja2 import Environment, PackageLoader, select_autoescape
from collections import OrderedDict

class ScanOrg():
	def __init__(self, user, passwd, acct=None, org=None, base_url="https://api.github.com"):
		self.github = Github(user, passwd, base_url=base_url)
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
	def __init__(self, user, passwd, acct=None, org=None, base_url="https://api.github.com",search_query="/search/code?q={}:{}+{}", 
		headers={"Accept":"application/vnd.github.v3.text-match+json"}):

		self.user = user
		self.passwd = passwd
		self.acct=acct
		self.org=org
		self.base_url = "https://api.github.com"
		self.search_query=search_query
		self.headers = headers

	def search(self, query, sre=""):
		if(self.acct):
			myquery = self.search_query.format("user", self.acct, query)
		else:
			myquery = self.search_query.format("org", self.org, query)

		sleeper=31
		while sleeper != 0:
			r = requests.get(self.base_url+myquery, auth=(self.user, self.passwd), headers=self.headers)
			rjson = r.json()
			if "message" in rjson and "API rate limit exceeded" in rjson["message"]:
				sleeper += sleeper
				#print("(resting)")
				time.sleep(sleeper)
			else:
				sleeper = 0

		results = []

		if "total_count" in rjson and rjson["total_count"] != 0:
			for items in rjson["items"]:
				if "text_matches" in items:
					for matches in items["text_matches"]:
						#set_trace()
						if re.search(sre, matches["fragment"]):
							results.append({"query": query, "url": items["html_url"], "fragment": matches["fragment"]}) 
		return results

class Report():
	def __init__(self):
		self.env=Environment(loader=PackageLoader("polecat", "reports"),
							autoescape=select_autoescape(["html", "xml"]))

	def generate_report(self, template, results):
		tc = self.env.get_template(template)
		return tc.render(report_data=results)

scan_list = {"AWS_ACCESS_KEY_ID":r"(?i)AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY":"(?i)AWS_SECRET_ACCESS_KEY",
"KEY-----":"BEGIN.*PRIVATE", "PrivateKey":"PrivateKey", "ConsumerSecret":"ConsumerSecret","passwd":"(?i)passwd","password":"(?i)password"}

if __name__ == "__main__":
	(user, passwd) = open(os.path.expanduser('~')+"/.gitcred").read().strip().split(":")
	org = ScanOrg(user, passwd, org=sys.argv[1])
	members = org.get_members()
	r = OrderedDict()

	s=SearchAccount(user, passwd, org=sys.argv[1])
	r[sys.argv[1]] = []
	for term, sre in scan_list.items():
		r[sys.argv[1]] += s.search(term, sre)

	for member in members:
		r[member.login] = []
		s=SearchAccount(user, passwd, acct=str(member.login))
		for term, sre in scan_list.items():
			r[member.login] = r[member.login] + s.search(term, sre)

	reporter = Report()
	print(reporter.generate_report("template.html", results=r).encode('utf-8'))
