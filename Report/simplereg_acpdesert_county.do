**ACP Desert County level**
**generate demographic proportions**
gen p_black= black/ totalpopulation
gen p_hispanic=hispanic/ totalpopulation
gen p_native= americanindianandalaskanative/ totalpopulation
gen bachelormore= bachelorsdegree+ mastersdegree+ doctoratedegree
gen p_bachelormore= bachelormore/ totalover25yearsold
gen p_renter= renteroccupied/ totalhousingunits
gen p_children= householdswithonemoremorepeopleu/ totalhouseholds
gen p_noncitizen= notauscitizen/ totalpopulation
gen totalenglishless= speakenglishlessthanverywellspan+ speakenglishlessthanverywellothe
gen p_englishlesswell= totalenglishless/ totalover5yearsold
gen totalpoverty= under50ofpovertylevel+ to99ofpovertylevel
gen p_poverty= totalpoverty/ totalpopulation
gen p_white= white/ totalpopulation

**generate outcome broadband + PC**
gen p_bbPC=computerandbroadbandinternetsubs/totalhouseholds

gen totalHHbelow35K= lessthan10000householdincome+ v33+ v35
gen totalHHbelow35KBB= lessthan10000householdincomewith+ v34+ v36
gen p_totalhhbelow35Kbb= totalHHbelow35KBB/ totalHHbelow35K

gen totalHHbelow50K= lessthan10000householdincome+ v33+ v35 +v37
gen totalHHbelow50KBB= lessthan10000householdincomewith+ v34+ v36 + v38
gen p_totalhhbelow50Kbb= totalHHbelow50KBB/ totalHHbelow50K

**generate underserved flags**
gen lowincome50K_flag=.
replace lowincome50K_flag=1 if medianhouseholdincome<50000 & medianhouseholdincome!=.
replace lowincome50K_flag=0 if medianhouseholdincome>=50000 & medianhouseholdincome!=.

gen lowincome35K_flag=.
replace lowincome35K_flag=1 if medianhouseholdincome<35000 & medianhouseholdincome!=.
replace lowincome35K_flag=0 if medianhouseholdincome>=35000 & medianhouseholdincome!=.

gen served51=1
replace served51=0 if servedpercentage<0.51

**demographic characterstics**
mean p_poverty if lowincome50K_flag==1 & servedpercentage<.51 [w=totalhouseholds]
mean p_poverty if lowincome50K_flag==0 | servedpercentage>=.51 [w=totalhouseholds]
mean p_black if lowincome50K_flag==1 & servedpercentage<.51 [w=totalpopulation]
mean p_black if lowincome50K_flag==0 | servedpercentage>=.51 [w=totalpopulation]
mean p_native if lowincome50K_flag==1 & servedpercentage<.51 [w=totalpopulation]
mean p_native if lowincome50K_flag==0 | servedpercentage>=.51 [w=totalpopulation]

**broadband/acp uptake**
mean p_acpuptake if lowincome50K_flag==1 & servedpercentage<.51 [w=totalhouseholds]
mean p_acpuptake if lowincome50K_flag==1 & servedpercentage>=.51 [w=totalhouseholds]

mean p_bbPC if lowincome50K_flag==1 & servedpercentage<.51 [w=totalhouseholds]
mean p_bbPC if lowincome50K_flag==1 & servedpercentage>=.51 [w=totalhouseholds]

mean p_totalhhbelow35Kbb if lowincome50K_flag==1 & servedpercentage<.51 [w=totalhouseholds]
mean p_totalhhbelow35Kbb if lowincome50K_flag==1 & servedpercentage>=.51 [w=totalhouseholds]


**simple regression only lowincome areas**
qui reg p_bbPC i.served51 medianhouseholdincome pop_density i.rural ispscount i.tribal p_white p_bachelormore p_children p_poverty medianage if medianhouseholdincome<50000 [w=totalhouseholds], vce (robust)
outreg2 using acpdesert, word ctitle("Broadband (any) + PC (<50K areas)") addnote("Note: robust standard errors") replace

qui reg p_bbPC i.served51 medianhouseholdincome pop_density i.rural ispscount i.tribal p_white p_bachelormore p_children p_poverty medianage if medianhouseholdincome<45000 [w=totalhouseholds], vce (robust)
outreg2 using acpdesert, word ctitle("Broadband (any) + PC (<45K areas)") addnote("Note: robust standard errors") append

qui reg p_bbPC i.served51 medianhouseholdincome pop_density i.rural ispscount i.tribal p_white p_bachelormore p_children p_poverty medianage if medianhouseholdincome<55000 [w=totalhouseholds], vce (robust)
outreg2 using acpdesert, word ctitle("Broadband (any) + PC (<55K areas)") addnote("Note: robust standard errors") append

**simple regression for all counties but limited to lowincome HHs**
qui reg p_totalhhbelow35Kbb i.served51 medianhouseholdincome pop_density i.rural ispscount i.tribal p_white p_bachelormore p_children p_poverty medianage [w=totalhouseholds], vce (robust)
outreg2 using acpdesert2, word ctitle("Broadband (any) <35K HHs") addnote("Note: robust standard errors") replace

qui reg p_totalhhbelow50Kbb i.served51 medianhouseholdincome pop_density i.rural ispscount i.tribal p_white p_bachelormore p_children p_poverty medianage [w=totalhouseholds], vce (robust)
outreg2 using acpdesert2, word ctitle("Broadband (any) <50K HHs") addnote("Note: robust standard errors") append



