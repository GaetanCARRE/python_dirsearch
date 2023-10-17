import sys
import requests as re
import argparse
import threading
import queue

class DirSearch:
    def __init__(self, args):
        self.url = args.url
        self.wordlist = args.wordlist
        self.recursive = args.recursive
        self.threads = args.threads
        self.result_queue = queue.Queue()
        self.keyword = args.keyword
        self.depth = args.depth
        self.extension = args.extension
        self.vhost = args.vhost
        self.domain = args.domain
        self.fs = args.filter_size

    def run(self):
        # Get wordlist in list
        wordlist = []
        with open(self.wordlist, "r") as f:
            for line in f:
                wordlist.append(line.strip())

        # Split wordlist into self.threads parts
        thread_num = int(self.threads)
        wordlist = [wordlist[i::thread_num] for i in range(thread_num)]
        threads = []

        for i in range(thread_num):
            t = threading.Thread(target=self.search, args=(self.url, wordlist[i], 1))
            print("Thread " + str(i) + " started")
            t.start()
            threads.append(t)

        # Wait for all threads to finish
        for t in threads:
            t.join()

        # Collect results from the queue
        output = []
        while not self.result_queue.empty():
            output.append(self.result_queue.get())

    def search(self, url, wordlist, depth):
        subdomain = None
        if self.extension:
            extension = "." + self.extension
        else:
            extension = ''
        for line in wordlist:
            if self.keyword:
                url_send = url.replace(self.keyword, line.strip() + extension)
                try: 
                    response = re.get(url= url_send)
                except re.exceptions.ConnectionError: # specify exceptions
                    response = None      
            else:
                try:
                    if self.vhost:
                        url_send = url
                        print("")
                        subdomain = line.strip() + "." + self.domain
                        headers = {"Host" : subdomain}
                        response = re.get(self.url, headers=headers, allow_redirects=False)
                    else:
                        url_send = url + "/" + line.strip() + extension
                        response = re.get(url_send)
                except re.exceptions.ConnectionError:
                    print("ConnectionError : " + url_send)
                    response = None
            
            if response:
                if response.status_code != 404:
                    if not subdomain:
                        result = {"url" : url_send, "status_code" : str(response.status_code), "size" : len(response.content)}
                    else:
                        result = {"url" : url_send, "status_code" : str(response.status_code), "size" : len(response.content), 'subdomain' : subdomain}
                    if self.fs:
                        if result["size"] != self.fs:
                            print(result)
                    else:
                        print(result)
                        
                    self.result_queue.put(result)
                    if self.recursive and depth < int(self.depth):
                        print("calling rec")
                        self.search(url + "/" + line.strip(), self.wordlist, depth + 1)



if __name__ == "__main__":
    print(
            """                                               
 ____  _                              _     
|  _ \(_)_ __ ___  ___  __ _ _ __ ___| |__  
| | | | | '__/ __|/ _ \/ _` | '__/ __| '_ \ 
| |_| | | |  \__ \  __/ (_| | | | (__| | | |
|____/|_|_|  |___/\___|\__,_|_|  \___|_| |_|
            """
        )
    print("Usage: python3 dirsearch.py <url> <wordlist>")
    parser = argparse.ArgumentParser(description="Dirsearch")
    parser.add_argument('-u', '--url', help="URL to search", required=True)
    parser.add_argument('-w', '--wordlist', help="Wordlist", required=True)
    parser.add_argument('-r', '--recursive', action='store_true', required=False)
    parser.add_argument('-t', '--threads', help="Number of threads", required=False, default=10)
    parser.add_argument('-o', '--output', help="Output file", required=False)
    parser.add_argument('-k', '--keyword', help="keyword to fuzz",required=False)
    parser.add_argument('-depth', '--depth', help= "depth of the recursivity", required=False)
    parser.add_argument('-e', '--extension', help= "specify extension", required=False)
    parser.add_argument('-vhost', '--vhost', help="Fuzz virtual hosts", required=False, action='store_true')
    parser.add_argument('-domain', '--domain', help="IP to Fuzz virtual hosts", required=False)
    parser.add_argument('-fs', '--filter-size', help="remove response size value", required=False, type=int)
    args = parser.parse_args()

    dir_search = DirSearch(args)
    dir_search.run()