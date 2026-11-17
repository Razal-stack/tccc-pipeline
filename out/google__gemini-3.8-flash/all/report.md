# google/gemini-3.8-flash on all (50 cards)

Cards scored: 50 (50 with predictions)

F1 on filled fields:      94.0%  (precision 95.9%, recall 92.2%)
Safety-critical fields:   96.1%  (precision 97.1%, recall 95.2%)
Invented values:          7 total, 0.14 per card
Injury boxes F1:          89.0%
Naive field accuracy:     98.7%  (an empty card scores 84.5%)

| Group | F1 | Precision | Recall | Correct | Wrong | Invented | Missed |
|---|---|---|---|---|---|---|---|
| identity | 89.5% | 93.0% | 86.3% | 265 | 20 | 0 | 22 |
| mechanism | 94.0% | 95.9% | 92.2% | 47 | 0 | 2 | 4 |
| tourniquets | 94.0% | 94.8% | 93.2% | 55 | 3 | 0 | 1 |
| treatments | 94.0% | 96.9% | 91.3% | 63 | 1 | 1 | 5 |
| vital_signs | 95.9% | 97.5% | 94.4% | 354 | 9 | 0 | 12 |
| medications | 96.5% | 96.2% | 96.8% | 150 | 2 | 4 | 3 |
| evac | 98.9% | 100.0% | 97.8% | 45 | 0 | 0 | 1 |

## Where the errors come from

- transcription: 47
- extraction: 36
- invented: 7

## Errors by group and stage

- identity / transcription: 24
- identity / extraction: 18
- vital_signs / transcription: 14
- vital_signs / extraction: 7
- treatments / extraction: 5
- mechanism / extraction: 4
- tourniquets / transcription: 4
- medications / transcription: 4
- medications / invented: 4
- mechanism / invented: 2
- medications / extraction: 1
- evac / extraction: 1
- treatments / transcription: 1
- treatments / invented: 1

## Every error

| file | field | stage | predicted | truth |
|---|---|---|---|---|
| aim | name | extraction | Carr, Jas | Kaur, Jas |
| aim | mechanism_gsw | extraction | False | True |
| ato | tq_right_leg_time | transcription |  | 1012 |
| ato | breathing_chest_seal | extraction | False | True |
| bwt | last4 | transcription |  | 5033 |
| cjp | battle_roster | transcription | VA62119 | VA6119 |
| dgf | signs_2_avpu | extraction |  | A - Alert |
| fox | battle_roster | transcription | RE88206 | RE8826 |
| ihg | tq_right_leg_time | transcription | 1425 | 1424 |
| ihg | tq_left_leg_time | transcription | 1420 | 1422 |
| ihg | signs_1_pulse | transcription | 108 radial | 128 radial |
| ihg | analgesic_1_time | extraction | 1432 | 1430 |
| ihg | first_responder_name | extraction | Jones | Jones, Sam |
| ihg | first_responder_last4 | transcription | 3319 | 3318 |
| inj | time | transcription | 2050 | 2015 |
| inj | first_responder_name | extraction | Quinn, Joe | Quinn, Jo |
| jql | first_responder_last4 | transcription |  | 2285 |
| jso | last4 | transcription |  | 4062 |
| jso | splint | extraction | False | True |
| jso | first_responder_name | extraction | Dunn | Dunn, Ross |
| kdb | evac_priority | extraction | False | True |
| kdb | name | transcription |  | Reid, Fiona |
| kdb | last4 | transcription |  | 6363 |
| kdb | gender_f | extraction | False | True |
| kdb | time | extraction |  | 0405 |
| kdb | service | transcription |  | Army |
| kdb | unit | transcription |  | 29 Commando Royal Artillery |
| kdb | mechanism_artillery | extraction | False | True |
| kdb | signs_1_time | transcription |  | 0420 |
| kdb | signs_1_pulse | transcription |  | 108 radial |
| kdb | signs_1_bp_systolic | transcription |  | 112 |
| kdb | signs_1_bp_diastolic | transcription |  | 70 |
| kdb | signs_1_resp_rate | extraction |  | 22 |
| kdb | signs_1_avpu | transcription |  | A - Alert |
| kdb | signs_1_pain | extraction |  | 6 Intense |
| kdb | dressing_hemostatic | extraction | False | True |
| kdb | dressing_pressure | extraction | False | True |
| liq | time | transcription | 1110 | 1100 |
| liq | first_responder_name | extraction | Rhys, Owen | Reece, Owen |
| lrh | date | transcription |  | 01-NOV-26 |
| mbs | signs_2_time | transcription | 0450 | 0415 |
| mbs | signs_2_pulse | transcription | 160 radial | 116 radial |
| mbs | blood_1_route | transcription |  | IV |
| nwd | time | transcription |  | 1500 |
| oeu | time | transcription |  | 1910 |
| oeu | unit | extraction |  | Signals det |
| oeu | mechanism_burn | invented | True | False |
| oeu | signs_1_avpu | transcription | A - Alert | V - Verbal |
| oeu | dressing_type | transcription | clingfilm | cling film |
| onh | unit | extraction | Royal Army detachment | REME detachment |
| onh | signs_1_avpu | extraction |  | A - Alert |
| oog | date | transcription |  | 04-NOV-26 |
| oog | signs_2_time | transcription | 0915 | 0920 |
| pbj | other_med_1_dose | transcription |  | 1 g |
| pbj | other_med_2_dose | transcription |  | 1 g |
| pma | time | transcription | 1305 | 1306 |
| qof | first_responder_name | extraction | Hogan | Hogan, Ciara |
| riq | last4 | transcription |  | 5290 |
| riq | gender_m | extraction | False | True |
| riq | time | transcription |  | 2100 |
| riq | signs_1_spo2 | transcription | 94 | 95 |
| riq | signs_1_avpu | extraction |  | A - Alert |
| riq | first_responder_name | extraction | Weed, Cal | Reid, Cal |
| roo | dressing_pressure | invented | True | False |
| roo | other_med_1_name | invented | TXA |  |
| roo | other_med_1_dose | invented | 2 g |  |
| roo | other_med_1_route | invented | IV |  |
| roo | other_med_1_time | invented | 1058 |  |
| rtw | signs_1_time | transcription |  | 1500 |
| uij | mechanism_mvc | extraction | False | True |
| vbf | gender_m | extraction | False | True |
| vdi | time | transcription |  | 0715 |
| vdi | mechanism_ied | extraction | False | True |
| vdi | tq_left_leg_time | transcription | 1715 | 0718 |
| vdi | signs_1_pulse | transcription |  | 130 |
| xbf | last4 | transcription |  | 3620 |
| xbf | date | transcription | 31-OCT-26 | 30-OCT-26 |
| xqh | name | extraction | Murphy, Aoi | Murphy, Aoife |
| xqh | signs_1_bp_diastolic | transcription | 74 | 76 |
| xqh | first_responder_name | extraction | Ahmed, Zayn | Ahmed, Zain |
| xqu | signs_1_pulse | extraction | 104 | 104 radial |
| xqu | combat_pill_pack | extraction | False | True |
| xqu | first_responder_name | extraction | Guru, Raj | Gurung, Raj |
| xqu | first_responder_last4 | transcription |  | 9501 |
| xts | signs_1_resp_rate | extraction | 18 | 16 |
| xvw | last4 | transcription |  | 7007 |
| ynt | battle_roster | extraction | SP22214 | SP2214 |
| ynt | mechanism_burn | invented | True | False |
| ynt | first_responder_name | extraction | Day | Day, Finn |
| zas | other_med_1_time | transcription | 0750 | 0755 |
