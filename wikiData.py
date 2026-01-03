import requests
import json
from pprint import pprint as pp
from bs4 import BeautifulSoup
import re

# A lot may break if lolwiki changes.
# Each line that may break has been commented with # BREAK
# Each line which is ONLY used for debugging has been commented with # DEBUG
class wikiGetData:
    def __init__(self):
        print("Init GetData") # DEBUG
        self._listofChampsFilePath = r"C:\Code\AbilityHaste\wikiListofChamps.txt"
        self._baseStatsPath = r"C:\Code\AbilityHaste\baseStats.txt"
        self.__urlToChampion = r"https://wiki.leagueoflegends.com/en-us/"
        self.__urlToBaseStats = r"https://wiki.leagueoflegends.com/en-us/List_of_champions/Base_statistics"

    # Updates file at self._champsFilePath with the list of champs on lolwiki.
    def __updateChampsFile(self): 
        champions = [] # List instead of a set because I want alphabetical order and idc about added 0.2 seconds for something that will run one time per 14 days.

        r = requests.get("https://wiki.leagueoflegends.com/en-us/List_of_champions") # BREAK 
        # FIX should maybe throw a clear error if this doesn't give a 200.
        r = str(r.content)

        for champ in r.split('data-champion="')[1:]: # First part of the split is the only one that doesn't start with a champ name. A | B | B .split("|")
            # champ = "{championName}"randomhtmlNonsense....
            finchamp = ""
            for ch in champ:
                if (ch != '"'):
                    finchamp += ch
                else:
                    break
            finchamp = finchamp.replace("&#39;", "'").replace(" ", "_") # HTML encoding of ' is &#39;  AND replace space with _ for urls.
            if (not (finchamp in champions)):
                champions.append(finchamp)
        
        toWrite = ""
        for champ in champions:
            toWrite += champ + "\n"
        toWrite = toWrite[:-1] # del last \n
        
        with open(self._listofChampsFilePath, "w") as f:
            f.write(toWrite)

    def __updateBaseStats(self): # Update self._baseStatsPath file
        r = str(requests.get(self.__urlToBaseStats).content)
        champs = r.split("<tbody>")[1].split("</tbody>")[0].split("<tr>")[2:] # 2: To skip the empty and the trhead  # BREAK
        edgeCaseNames = ["Kled", "Mega_Gnar"] # BREAK Edge cases are the transformations of champs that can transform. mega gnar, kled (not kled & skaarl)
        edgeCaseStats = ""
        finToWrite = ""

        for champ in champs:
            # I belive with my full mind body and soul that the champs are always sorted alphabetically lexicographically
            # But I still need to get the names or edgecases
            # Getting the name:
            name = ""
            for ch in champ.split('data-sort-value="')[1]:
                if ch != '"':
                    name += ch
                else:
                    break
            name = name.replace(" ", "_").replace("&#39;", "'")  # DO NOT USE THIS NAME VALUE ELSEWHERE OTHER THAN IN EDGECASES. THEY ARE DIFFERENT TO listofChamps.txt

            # Getting the stats:
            indvStats = "" # indvStats = name + "," if you wanna store the name as well, but read comment above.
            for stat in champ.split("<td>")[1:]: # BREAK
                res = ""
                for ch in stat:
                    if ch.isnumeric() or ch == ".":
                        res += ch
                indvStats += res + ","

            indvStats = indvStats[:-1]
            if name in edgeCaseNames:
                edgeCaseStats += indvStats + "\n"
            else:    
                finToWrite += indvStats + "\n"
        
        edgeCaseStats = edgeCaseStats[:-1]
        finToWrite += edgeCaseStats

        print(finToWrite) # DEBUG

        with open(self._baseStatsPath, "w") as f: # 170 champs + edge cases stored at the end.
            f.write(finToWrite)

    def __updateAbilities(self, champion: str):
        # For a given champion this function appropriately classifies all of its abilities.

        #
        r = requests.get(self.__urlToChampion + champion)
        with open(self._indvChampPath + champion, "w"):
            pass

    def updateAll(self):
        self.__updateChampsFile()
        self.__updateBaseStats()
        pass

    def getCDNotes(self,champ):
        print(repr(champ))
        print(f"https://wiki.leagueoflegends.com/en-us/{champ}")

        html = requests.get(rf"https://wiki.leagueoflegends.com/en-us/{champ}").content
        soup = BeautifulSoup(html, "html.parser")
        a = soup.get_text().split("edit source")
        abilityContent = a[1]
        regex = re.compile(r"[^.?!\n]*cooldown[^.?!\n]*\.")
        cdSentences = re.findall(regex,abilityContent)
        
        return cdSentences
    
    # Cassiopeia, Ekko
    def getAllCDNotes(self):
        notes = {}
        with open(r"C:\Code\AbilityHaste\wikiListofChamps.txt", "r") as f:
            for champ in f.readlines():
                c = champ.strip("\n")
                try:
                    notes[c] = self.getCDNotes(c)
                except:
                    input(c)

        print(notes)
        for champNote in notes.values():
            print(champNote)
            print()
        self.toJSONfile(notes,"C:\Code\AbilityHaste\cdNotes.txt")
        return notes
    
    def toJSONfile(self, content, filepath):
        if input(f"Write to file {filepath}? Y/N").lower() == "n":
            return
        
        with open(filepath, "w") as f:
            f.write(json.dumps(content))



class Calculations:
    def __init__(self):
        pass

    def AAOnly(self, champion: str, level: int, items: list[str]):
        pass

    def abilitiesOnly(self, champion: str, level: int, items: list[str], abilityOrder=[0,1,2,3]):
        # Asymptotic DPS, potentially with a combo order provided.
        pass

    def realDamage(self, champion: str, level: int, items: list[str], abilityOrder=[0,1,2,3]):
        # Hard to do, but give spells the highest priority, casting autos while possible.
        # Returns asymptotic DPS.
        # Auto is the lowest priority ability.
        pass


bob = wikiGetData()
bob.getAllCDNotes()