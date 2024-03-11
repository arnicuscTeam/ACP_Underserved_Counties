**ACP deserts DiD estimations County level**
**generate variables**
gen served51=0
replace served51=1 if calculatedpercentageofunitsforbr>=.51
gen served51_post22=0
replace served51_post22=1 if served51==1 & year==2022

gen cohort2=0
replace cohort2=2022 if served51==1


**code to generate figure 2**
**calculate means for each group/year**
mean p_hh_broadband_pc if medianhouseholdincome22<50000 & served51==1, over(year)
mean p_hh_broadband_pc if medianhouseholdincome22<50000 & served51==0, over(year)

**input results and generate graph**
input int year byte(time treatment) float percentage
2016	0	0	0.6152024
2017	0	0	0.6358661
2018	0	0	0.6725636
2019	0	0	0.6845734
2021	0	0	0.768127
2022	1	0	0.7834498
2016	0	0	0.6743293
2017	0	0	0.7017867
2018	0	0	0.7255825
2019	0	0	0.7462603
2021	0	0	0.7974067
2022	1	1	0.8229107
end

gen id = ceil(_n / 6)
separate percentage, by(id)
gen counterfactual = percentage if id == 2 & year == 2021
replace counterfactual = 0.7974067 + (0.7834498 - 0.768127) if id == 2 & year == 2022
line percentage? counterfactual year, xlabel(2016 2017 2018 2019 2021 2022) lpattern(solid solid dash) xline(2021)

**double difference model for table 3 and appendix B**
csdid p_hh_broadband_pc estimatemedianhouseholdincomeint totalpop p_bachmore estimatemedianagetotal if medianhouseholdincome22<50000, time(year) gvar(cohort2) method(dripw ) wboot
estat simple
estat event, level(90)
csdid_plot


***Triple difference estimator (table 3)***
reghdfe p_hh_broadband_pc i.post2022##c.served_fixed_bb##i.lowincome50k estimatemedianhouseholdincomeint totalpop p_bachmore estimatemedianagetotal, a(county year) vce(cluster county)
outreg2 using tripledid, word ctitle("Broadband (any) + PC 50K") addnote("Note: robust standard errors") replace




