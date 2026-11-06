person
    recordInfo [MANDATORY] 
        validationType{diva-person} [MANDATORY]  ✅
        dataDivider{divaData} [MANDATORY] 
        inTrashBin ✅
        oldId ✅
        updated
            updatedBy
            tsUpdated
    authority [MANDATORY] ✅
        nametype:{personal} [MANDATORY] ✅
            namePart type:{given} ✅
            namePart type:{family} [MANDATORY] ✅
            namePart type:{termsOfAddress} ✅
            namePart type:{date} ✅
    variant [REPEATING] ✅
        nametype:{personal} [MANDATORY]  ✅
            namePart type:{given} ✅
            namePart type:{family} [MANDATORY] ✅
    email [REPEATING] ✅
    location [REPEATING] ✅
        url [MANDATORY] ✅
        displayLabel ✅
    note type:{biographical}, attr=lang [REPEATING] ✅
    localId [REPEATING]
        nameIdentifier type:{localId} [MANDATORY] 
        permissionUnit [MANDATORY] 
    nameIdentifier type:{orcid} [REPEATING] ✅
    nameIdentifier type:{se-libr} [REPEATING] ✅
    nameIdentifier type:{openAlex} [REPEATING] ✅
    nameIdentifier type:{scopus} [REPEATING] ✅
    nameIdentifier type:{wos} [REPEATING] ✅
    nameIdentifier type:{googleScholar} [REPEATING] ✅
    nameIdentifier type:{viaf} [REPEATING] ✅
    affiliation [REPEATING]
        organisation, ✅
        namePart ✅
        identifier type:{ror}
        country
        description
        startDate, ✅
            year [MANDATORY] ✅
            month
            day
        endDate,
            year [MANDATORY]
            month
            day