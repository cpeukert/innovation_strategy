****************************************
** Case study: Boombox music platform **
****************************************
** Strategy of Innovation
** Christian Peukert
****************************************


cls
cd "/Users/cpeukert/Dropbox/Teaching/UNIL/Master/Fall 2023/SOI/Slides/Week 8"
use boombox.dta,clear


browse month country n_artist n_curator

codebook country


// plot growth on both market sides

preserve

	collapse (sum) n_artist n_curator, by(month)
	twoway (line n_artist month) (line n_curator month), name(n, replace)
	twoway (line n_artist month) (line n_curator month, yaxis(2)), name(n2,replace)

restore

// plot installed base on both market sides


preserve
	drop if month==tm(2022m06)
	collapse (sum) cum_artist1 cum_curator1, by(month)
	twoway (line cum_artist1 month) (line cum_curator1 month), name(cum, replace)
	twoway (line cum_artist1 month) (line cum_curator1 month, yaxis(2))	, name(cum2, replace)

restore

// estimate direct network effects

reg n_artist n_artist1
reg n_curator n_curator1

// test for hump shape

gen n_artist12=n_artist1^2
gen n_curator12=n_curator1^2

reg n_artist n_artist1 n_artist12
reg n_curator n_curator1 n_curator12

twoway (function y=0.89*x-0.00005*x^2, range(0 10000))

// estimate direct and indirect network effects

reg n_artist n_artist1 cum_curator1
reg n_curator n_curator1 cum_artist1

// use logarithm to get a nicer interpretation

reg log_n_artist c.log_n_artist1 log_cum_curator1
reg log_n_curator c.log_n_curator1 log_cum_artist1


// use fixed effects for country and month

reghdfe log_n_artist c.log_n_artist1 log_cum_curator1,absorb(country month)
reghdfe log_n_curator c.log_n_curator1 log_cum_artist1,absorb(country month)


/*
// pro stuff: standardize variables to make the coefficients comparable

foreach var in n_artist n_artist1 cum_curator1 n_curator n_curator1 cum_artist1 {
	egen s_`var'=std(`var')
}

reghdfe s_n_artist s_n_artist1 s_cum_curator1,absorb(country month)
reghdfe s_n_curator s_n_curator1 s_cum_artist1,absorb(country month)
*/

// plot predicted values

reghdfe log_n_artist c.log_n_artist1 log_cum_curator1,absorb(country month)

preserve
	predict yhat,xb
	collapse (mean) log_n_artist1 yhat*,by(month)
	twoway (line log_n_artist1 month) (line yhat month) // not perfect: we're underestimating the beginning, but overestimating in the end
restore

// run counterfactual simulations: what would have happened in the absence of paid/earned/owned media
 
reghdfe log_n_curator log_n_curator1 log_cum_artist1,absorb(country month)
predict yhat,xb
foreach media in paid earned owned {
	ren log_cum_artist1 temp1
	ren log_cum_artist_no`media'1 log_cum_artist1
	ren log_n_curator1 temp2
	ren log_n_curator_no`media'1 log_n_curator1
	predict yhat_no`media',xb
	ren log_cum_artist1 log_cum_artist_no`media'1
	ren temp1 log_cum_artist1
	ren log_n_curator1 log_n_curator_no`media'1
	ren temp2 log_n_curator1	
}

preserve
	collapse (mean) yhat*,by(month)
	foreach var in yhat yhat_nopaid yhat_noowned yhat_noearned {
		replace `var'=exp(`var')		
	}
	twoway ///
	(line yhat month, lcolor(black) lpattern(solid)) /// 
	(line yhat_nopaid month, lcolor(black) lpattern(dash)) /// 
	(connected yhat_noowned month, lcolor(black) lpattern(dash) msymbol(x) mcolor(black)) ///
	(connected yhat_noearned month,  lcolor(black) lpattern(solid) msymbol(x) mcolor(black)) ///
	if month>=tm(2020m6) ///
	, legend(order (1 "actual" 2 "w/o paid media" 3 "w/o earned media" 4 "w/o owned media" )) ///
	scheme(s1color) ylabel(,grid) xlabel(,grid) xtitle("") ytitle("average monthly curator growth per country") ///
	name(counterfactuals_curators,replace)
restore

drop yhat*

reghdfe log_n_artist log_n_artist1 log_cum_curator1,absorb(country month)
predict yhat,xb
foreach media in paid earned owned {
	ren log_cum_curator1 temp
	ren log_cum_curator_no`media'1 log_cum_curator1
	ren log_n_artist1 temp2
	ren log_n_artist_no`media'1 log_n_artist1	
	predict yhat_no`media',xb
	ren log_cum_curator1 log_cum_curator_no`media'1
	ren temp log_cum_curator1
	ren log_n_artist1 log_n_artist_no`media'1
	ren temp2 log_n_artist1		
}

preserve
	collapse (mean) yhat*,by(month)
	foreach var in yhat yhat_nopaid yhat_noowned yhat_noearned {
		replace `var'=exp(`var')		
	}
	twoway ///
	(line yhat month, lcolor(black) lpattern(solid)) /// 
	(line yhat_nopaid month, lcolor(black) lpattern(dash)) /// 
	(connected yhat_noowned month, lcolor(black) lpattern(dash) msymbol(x) mcolor(black)) ///
	(connected yhat_noearned month,  lcolor(black) lpattern(solid) msymbol(x) mcolor(black)) ///
	if month>=tm(2020m6) ///
	, legend(order (1 "actual" 2 "w/o paid media" 3 "w/o earned media" 4 "w/o owned media" )) ///
	scheme(s1color) ylabel(,grid) xlabel(,grid) xtitle("") ytitle("average monthly artist growth per country") ///
	name(counterfactuals_artist,replace)
restore
