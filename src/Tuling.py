import urllib.request
import urllib.parse
import re


class Tuling:
    url = "http://www.tuling123.com/openapi/api"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:56.0) Gecko/20100101 Firefox/56.0",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    pattern = re.compile("{\"code\":[0-9]+,\"text\":\"([^\"]+)\"")

    def __init__(self, key="2f42355beb56432eae25901621e51a63"):
        self.key = key

    def answer(self, user_id, question, location="Beijing"):
        """
        See following
        :param user_id: user identifier
        :param question: question
        :param location: location
        :return: answer to the question
        """
        data = urllib.parse.urlencode({"key": self.key,
                                       "info": question,
                                       "loc": location,
                                       "userid": user_id}).encode('utf-8')
        question = urllib.request.Request(
            url=Tuling.url, headers=Tuling.headers, data=data, method="POST")
        text = urllib.request.urlopen(question).read().decode()
        print(text)
        answer = Tuling.pattern.match(text)
        if answer is None:
            return "机器狗也不知道说啥了"
        return answer.group(1)
