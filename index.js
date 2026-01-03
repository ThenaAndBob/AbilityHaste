// index.js
const express = require('express');
const app = express();
const port = 3000;

const API_KEY = "RGAPI-3dd64ee1-c71f-4e69-8b95-77ee07666a8c"
const euBase = String.raw`https://europe.api.riotgames.com`
const euw1Base = String.raw`https://euw1.api.riotgames.com`

const getpuuidEndpoint = String.raw`/riot/account/v1/accounts/by-riot-id/`
const getLiveGame = String.raw`/lol/spectator/v5/active-games/by-summoner/`
// https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/C0mpl3x/EUW


async function getPUUID(name,tag){
  let resp = await fetch(euBase + getpuuidEndpoint + name + "/" + tag, {
    headers: {
      "X-Riot-Token": API_KEY
    }
  })
  
  return resp.body["puuid"]
}

async function getGame(puuid){ // Returns list of [blue],[red]
  let champs = [[],[]]
  let mapToTeam = new Map([[100, 0], [200, 1]])

  let JSONresponse = await fetch(euw1Base + getLiveGame + puuid, {
    headers: {
      "X-Riot-Token": API_KEY
    }
  })

  JSONresponse.body["participants"].forEach(element => { // Fills champs array with champion ids.
    champs[mapToTeam.get(element["teamId"])].push(element["championId"])
  });

  return champs
}


app.get('/', (req, res) => {
  res.sendFile('index.html', {root: __dirname})
});

app.get("/livegame", (req, res) => {
  let body = JSON.parse(req.body) // not sure if this works.
  let name = body["name"]
  let tag = body["tag"]

  
  res.send({})

})

app.get('/:any', (req, res) => {
  const fileName = req.params.any; 
  res.sendFile(fileName, { root: __dirname });
});


app.listen(port, () => {
  console.log(`Example app listening at http://localhost:${port}`);
});