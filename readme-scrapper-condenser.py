from pyquery import PyQuery as pq
from github import Github
from urllib.request import Request, urlopen
from urllib.error import HTTPError,URLError
import base64
import os
import json
import re
import collections

languages = ["javascript", "ruby", "java", "php", "python", "c++", "c", "objective-c", "c#", "shell", "css", "perl", "viml", "haskell", "scala"] 
stop_words = ["and", "the", "it", "on", "in", "to", "a", "for", "more", "of", "with", "your", "is", "from", "see", "also"]

def get_most_starred_repos():
    g = Github()

    for lang in languages:
        i = 0
        
        metadata = []

        # create folder named after current language
        if not os.path.exists(lang):
            os.makedirs(lang)

        # search top repos of lang by descending stars
        for repo in g.search_repositories("",sort="stars", order="desc", language=lang):
            temp_data = {}
            temp_data["name"] = repo.name
            temp_data["full_name"] = repo.full_name
            temp_data["stargazers_count"] = repo.stargazers_count
            temp_data["forks_count"] = repo.forks_count
            temp_data["description"] = repo.description
            temp_data["id"] = repo.id
            temp_data["size"] = repo.size
            temp_data["language"] = lang
            temp_data["__html_location"] = lang+"/"+str(i)+"-readme.html"

            metadata.append(temp_data)

            i = i + 1

            if i == 150:
                break

        f = open(lang+"/metadata.json", 'w')
        f.write(json.dumps(metadata))
        f.close()

def download_readme_html():
    for lang in languages:
        json_data=open(lang+'/metadata.json')
        data = json.load(json_data)

        for repo in data:
            if os.path.isfile(repo["__html_location"]):
                continue
            else:
                # fetch readme as a rendered html (as seen in github)
                q = Request('https://api.github.com/repos/'+repo["full_name"]+'/readme')
                q.add_header('Accept', 'application/vnd.github.v3.html')

                try:
                    a = urlopen(q)
                except (HTTPError) as err:
                    if err.code == 404:
                        print("Page not found!" + repo["full_name"])
                        continue
                    elif err.code == 403:
                        print("Access denied!")
                        exit()
                    else:
                        print("error downloading readme from" + repo["full_name"] )
                        continue

                a_content = a.read()

                f = open(repo["__html_location"], 'wb')
                f.write(a_content)
                f.close()

def link_count(d, link_word):
    count = 0
    for link in d("a"):
        if pq(link).attr("href") and link_word in pq(link).attr("href"):
            count = count + 1

    return count

def anchor_link_count(d):
    count = 0
    for link in d("a"):
        if pq(link).attr("href") and '#' != pq(link).attr("href")[0]:
            count = count + 1

    return count

def html_tag_count(d, html_tag):
    count = 0
    for link in d(html_tag):
        count = count + 1

    return count

def word_mention_count(d, word):
    text = d.text()
    return text.lower().split().count(word)

def words_containing_word_count(d, word):
    text = d.text().lower().split()
    return len([w for w in text if word in w])

def word_count(d):
    return len(d.text().split())

def email_count(d):
    text = d.text().lower().split()
    return len([x for i, x in enumerate(text) if re.search(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", x)])

def word_document_frequency(hash_counter, words):
    for word in words:
        if word not in hash_counter:
            hash_counter[word] = 1
        else:
            hash_counter[word] = 1 + hash_counter[word]

    return hash_counter

def get_stats():
    for lang in languages:
        json_data=open(lang+'/metadata.json')
        data = json.load(json_data)
        h1_word_hash = {}
        hn_word_hash = {}

        repos = { "lang":lang,"words":0, "name":0, "twitter":0, "github":0, "codeclimate":0, "travis":0, "images":0, "paragraphs":0, "code":0, "titles":0, "bugs":0, "license":0, "email":0, "donation":0, "link":0 }

        for repo in data:
            if os.path.isfile(repo["__html_location"]):
                d = pq(filename=repo["__html_location"])
                # print(repo["__html_location"])
                repo["_word_count"] = word_count(d)
                repos["words"] += repo["_word_count"]
                repo["_name_mention_count"] = word_mention_count(d,repo["name"].lower())
                repos["name"] += repo["_name_mention_count"]
                repo["_twitter_link_count"] = link_count(d,"twitter")
                if repo["_twitter_link_count"] > 0:
                    repos["twitter"] += 1 
                repo["_github_link_count"] = link_count(d,"github")
                repos["github"] += repo["_github_link_count"]
                repo["_travis_link_count"] = link_count(d,"travis")
                if repo["_travis_link_count"] > 0:
                    repos["travis"] += 1 
                repo["_codeclimate_link_count"] = link_count(d,"codeclimate")
                if repo["_codeclimate_link_count"] > 0:
                    repos["codeclimate"] += 1 
                repo["_images_count"] = html_tag_count(d,"img")
                if repo["_images_count"] > 0:
                    repos["images"] += 1 
                repo["_paragraph_count"] = html_tag_count(d,"p")
                repos["paragraphs"] += repo["_paragraph_count"] 
                repo["_code_count"] = html_tag_count(d,"pre")
                if repo["_code_count"] > 0:
                    repos["code"] += 1 
                repo["_header_count"] = html_tag_count(d,":header")
                if repo["_header_count"] > 0:
                    repos["titles"] += 1 
                repo["_h1_count"] = html_tag_count(d,"h1")
                repo["_license_mention_count"] = words_containing_word_count(d,"license")
                if repo["_license_mention_count"] > 0:
                    repos["license"] += 1 
                repo["_issue_mention_count"] = words_containing_word_count(d,"issue")
                repo["_donation_mention_count"] = words_containing_word_count(d,"donat")
                if repo["_donation_mention_count"] > 0:
                    repos["donation"] += 1 
                repo["_bug_mention_count"] = words_containing_word_count(d,"bug")
                if repo["_bug_mention_count"] > 0 or repo["_issue_mention_count"] > 0:
                    repos["bugs"] += 1 
                repo["_email_count"] = email_count(d)
                if repo["_email_count"] > 0:
                    repos["email"] += 1 
                repo["_anchor_count"] = anchor_link_count(d)
                if repo["_anchor_count"] > 0:
                    repos["link"] += 1 
                set_of_h1_words = set( re.sub(r'([^\s\w])+', '', d("h1").text().lower() ).split())
                if repo["name"].lower() in set_of_h1_words:
                    set_of_h1_words.discard(repo["name"].lower())
                    set_of_h1_words.add("__github_repo_name")
                word_document_frequency(h1_word_hash, set_of_h1_words)
                set_of_hn_words = set( re.sub(r'([^\s\w])+', '', d(":header").text().lower() ).split())
                if repo["name"].lower() in set_of_hn_words:
                    set_of_hn_words.discard(repo["name"].lower())
                    set_of_hn_words.add("repo_name")
                word_document_frequency(hn_word_hash, set_of_hn_words)
        # od = collections.OrderedDict(sorted(h1_word_hash.items(), key=lambda x: x[1]))
        for word in stop_words:
            if word in hn_word_hash.keys():
                hn_word_hash[word]=-1
        od2 = collections.OrderedDict(sorted(hn_word_hash.items(), key=lambda x: x[1]))
        common_words = list(od2.items())[::-1]
        print(json.dumps(common_words[:15]))

        # print(repos)
        repos["words"] /= 150
        repos["words"] = int(round(repos["words"],1))
        repos["name"] /= 150
        repos["name"] = int(round(repos["name"],1))
        repos["github"] /= 150
        repos["github"] = int(round(repos["github"],1))
        repos["paragraphs"] /= 150
        repos["paragraphs"] = int(round(repos["paragraphs"],1))
        # print(repos)

        f = open(lang+".json", 'w')
        f.write(json.dumps(repos))
        f.close()
        f = open(lang+"-words.json", 'w')
        f.write(json.dumps(common_words[:15]))
        f.close()

get_stats()
