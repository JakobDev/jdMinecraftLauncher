import os

class TranslationHelper():
    def __init__(self, language):
        self.strings = {}
        currentDir = os.path.dirname(os.path.realpath(__file__))
        langPath = os.path.join(currentDir,"translation","en_GB.lang")
        self.readLanguageFile(langPath)
        langPath = os.path.join(currentDir,"translation",language + ".lang")
        if os.path.isfile(langPath):
            self.readLanguageFile(langPath)

    def readLanguageFile(self, path):
        with open(path,encoding="utf-8") as f:
            content = f.readlines()
            for line in content:
                if line != "\n" and line.find("#") != 0:
                    try:
                        a,b = line.rstrip().split("=")
                        self.strings[a] = b
                    except:
                        print('Error in line "' + line + '"')

    def translate(self, key):
        if key in self.strings:
            return self.strings[key]
        else:
            return key
