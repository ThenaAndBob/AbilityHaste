import requests
import json
import os

class getData:
    SPELLORDER = ["Q", "W", "E", "R"]

    def __init__(self,patch,apiType="C",download=True):
        self.__patch = patch
        self.__version = patch[:-2]
        self.__apiType = apiType
        self.__download = download
        if apiType != "C" and apiType != "D":
            raise ValueError("apiType must be C or D")
        if download:
            if input("ARE YOU SURE YOU WANT TO DO API REQUEST? Y/N").lower() == "n":
                print("YOU SAID NO, so i will change self.__download to False.")
                self.__download == False

    def __getChampsListUrl(self):
        url = ""
        if self.__apiType == "C": 
            url = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champion-summary.json"
        else:
            url = f"https://ddragon.leagueoflegends.com/cdn/{self.__patch}/data/en_US/champion.json" 

        return url

    def __getChampsCooldownURL(self,champ):
        url = ""
        if self.__apiType == "C": 
            url = f"https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champions/{champ}.json"
        else: # D
            url = f"https://ddragon.leagueoflegends.com/cdn/15.24.1/data/en_US/champion/{champ}.json"

        return url

    def __request(self,champion="All",rType="json"): # Array[String] of champion names.
        if rType != "json" and rType != "raw":
            raise ValueError("rType must be json or raw")
        
        filepath = ""
        if self.__apiType == "C":
            filepath = f"C:\Code\AbilityHaste\cdragon\{champion}"
        else:
            filepath = f"C:\Code\AbilityHaste\ddragon\{champion}"

        if self.__download:
            url = ""
            if champion == "All":
                url = self.__getChampsListUrl()         
            else:
                url = self.__getChampsCooldownURL(champion)
            
            response = requests.get(url)
            print(url + " : " + str(response) + "\n") # DEBUG
            print(response.content)
            with open(filepath,"wb") as f:
                f.write(response.content)
        else:
            with open(filepath,"rb") as f:
                data = json.loads(f.read())


        if rType == "json":
            if self.__download:
                return json.loads(response.content)
            else:
                return data
        else:
            return response.content



    def __getChampsListC(self): # Array[Int] of champion ids.
        champions = [] 
        data = self.__request()
        
        for champion in data[1:]:
            champions.append(champion["id"])
        
        return champions

    def __getChampsListD(self):
        champions = []
        data = self.__request()
        
        for champion in data["data"].keys():
            champions.append(champion)
        
        return champions
    
    def getChampsList(self): # TO BE CALLED ONCE PER PATCH. Returns list of strings
        if self.__apiType == "C": 
            return self.__getChampsListC()
        else:
            return self.__getChampsListD()



    def __getChampCooldownsC(self, champion): # given champ id returns cooldowns and ammorechargetime
        cooldowns = [[[],[]] for _ in range(4)] # Array[Array[X]]  list of 4 lists of size 1-6
        data = self.__request(champion)

        for index in range(4):
            cooldowns[index][0] = data["spells"][index]["cooldownCoefficients"]
            cooldowns[index][1] = data["spells"][index]["ammo"]["ammoRechargeTime"]

        return cooldowns
    
    def __getChampCooldownsD(self, champion): # TO BE CALLED ONCE PER PATCH PER CHAMPION.
        cooldowns = [] # Array[Array[X]]  list of 4 lists of size 1-6
        data = self.__request(champion)

        for spell in data["data"][champion]["spells"]:
            cooldowns.append(spell["cooldown"]) # Returns a list (size 1 to 6) (karma,udyr,jayce etc)

        return cooldowns
    
    def getChampCooldowns(self,champ): # TO BE CALLED ONCE PER PATCH.
        if self.__apiType == "C": 
            return self.__getChampCooldownsC(champ)
        else:
            return self.__getChampCooldownsD(champ)



    def getAllCDsList(self): # once per patch
        cds = []
        champions = self.getChampsList()

        for champ in champions:
            cds.append(self.getChampCooldowns(champ))

    def getAllCDsDict(self):
        cds = {}
        champions = self.getChampsList()

        for champ in champions:
            cds[champ] = self.getChampCooldowns(champ)

        return cds
    
    def getIdNameMapping(self):
        temp = self.__apiType
        self.__apiType = "C" # USE API D second BECAUSE WE NEEEEEEEEEEEEEEEEED the names in the mapping to agree with the D api.

        if self.__download:
            myMap = {}
            
            champions = self.getChampsList()
            for champ in champions:
                data = self.__request(champ)

                myMap[f"{data['alias']}"] = f"{data['id']}"
                myMap[f"{data['id']}"] = f"{data['alias']}"


            self.__apiType = "D"
            champions = self.getChampsList()

            for champ in champions:
                data = self.__request(champ)["data"][champ]

                myMap[f"{data['id']}"] = f"{data['key']}"
                myMap[f"{data['key']}"] = f"{data['id']}"


            self.toJSONfile(myMap,"C:\Code\AbilityHaste\Map.json")
        else:
            with open("C:\Code\AbilityHaste\Map.json","r") as f:
                myMap = json.loads(f.read())
        
        self.__apiType = temp

        return myMap
    
    def dataToFile(self): # Should only be called if download is on ig. Its a bit stupid 
        if not self.__download:
            return
        champions = self.getChampsList()
        champions.append("")
        for champ in champions:
            data = self.__request(champ,rType="raw")
            filepath = f"C:\Code\AbilityHaste\datadump\{self.__apiType}F-{champ}"
            with open(filepath,"wb") as f:
                f.write(data)

    def toJSONfile(self, content, filepath):
        if input(f"Write to file {filepath}? Y/N").lower() == "n":
            return
        
        with open(filepath, "w") as f:
            f.write(json.dumps(content))

    def createChampCDFile(self):
        if self.__apiType == "C":
            path = "C:\Code\AbilityHaste\C-CD.json"
        else :
            path = "C:\Code\AbilityHaste\D-CD.json"

        cds = self.getAllCDsDict()
        self.toJSONfile(cds,path)

    def __shorten(self,c,d):
        # c = [[Qcd,Qrecharge], [W,W],[E,E],[R,R]]
        # Make c have similar shape to d
        cnew = [[[],[]] for _ in range(len(d))]

        print(c)
        for i in range(len(d)):
            print(i)
            cnew[i][0] = c[i][0][:len(d[i])]
            cnew[i][1] = c[i][1][:len(d[i])]

        print(cnew)
        return cnew

    def cleanC(self): # Only need to clean C to fix lengths, and also think about recharge times.
        cleanedDict = {}
        myMap = self.getIdNameMapping()

        fC = open("C:\Code\AbilityHaste\C-CD.json", "rb")
        fD = open("C:\Code\AbilityHaste\D-CD.json", "rb")

        Cdict = json.load(fC)
        Ddict = json.load(fD)
        fC.close()
        fD.close()
        
        for key,value in Ddict.items():
            id = myMap[key]
            cleanedDict[id] = self.__shorten(Cdict[id],value)

        self.toJSONfile(cleanedDict,"C:\Code\AbilityHaste\cleanedC-CD.json")

        print(cleanedDict)
        return cleanedDict
    
    def notesC(self):
        pass

    def __localDownload(self, download): 
        
        # Purpose:
        # I want some functions to be allowed to download despite the object self.__download flag. 
        # This parses the download parameter that should be passed to those functions.
        
        # Use:
        # download : String 
        # if download.lower() == "default" (base case), give object flag
        # else convert y/n to true/false respectively.

        download = download.lower()
        if download == "default":
            localDownloadCheck = self.__download
        elif download == "y":
            if input("Are you sure you want to download, Y/N").lower() == "y":
                localDownloadCheck = True
            else: 
                localDownloadCheck = False
        else:
            localDownloadCheck = False
        
        return localDownloadCheck

    def getIconURLs(self, download="default"):
        localDownloadCheck = self.__localDownload(download)

        if not localDownloadCheck:
            raise NotImplementedError
        else:
            if self.__apiType == "C":
                raise NotImplementedError
                # https://raw.communitydragon.org/{version}/game/assets/characters/{champ.lower()}/hud/icons2d/
                champids = self.getChampsList()
                mapping = self.getIdNameMapping()
                
                for id in champids:
                    id = str(id)
                    with open("cdragon/id", "rb") as f:
                        champJSON = json.load(f)


                    for spell in champJSON["spells"]:
                        pass

                    with open(f"cAssets/{id}", "w") as f:
                        toWrite = ""
                        for asset in data:
                            toWrite += imgUrlBase + asset["name"] + "\n"
                        toWrite = toWrite[:-1]
                        f.write(toWrite)
            else:
                imgBase = f"https://ddragon.leagueoflegends.com/cdn/{self.__patch}/img/spell/"
                champNames = self.getChampsList()
                
                for name in champNames:
                    with open(f"ddragon/{name}", "rb") as f:
                        champJSON = json.load(f)

                    with open(f"dAssetsLinks/{name}.txt", "w") as f:
                        toWrite = {}
                        for index, spell in enumerate(champJSON["data"][name]["spells"]):
                            toWrite[index] = imgBase + spell["image"]["full"]
                        f.write(json.dumps(toWrite))

    def getIconPNGs(self,download):
        localDownloadCheck = self.__localDownload(download)

        if not localDownloadCheck:
            raise NotImplementedError
        else:
            if self.__apiType == "D":
                champNames = self.getChampsList()
                for name in champNames:
                    with open(f"dAssetsLinks/{name}.txt", "rb") as f:
                        iconUrls = json.load(f)

                    for spellIndex in range(4):
                        url = iconUrls[str(spellIndex)]
                        with open(f"dAssets/{name}{self.SPELLORDER[spellIndex]}.png", "wb") as f:
                            img = requests.get(url)
                            f.write(img.content)
            else: 
                raise NotImplementedError

# END OF CLASS

def printChampions():
    with open("C:\Code\AbilityHaste\D-CD.json", "rb") as f:
        print(json.load(f).keys())

# ELISE, JAYCE, KARMA, NIDALEE, YUUMI
# Not needed if we just trust D.
def classify(): # I dont like this
    with open("C:\Code\AbilityHaste\D-CD.json", "rb") as f:
        champs = list(json.load(f).keys())
        classify = [[] for _ in range(len(champs))]
        i = 0
        while (True):
            try:
                abilities = input(champs[i])
                if (abilities == ""):
                    classify[i] = [5,5,5,3]
                elif (abilities == "b"):
                    i -= 2
                else:
                    classify[i] = list(map(lambda x: int(x), [abilities[0], abilities[1], abilities[2], abilities[3]]))
            except:
                input("BAD!")
                print(classify)
                break
            
            i += 1
            if i >= len(champs) and abilities == "quit":
                break
    
    with open("C:\Code\AbilityHaste\numSkillPointsAlpha.txt", "w") as f:
        f.write(str(abilities))

    print(abilities)
    return abilities



# READTHIS:
# the reason i wanted to use cdragon is because it also has recharge times.
# i couldnt find them in ddragon. skill issue maybe.

bob = getData("15.24.1","D",download=False)




# TODO: 
# Clean this up a bit. Add some documentation ?

# Create an UPDATE_ALL_CDS, which should be run once per patch.
# Create a UPDATE_ONE_CD(champ) so that if you know all the champs that have been changed, you can limit the number of API calls.
# UPDATE_ONE_CHAMPION_ICON(champ) for VSUs
# A function FIX_CDS to fix certain issues with champs (e.g. veigar)

# 