import requests
import json

class getData:
    def __init__(self,patch,apiType="C",download=True):
        self.__patch = patch
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

    def __request(self,champion="",rType="json"): # Array[String] of champion names.
        if rType != "json" and rType != "raw":
            raise ValueError("rType must be json or raw")
        
        filepath = ""
        if self.__apiType == "C":
            filepath = f"C:\Code\AbilityHaste\cdragon\#{champion}"
        else:
            filepath = f"C:\Code\AbilityHaste\ddragon\#{champion}"

        if self.__download:
            url = ""
            if champion == "":
                url = self.__getChampsListUrl()         
            else:
                url = self.__getChampsCooldownURL(champion)
            
            response = requests.get(url)
            print(url + " : " + str(response) + "\n") # DEBUG
            data = json.loads(response.content)
            with open(filepath,"wb") as f:
                f.write(response.content)
        else:
            with open(filepath,"rb") as f:
                data = json.loads(f.read())


        if rType == "json":
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
    
    def getChampsList(self): # TO BE CALLED ONCE PER PATCH.
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
        self.__apiType = "D" # USE API D BECAUSE WE NEEEEEEEEEEEEEEEEED the names in the mapping to agree with the D api.

        if self.__download:
            myMap = {}
            champions = self.getChampsList()

            for champ in champions:
                data = self.__request(champ)["data"][champ]

                myMap[f"{data['id']}"] = f"{data['key']}"
                myMap[f"{data['key']}"] = f"{data['id']}"


            self.toJSONfile(self,myMap,"C:\Code\AbilityHaste\Map.json")
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

print("main.py running -doing nothing")

