function searchBarUpdate(event, listOfChoices, popup, onSuccessEnter, searchType="B"){
    let key = event.key
    let name = searchbar.value
    if (key == "Enter"){
        console.log("Searching")
        // Go through the list until you find a champion that contains the characters of "name" in order.
        if (searchType === "B" || searchType === "S"){
            for (let i = 0; i < listOfChoices.length; i++){
                let champ = listOfChoices[i]
                if (substringSearch(name.toLowerCase(), champ.toLowerCase())){
                    // CHANGE SITE.
                    onSuccessEnter(champ)
                    break
                }
            }
        }

        // Use substring search first, then order earch
        if (searchType === "B" || searchType === "O"){
            for (let i = 0; i < listOfChoices.length; i++){
                let champ = listOfChoices[i]
                if (orderSearch(name.toLowerCase(), champ.toLowerCase())){
                    // CHANGE SITE.
                    onSuccessEnter(champ)
                    break
                }
            }
        }
    }
    else{
        let contents = new Set([])
        for (let i = 0; i < listOfChoices.length; i++){
            let champ = listOfChoices[i]
            if (substringSearch(name.toLowerCase(), champ.toLowerCase())){
                contents.add(champ)
            }
        }
        
        // TODO: maybe get rid of this, could be slow.
        for (let i = 0; i < listOfChoices.length; i++){
            let champ = listOfChoices[i]
            if (orderSearch(name.toLowerCase(), champ.toLowerCase()) && !(champ in contents)){
                contents.add(champ)
            }
        }
        // Display popup menu for contents
        // TODO:
        // Idk if i like all of this. Just feels bloated. Maybe go back to list if you want to increase performance.
        popup.innerHTML = Array.from(contents)
    }
}

function isValidSearch(currentSearch, champion){
    // I havnt decided which one i want.
    return substringSearch(currentSearch,champion)
}

function orderSearch(currentSearch, champion){
    var indexInSearch = 0
    var indexInChampion = 0
    while (indexInSearch < currentSearch.length && indexInChampion < champion.length){
        if (currentSearch[indexInSearch] == champion[indexInChampion]){
            indexInSearch += 1
        }
        indexInChampion += 1
    }

    return indexInSearch == currentSearch.length
}

function substringSearch(currentSearch, champion){
    // Checks if currentSearch is a substring of champion.
    var indexInSearch = 0
    var indexInChampion = 0
    while (indexInChampion < champion.length && currentSearch[0] !== champion[indexInChampion]){
        indexInChampion += 1
    }

    while (currentSearch[0] === champion[indexInChampion]){
        let ts = indexInSearch
        let tc = indexInChampion

        while (indexInSearch < currentSearch.length && indexInChampion < champion.length){
            if (currentSearch[indexInSearch] == champion[indexInChampion]){
                indexInSearch += 1
                indexInChampion += 1
            }
            else{
                break
            }
        }
        if (indexInSearch == currentSearch.length){
            return true
        } else{
            indexInSearch = ts
            indexInChampion = tc + 1
        }
    }
    
    return indexInSearch == currentSearch.length
}
