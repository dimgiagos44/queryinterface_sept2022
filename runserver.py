import subprocess

from queryinterface_v5 import app

from graphbuilder.graphbuilder import extractor

if __name__ == '__main__':
    print("Initializing information extractor...")
    parserproc = subprocess.Popen('java -Xmx8G -cp "parser/*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 10000 -timeout 3000',
                                  stdout=subprocess.DEVNULL)#,stderr=subprocess.DEVNULL)
    try:
        extractor.extract("This is a test.")
        app.run('localhost',5555)
    finally:
        parserproc.kill()
