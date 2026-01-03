const fs = require('node:fs');
const { format, parse } = require('lua-json')

const readFile = "items.lua"
const writeFile = "allItems.txt"

fs.readFile(readFile, "utf8", (err, data) => {
    let json = parse(data)
    let toWrite = ""
    for (const key in json){
        toWrite += `, "${key}"`
    }
    toWrite = `[${toWrite.slice(2)}]`
    fs.writeFile(writeFile, toWrite, "utf8", (err) => {})
})