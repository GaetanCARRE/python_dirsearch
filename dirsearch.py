import sys
import requests as re
import argparse
import threading
def main():
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
    # search(sys.argv[1], sys.argv[2])
    parser = parsing()
    # get wordlist in list
    wordlist = []
    with open(parser.wordlist, "r") as f:
        for line in f:
            wordlist.append(line.strip())
    
    # split wordlist to parser.threads part
    thread_num = int(parser.threads)
    wordlist = [wordlist[i::thread_num] for i in range(thread_num)] 
    for i in range(thread_num):
        t = threading.Thread(target=search, args=(parser.url, wordlist[i], parser.recursive))
        print("Thread " + str(i) + " started")
        t.start()
        

def search(url, wordlist, r = False):
        for line in wordlist:
            response = re.get(url + "/" + line.strip())
            if response.status_code != 404:
                print("Found: " + url + "/" + line.strip() + " " + str(response.status_code))
                if r:
                    search(url + "/" + line.strip(), wordlist)
                    
            else:
                pass
                # print("Not Found: " + url + "/" + line.strip())



def parsing():
    parser = argparse.ArgumentParser(description="Dirsearch")
    parser.add_argument('-u', '--url', help="URL to search", required=True)
    parser.add_argument('-w', '--wordlist', help="URL to search", required=True)
    parser.add_argument('-r', '--recursive', action='store_true', required=False)
    parser.add_argument('-t', '--threads', help="Number of threads", required=False, default=10)
    return parser.parse_args()


if __name__ == "__main__":
    main()